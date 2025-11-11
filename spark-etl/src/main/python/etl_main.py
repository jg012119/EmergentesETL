"""
Aplicación principal de ETL con Spark
"""
import threading
import time
import os
import tempfile
import platform
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp
import logging
from config import Config
from http_server import start_server, get_events_batch, events_queue
from processors import SoundProcessor, DistanceProcessor, AirProcessor
from sinks import KafkaSink
# from sinks import MySQLSink, MongoDBSink  # Opcional - escritura directa
# from db_writer_client import DBWriterClient  # Deshabilitado - ahora usamos Kafka

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

def create_spark_session() -> SparkSession:
    """Crea una sesión de Spark con conectores para MySQL y MongoDB"""
    # Solución para Windows: configurar HADOOP_HOME y verificar winutils.exe
    if platform.system() == "Windows":
        hadoop_home = os.environ.get("HADOOP_HOME")
        if not hadoop_home:
            # Crear un directorio temporal para HADOOP_HOME
            hadoop_home = os.path.join(tempfile.gettempdir(), "hadoop_home")
            os.makedirs(hadoop_home, exist_ok=True)
            os.makedirs(os.path.join(hadoop_home, "bin"), exist_ok=True)
            os.environ["HADOOP_HOME"] = hadoop_home
            logger.info(f"HADOOP_HOME configurado para Windows: {hadoop_home}")
        
        # Verificar si winutils.exe existe
        winutils_path = os.path.join(hadoop_home, "bin", "winutils.exe")
        if not os.path.exists(winutils_path):
            logger.warning(f"winutils.exe no encontrado en: {winutils_path}")
            logger.warning("Spark puede fallar sin winutils.exe en Windows")
            logger.warning("Ejecuta: spark-etl\\scripts\\descargar-winutils.ps1")
            logger.warning("O descarga manualmente desde: https://github.com/cdarlint/winutils")
        else:
            logger.info(f"winutils.exe encontrado en: {winutils_path}")
    
    # Paquetes necesarios para conectores
    # MySQL: Driver JDBC para MySQL (opcional - ahora usamos Kafka)
    # MongoDB: Conector Spark-MongoDB (opcional - ahora usamos Kafka)
    # Kafka: Conector Kafka para Spark (requerido para escribir a Kafka)
    spark_packages = [
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"  # Conector Kafka para Spark 3.x (NO requiere Python workers)
    ]
    packages_str = ",".join(spark_packages)
    
    # Configurar checkpoint location según el sistema operativo
    if platform.system() == "Windows":
        checkpoint_dir = os.path.join(tempfile.gettempdir(), "spark-checkpoint")
    else:
        checkpoint_dir = "/tmp/spark-checkpoint"
    
    spark = SparkSession.builder \
        .appName(Config.SPARK_APP_NAME) \
        .master(Config.SPARK_MASTER) \
        .config("spark.jars.packages", packages_str) \
        .config("spark.driver.memory", Config.SPARK_DRIVER_MEMORY) \
        .config("spark.executor.memory", Config.SPARK_EXECUTOR_MEMORY) \
        .config("spark.sql.streaming.checkpointLocation", checkpoint_dir) \
        .config("spark.python.worker.reuse", "true") \
        .config("spark.python.worker.timeout", "120s") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
        .config("spark.hadoop.fs.defaultFS", "file:///") \
        .config("spark.driver.host", "localhost") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.network.timeout", "800s") \
        .config("spark.executor.heartbeatInterval", "60s") \
        .config("spark.sql.adaptive.enabled", "false") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "false") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel(Config.LOG_LEVEL)
    logger.info(f"Spark session creada con paquetes: {packages_str}")
    logger.info(f"Checkpoint location: {checkpoint_dir}")
    return spark

def process_events(spark: SparkSession):
    """Procesa eventos de la cola"""
    # Crear procesadores
    sound_processor = SoundProcessor(spark)
    distance_processor = DistanceProcessor(spark)
    air_processor = AirProcessor(spark)
    
    # Inicializar Kafka sink (NO requiere Python workers - usa conector Kafka Java/Scala)
    # Spark escribe a Kafka, y db-writer consume de Kafka para escribir a MySQL y MongoDB
    kafka_sink = KafkaSink(spark)
    
    logger.info("Procesadores y Kafka sink inicializados (Spark -> Kafka -> db-writer -> DBs)")
    
    while True:
        try:
            # Obtener batch de eventos
            if len(events_queue) == 0:
                time.sleep(1)
                continue
            
            batch = get_events_batch(size=100)  # Procesar hasta 100 eventos a la vez
            
            if not batch:
                continue
            
            logger.info(f"Procesando batch de {len(batch)} eventos")
            
            # Separar eventos por tipo
            sound_events = [e for e in batch if 'WS302' in e.get('model', '') or 'sound' in e.get('model', '').lower()]
            distance_events = [e for e in batch if 'EM310' in e.get('model', '') or 'distance' in e.get('model', '').lower()]
            air_events = [e for e in batch if 'EM500' in e.get('model', '') or 'co2' in e.get('model', '').lower() or 'air' in e.get('model', '').lower()]
            
            # Procesar eventos de sonido
            if sound_events:
                try:
                    df = sound_processor.create_streaming_df(sound_events)
                    df = sound_processor.validate_and_clean(df)
                    # Solo procesar si hay datos (evitar operaciones en DataFrames vacíos)
                    try:
                        metrics = sound_processor.aggregate_metrics(df)
                        # Escribir a Kafka (NO requiere Python workers - usa conector Kafka Java/Scala)
                        # db-writer consumirá de Kafka y escribirá a MySQL y MongoDB
                        try:
                            kafka_sink.write_metrics(metrics, "sound_metrics_1m")
                        except Exception as kafka_error:
                            logger.warning(f"Error escribiendo métricas a Kafka (sonido): {kafka_error}")
                        
                        try:
                            kafka_sink.write_readings(df, "sound_readings_clean")
                        except Exception as kafka_error:
                            logger.warning(f"Error escribiendo lecturas a Kafka (sonido): {kafka_error}")
                        
                        logger.info(f"Procesados {len(sound_events)} eventos de sonido")
                    except Exception as e2:
                        logger.error(f"Error en agregación de sonido: {e2}")
                        import traceback
                        logger.error(traceback.format_exc())
                        logger.warn("Continuando con siguiente batch")
                except Exception as e:
                    logger.error(f"Error procesando eventos de sonido: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
            
            # Procesar eventos de distancia
            if distance_events:
                try:
                    df = distance_processor.create_streaming_df(distance_events)
                    df = distance_processor.validate_and_clean(df)
                    # Solo procesar si hay datos
                    try:
                        metrics = distance_processor.aggregate_metrics(df)
                        # Escribir a Kafka (NO requiere Python workers - usa conector Kafka Java/Scala)
                        try:
                            kafka_sink.write_metrics(metrics, "distance_metrics_1m")
                        except Exception as kafka_error:
                            logger.warning(f"Error escribiendo métricas a Kafka (distancia): {kafka_error}")
                        
                        try:
                            kafka_sink.write_readings(df, "distance_readings_clean")
                        except Exception as kafka_error:
                            logger.warning(f"Error escribiendo lecturas a Kafka (distancia): {kafka_error}")
                        
                        logger.info(f"Procesados {len(distance_events)} eventos de distancia")
                    except Exception as e2:
                        logger.error(f"Error en agregación de distancia: {e2}")
                        import traceback
                        logger.error(traceback.format_exc())
                        logger.warn("Continuando con siguiente batch")
                except Exception as e:
                    logger.error(f"Error procesando eventos de distancia: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
            
            # Procesar eventos de aire
            if air_events:
                try:
                    df = air_processor.create_streaming_df(air_events)
                    df = air_processor.validate_and_clean(df)
                    # Solo procesar si hay datos
                    try:
                        metrics = air_processor.aggregate_metrics(df)
                        # Escribir a Kafka (NO requiere Python workers - usa conector Kafka Java/Scala)
                        try:
                            kafka_sink.write_metrics(metrics, "air_metrics_1m")
                        except Exception as kafka_error:
                            logger.warning(f"Error escribiendo métricas a Kafka (aire): {kafka_error}")
                        
                        try:
                            kafka_sink.write_readings(df, "air_readings_clean")
                        except Exception as kafka_error:
                            logger.warning(f"Error escribiendo lecturas a Kafka (aire): {kafka_error}")
                        
                        logger.info(f"Procesados {len(air_events)} eventos de aire")
                    except Exception as e2:
                        logger.error(f"Error en agregación de aire: {e2}")
                        import traceback
                        logger.error(traceback.format_exc())
                        logger.warn("Continuando con siguiente batch")
                except Exception as e:
                    logger.error(f"Error procesando eventos de aire: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
            
        except Exception as e:
            logger.error(f"Error en el loop de procesamiento: {e}")
            time.sleep(5)

def main():
    """Función principal"""
    logger.info("=== Iniciando Spark ETL ===")
    logger.info(f"Spark Master: {Config.SPARK_MASTER}")
    logger.info(f"HTTP Server: {Config.HTTP_HOST}:{Config.HTTP_PORT}")
    
    # Crear sesión de Spark
    spark = create_spark_session()
    logger.info("Spark session creada")
    
    # Iniciar servidor HTTP en un thread separado
    http_thread = threading.Thread(target=start_server, daemon=True)
    http_thread.start()
    logger.info("Servidor HTTP iniciado")
    
    # Esperar un momento para que el servidor se inicie
    time.sleep(2)
    
    # Iniciar procesamiento de eventos
    try:
        process_events(spark)
    except KeyboardInterrupt:
        logger.info("Deteniendo ETL...")
    finally:
        spark.stop()
        logger.info("Spark detenido")

if __name__ == '__main__':
    main()

