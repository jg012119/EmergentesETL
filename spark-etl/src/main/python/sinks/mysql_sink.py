"""
Sink para escribir datos a MySQL
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, to_timestamp
from config import Config
import logging

logger = logging.getLogger(__name__)

class MySQLSink:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.mysql_url = Config.get_mysql_url()
        credentials = Config.get_mysql_credentials()
        self.properties = {
            "user": credentials['user'],
            "password": credentials['password'],
            "driver": "com.mysql.cj.jdbc.Driver"
        }
    
    def write_metrics(self, df: DataFrame, table_name: str, mode: str = "append"):
        """Escribe métricas agregadas a MySQL"""
        try:
            # Preparar DataFrame para escritura
            df_to_write = df.select(
                col("sensor_id"),
                col("window_info.start").alias("window_start"),
                col("window_info.end").alias("window_end"),
                *[col(c) for c in df.columns if c not in ["sensor_id", "window_info"]]
            )
            
            df_to_write.write \
                .format("jdbc") \
                .option("url", self.mysql_url) \
                .option("dbtable", table_name) \
                .option("user", self.properties["user"]) \
                .option("password", self.properties["password"]) \
                .option("driver", self.properties["driver"]) \
                .mode(mode) \
                .save()
            
            logger.info(f"Métricas escritas a MySQL: {table_name}")
        except Exception as e:
            # No hacer raise - solo registrar el error y continuar
            logger.error(f"Error al escribir a MySQL {table_name}: {e}")
            logger.warn(f"No se pudieron escribir métricas a MySQL: {table_name}. Continuando sin MySQL.")
            # No hacer raise para que el procesamiento continúe

