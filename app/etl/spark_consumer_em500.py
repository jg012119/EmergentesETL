from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, MapType
import mysql.connector
from pymongo import MongoClient
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("🚀 CONSUMER SPARK - EM500 CO2")
logger.info("=" * 80)

DB_HOST = "mysql"
DB_PORT = 3306
DB_NAME = "emergentETL"
DB_USER = "root"
DB_PASSWORD = "Os51t=Ag/3=B"
MONGO_ATLAS_URI = "mongodb+srv://BDETLEmergentes:12345@bdemergetesetl.lwsmez4.mongodb.net/?appName=BDEmergetesETL"
MONGO_DB_NAME = "BDETLEmergentes"
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "datos_sensores"
TABLA = "em500_co2"

spark = SparkSession.builder \
    .appName("SparkConsumer_EM500") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint_em500") \
    .getOrCreate()

logger.info("✅ Spark Session creada")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

logger.info("✅ Lectura de Kafka configurada")

def procesar_lote(batch_df, batch_id):
    try:
        rows = batch_df.collect()
        if not rows:
            return
        
        # Reintentar conexión a MySQL si falla
        max_retries = 3
        retry_count = 0
        conn = None
        while retry_count < max_retries:
            try:
                conn = mysql.connector.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    autocommit=True,
                    connect_timeout=10
                )
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"❌ No se pudo conectar a MySQL después de {max_retries} intentos: {e}")
                    return
                logger.warning(f"⚠️ Reintentando conexión a MySQL (intento {retry_count}/{max_retries})...")
                import time
                time.sleep(2)
        
        cursor = conn.cursor()
        
        # Conexión a MongoDB
        try:
            mongo_client = MongoClient(MONGO_ATLAS_URI, serverSelectionTimeoutMS=10000)
            mongo_db = mongo_client[MONGO_DB_NAME]
            mongo_collection = mongo_db["em500_co2"]
            # Verificar conexión
            mongo_client.admin.command('ping')
            logger.info(f"✅ Conectado a MongoDB Atlas - Base: {MONGO_DB_NAME}, Colección: em500_co2")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            mongo_client = None
            mongo_collection = None
        
        registros_guardados = 0
        
        for row in rows:
            try:
                value_str = row.value.decode('utf-8')
                data = json.loads(value_str)
                
                # FILTRAR SOLO EM500 (debe tener co2, temperature, humidity o pressure)
                object_data = data.get("object", {})
                has_co2 = "co2" in object_data
                has_temp = "temperature" in object_data
                has_hum = "humidity" in object_data
                has_press = "pressure" in object_data
                
                # También verificar por nombre de dispositivo
                device_name = data.get("deviceInfo", {}).get("deviceName", "").upper()
                is_ems = device_name.startswith("EMS-")
                
                if not (has_co2 or has_temp or has_hum or has_press or is_ems):
                    continue
                
                # Extraer datos
                time_val = data.get("time", datetime.now().isoformat())
                address = data.get("deviceInfo", {}).get("tags", {}).get("Address", "")
                location = data.get("deviceInfo", {}).get("tags", {}).get("Location", "")
                
                co2 = object_data.get("co2")
                co2_status = object_data.get("co2_status", "")
                co2_message = object_data.get("co2_message", "")
                temperature = object_data.get("temperature")
                temperature_status = object_data.get("temperature_status", "")
                temperature_message = object_data.get("temperature_message", "")
                humidity = object_data.get("humidity")
                humidity_status = object_data.get("humidity_status", "")
                humidity_message = object_data.get("humidity_message", "")
                pressure = object_data.get("pressure")
                pressure_status = object_data.get("pressure_status", "")
                pressure_message = object_data.get("pressure_message", "")
                
                # Validar que al menos uno de los campos principales tenga valor (no null)
                has_valid_co2 = co2 is not None and co2 != "" and str(co2).lower() != "null"
                has_valid_temp = temperature is not None and temperature != "" and str(temperature).lower() != "null"
                has_valid_hum = humidity is not None and humidity != "" and str(humidity).lower() != "null"
                has_valid_press = pressure is not None and pressure != "" and str(pressure).lower() != "null"
                
                if not (has_valid_co2 or has_valid_temp or has_valid_hum or has_valid_press):
                    continue
                
                # Insertar en MySQL
                insert_sql = f"""
                    INSERT INTO `{TABLA}` (
                        time, device_name, Address, Location,
                        co2, co2_status, co2_message,
                        temperature, temperature_status, temperature_message,
                        humidity, humidity_status, humidity_message,
                        pressure, pressure_status, pressure_message
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    time_val, device_name, address, location,
                    co2, co2_status, co2_message,
                    temperature, temperature_status, temperature_message,
                    humidity, humidity_status, humidity_message,
                    pressure, pressure_status, pressure_message
                ))
                registros_guardados += 1
                
                # Insertar en MongoDB (solo campos con valores, sin null)
                if mongo_collection is not None:
                    try:
                        mongo_doc = {
                            "tipo": "EM500",
                            "time": time_val,
                            "batch_id": batch_id
                        }
                        if device_name and device_name != "":
                            mongo_doc["device_name"] = device_name
                        if address and address != "":
                            mongo_doc["Address"] = address
                        if location and location != "":
                            mongo_doc["Location"] = location
                        if has_valid_co2:
                            mongo_doc["co2"] = co2
                        if has_valid_temp:
                            mongo_doc["temperature"] = temperature
                        if has_valid_hum:
                            mongo_doc["humidity"] = humidity
                        if has_valid_press:
                            mongo_doc["pressure"] = pressure
                        result = mongo_collection.insert_one(mongo_doc)
                        if result.inserted_id:
                            logger.debug(f"✅ Insertado en MongoDB: {result.inserted_id}")
                    except Exception as e:
                        logger.error(f"❌ Error insertando en MongoDB: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                
            except Exception as e:
                logger.error(f"❌ Error procesando registro: {e}")
                continue
        
        cursor.close()
        if conn:
            conn.close()
        if mongo_client:
            mongo_client.close()
        
        if registros_guardados > 0:
            logger.info(f"✅ Batch {batch_id}: {registros_guardados} registros EM500 guardados en MySQL")
            if mongo_collection is not None:
                logger.info(f"✅ Batch {batch_id}: {registros_guardados} registros EM500 guardados en MongoDB")
    
    except Exception as e:
        logger.error(f"❌ Error en procesar_lote: {e}")

query = df.writeStream \
    .foreachBatch(procesar_lote) \
    .start()

logger.info("✅ Streaming iniciado - Esperando datos EM500...")
query.awaitTermination()

