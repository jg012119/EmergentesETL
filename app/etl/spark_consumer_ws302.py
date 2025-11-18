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
logger.info("🚀 CONSUMER SPARK - WS302 SONIDO")
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
TABLA = "ws302_sonido"

spark = SparkSession.builder \
    .appName("SparkConsumer_WS302") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint_ws302") \
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
            mongo_collection = mongo_db["ws302_sonido"]
            # Verificar conexión
            mongo_client.admin.command('ping')
            logger.info(f"✅ Conectado a MongoDB Atlas - Base: {MONGO_DB_NAME}, Colección: ws302_sonido")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            mongo_client = None
            mongo_collection = None
        
        registros_guardados = 0
        
        for row in rows:
            try:
                value_str = row.value.decode('utf-8')
                data = json.loads(value_str)
                
                # FILTRAR SOLO WS302 (debe tener LAeq, LAI o LAImax)
                object_data = data.get("object", {})
                has_LAeq = "LAeq" in object_data
                has_LAI = "LAI" in object_data
                has_LAImax = "LAImax" in object_data
                
                if not (has_LAeq or has_LAI or has_LAImax):
                    continue
                
                # Extraer datos
                time_val = data.get("time", datetime.now().isoformat())
                tenant_name = data.get("deviceInfo", {}).get("tenantName", "")
                address = data.get("deviceInfo", {}).get("tags", {}).get("Address", "")
                location = data.get("deviceInfo", {}).get("tags", {}).get("Location", "")
                LAeq = object_data.get("LAeq")
                LAI = object_data.get("LAI")
                LAImax = object_data.get("LAImax")
                status = object_data.get("status", "")
                
                # Validar que al menos uno de los campos principales tenga valor (no null)
                has_valid_LAeq = LAeq is not None and LAeq != "" and str(LAeq).lower() != "null"
                has_valid_LAI = LAI is not None and LAI != "" and str(LAI).lower() != "null"
                has_valid_LAImax = LAImax is not None and LAImax != "" and str(LAImax).lower() != "null"
                
                if not (has_valid_LAeq or has_valid_LAI or has_valid_LAImax):
                    continue
                
                # Insertar en MySQL
                insert_sql = f"""
                    INSERT INTO `{TABLA}` (time, tenant_name, Address, Location, LAeq, LAI, LAImax, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (time_val, tenant_name, address, location, LAeq, LAI, LAImax, status))
                registros_guardados += 1
                
                # Insertar en MongoDB (solo campos con valores, sin null)
                if mongo_collection is not None:
                    try:
                        mongo_doc = {
                            "tipo": "WS302",
                            "time": time_val,
                            "batch_id": batch_id
                        }
                        if tenant_name and tenant_name != "":
                            mongo_doc["tenant_name"] = tenant_name
                        if address and address != "":
                            mongo_doc["Address"] = address
                        if location and location != "":
                            mongo_doc["Location"] = location
                        if has_valid_LAeq:
                            mongo_doc["LAeq"] = LAeq
                        if has_valid_LAI:
                            mongo_doc["LAI"] = LAI
                        if has_valid_LAImax:
                            mongo_doc["LAImax"] = LAImax
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
            logger.info(f"✅ Batch {batch_id}: {registros_guardados} registros WS302 guardados en MySQL")
            if mongo_collection is not None:
                logger.info(f"✅ Batch {batch_id}: {registros_guardados} registros WS302 guardados en MongoDB")
    
    except Exception as e:
        logger.error(f"❌ Error en procesar_lote: {e}")

query = df.writeStream \
    .foreachBatch(procesar_lote) \
    .start()

logger.info("✅ Streaming iniciado - Esperando datos WS302...")
query.awaitTermination()

