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
logger.info("🚀 CONSUMER SPARK - EM310 SOTERRADOS")
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
TABLA = "em310_soterrados"

spark = SparkSession.builder \
    .appName("SparkConsumer_EM310") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint_em310") \
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
            mongo_collection = mongo_db["em310_soterrados"]
            # Verificar conexión
            mongo_client.admin.command('ping')
            logger.info(f"✅ Conectado a MongoDB Atlas - Base: {MONGO_DB_NAME}, Colección: em310_soterrados")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            mongo_client = None
            mongo_collection = None
        
        registros_guardados = 0
        
        for row in rows:
            try:
                value_str = row.value.decode('utf-8')
                data = json.loads(value_str)
                
                # FILTRAR SOLO EM310 (debe tener "distance")
                if "object" not in data or "distance" not in data.get("object", {}):
                    continue
                
                # Extraer datos
                time_val = data.get("time", datetime.now().isoformat())
                device_name = data.get("deviceInfo", {}).get("deviceName", "")
                address = data.get("deviceInfo", {}).get("tags", {}).get("Address", "")
                location = data.get("deviceInfo", {}).get("tags", {}).get("Location", "")
                distance = data.get("object", {}).get("distance", "")
                status = data.get("object", {}).get("status", "")
                
                # Validar que distance y status no sean null/vacíos
                if distance is None or distance == "" or str(distance).lower() == "null":
                    continue
                if status is None or status == "" or str(status).lower() == "null":
                    continue
                
                # Insertar en MySQL
                insert_sql = f"""
                    INSERT INTO `{TABLA}` (time, device_name, Address, Location, distance, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (time_val, device_name, address, location, distance, status))
                registros_guardados += 1
                
                # Insertar en MongoDB (solo campos con valores)
                if mongo_collection is not None:
                    try:
                        mongo_doc = {
                            "tipo": "EM310",
                            "time": time_val,
                            "batch_id": batch_id
                        }
                        if device_name and device_name != "":
                            mongo_doc["device_name"] = device_name
                        if address and address != "":
                            mongo_doc["Address"] = address
                        if location and location != "":
                            mongo_doc["Location"] = location
                        if distance and distance != "":
                            mongo_doc["distance"] = distance
                        if status and status != "":
                            mongo_doc["status"] = status
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
            logger.info(f"✅ Batch {batch_id}: {registros_guardados} registros EM310 guardados en MySQL")
            if mongo_collection is not None:
                logger.info(f"✅ Batch {batch_id}: {registros_guardados} registros EM310 guardados en MongoDB")
    
    except Exception as e:
        logger.error(f"❌ Error en procesar_lote: {e}")

query = df.writeStream \
    .foreachBatch(procesar_lote) \
    .start()

logger.info("✅ Streaming iniciado - Esperando datos EM310...")
query.awaitTermination()

