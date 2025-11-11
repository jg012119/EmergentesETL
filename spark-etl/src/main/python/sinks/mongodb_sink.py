"""
Sink para escribir datos a MongoDB
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, struct, to_json
from config import Config
import logging

logger = logging.getLogger(__name__)

class MongoDBSink:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.mongo_uri = Config.get_mongo_uri()
        self.mongo_database = self._get_mongo_database()
    
    def _get_mongo_database(self):
        """Obtiene el nombre de la base de datos de la URI o de la configuración"""
        # Si hay URI de Atlas, intentar extraer el nombre de la base de datos
        if Config.MONGO_ATLAS_URI:
            from urllib.parse import urlparse
            try:
                parsed = urlparse(Config.MONGO_ATLAS_URI)
                # La base de datos puede estar en el path o en los parámetros
                if parsed.path and parsed.path != '/':
                    # Remover el / inicial
                    db_name = parsed.path.lstrip('/')
                    if db_name:
                        return db_name
            except Exception as e:
                logger.warning(f"No se pudo extraer nombre de BD de MONGO_ATLAS_URI: {e}")
        
        # Si no se pudo extraer de la URI, usar la configuración
        return Config.MONGO_DATABASE
    
    def write_readings(self, df: DataFrame, collection_name: str):
        """Escribe lecturas limpias a MongoDB"""
        try:
            # Intentar con el conector de Spark para MongoDB (no requiere Python workers)
            df.write \
                .format("mongo") \
                .option("uri", self.mongo_uri) \
                .option("database", self.mongo_database) \
                .option("collection", collection_name) \
                .mode("append") \
                .save()
            
            logger.info(f"Lecturas escritas a MongoDB: {collection_name}")
        except Exception as e:
            # Si el conector Spark-MongoDB no está disponible, no intentar PyMongo
            # porque PyMongo requiere collect() o foreachPartition() que necesitan Python workers
            logger.warn(f"Conector Spark-MongoDB no disponible: {e}")
            logger.warn(f"No se pudieron escribir lecturas a MongoDB: {collection_name}.")
            logger.warn(f"Para habilitar MongoDB, instala el conector: pip install pyspark[connectors]")
            logger.warn(f"Continuando sin MongoDB - el sistema seguirá procesando datos.")
            # No hacer raise para que el procesamiento continúe
    

