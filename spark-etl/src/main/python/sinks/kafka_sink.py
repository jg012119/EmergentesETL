"""
Sink para escribir datos a Kafka
Usa el conector Kafka de Spark (Java/Scala) - NO requiere Python workers
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, to_json, struct, lit
from config import Config
import logging

logger = logging.getLogger(__name__)

class KafkaSink:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.kafka_bootstrap_servers = Config.KAFKA_BOOTSTRAP_SERVERS
    
    def write_metrics(self, df: DataFrame, table_name: str):
        """
        Escribe métricas agregadas a Kafka para que db-writer las consuma y escriba en MySQL
        
        Args:
            df: DataFrame con métricas agregadas
            table_name: Nombre de la tabla MySQL (ej: "sound_metrics_1m")
        """
        try:
            # Aplanar estructuras anidadas como window_info
            df_to_write = df.select(
                col("sensor_id"),
                col("window_info.start").alias("window_start"),
                col("window_info.end").alias("window_end"),
                *[col(c) for c in df.columns if c not in ["sensor_id", "window_info"]]
            )
            
            # Agregar metadata: table_name para que db-writer sepa dónde escribir
            df_with_metadata = df_to_write.withColumn("_table_name", lit(table_name))
            
            # Convertir a JSON string (requerido por Kafka)
            df_json = df_with_metadata.select(
                col("sensor_id").alias("key"),  # Usar sensor_id como key para particionado
                to_json(struct([col(c) for c in df_with_metadata.columns])).alias("value")
            )
            
            # Escribir a Kafka usando el conector Kafka de Spark (Java/Scala - NO requiere Python workers)
            df_json.write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
                .option("topic", "processed.metrics.v1") \
                .mode("append") \
                .save()
            
            logger.info(f"Métricas escritas a Kafka (tabla: {table_name})")
        except Exception as e:
            logger.error(f"Error al escribir métricas a Kafka (tabla: {table_name}): {e}")
            logger.warn(f"No se pudieron escribir métricas a Kafka: {table_name}. Continuando sin Kafka.")
            # No hacer raise para que el procesamiento continúe
    
    def write_readings(self, df: DataFrame, collection_name: str):
        """
        Escribe lecturas limpias a Kafka para que db-writer las consuma y escriba en MongoDB
        
        Args:
            df: DataFrame con lecturas limpias
            collection_name: Nombre de la colección MongoDB (ej: "sound_readings_clean")
        """
        try:
            # Agregar metadata: collection_name para que db-writer sepa dónde escribir
            df_with_metadata = df.withColumn("_collection_name", lit(collection_name))
            
            # Convertir a JSON string (requerido por Kafka)
            # Usar sensor_id como key si existe, sino usar ts_utc
            key_col = col("sensor_id") if "sensor_id" in df.columns else col("ts_utc")
            
            df_json = df_with_metadata.select(
                key_col.alias("key"),
                to_json(struct([col(c) for c in df_with_metadata.columns])).alias("value")
            )
            
            # Escribir a Kafka usando el conector Kafka de Spark (Java/Scala - NO requiere Python workers)
            df_json.write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
                .option("topic", "processed.readings.v1") \
                .mode("append") \
                .save()
            
            logger.info(f"Lecturas escritas a Kafka (colección: {collection_name})")
        except Exception as e:
            logger.error(f"Error al escribir lecturas a Kafka (colección: {collection_name}): {e}")
            logger.warn(f"No se pudieron escribir lecturas a Kafka: {collection_name}. Continuando sin Kafka.")
            # No hacer raise para que el procesamiento continúe

