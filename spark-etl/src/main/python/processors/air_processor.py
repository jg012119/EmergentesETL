"""
Procesador para datos de sensores de aire (EM500)
"""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, avg, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from processors.base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class AirProcessor(BaseProcessor):
    def get_schema(self):
        return StructType([
            StructField("source", StringType(), True),
            StructField("model", StringType(), True),
            StructField("ts_utc", TimestampType(), True),
            StructField("sensor_id", StringType(), True),
            StructField("addr", StringType(), True),
            StructField("co2", DoubleType(), True),
            StructField("co2_status", StringType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("temperature_status", StringType(), True),
            StructField("humidity", DoubleType(), True),
            StructField("humidity_status", StringType(), True),
            StructField("pressure", DoubleType(), True),
            StructField("pressure_status", StringType(), True),
            StructField("geo", StringType(), True),
        ])
    
    def validate_and_clean(self, df: DataFrame) -> DataFrame:
        """Valida y limpia datos de aire"""
        # Filtrar valores fuera de rangos razonables
        df = df.filter(
            (col("co2").isNull() | ((col("co2") >= 0) & (col("co2") <= 10000))) &
            (col("temperature").isNull() | ((col("temperature") >= -50) & (col("temperature") <= 100))) &
            (col("humidity").isNull() | ((col("humidity") >= 0) & (col("humidity") <= 100))) &
            (col("pressure").isNull() | ((col("pressure") >= 0) & (col("pressure") <= 2000)))
        )
        
        # No usar df.count() para evitar problemas con Python workers
        logger.info("Datos de aire validados")
        return df
    
    def aggregate_metrics(self, df: DataFrame) -> DataFrame:
        """Calcula métricas agregadas para aire"""
        from pyspark.sql.functions import lit
        
        windowed = self.apply_window(df, "ts_utc")
        
        metrics = windowed.agg(
            avg("co2").alias("co2_avg"),
            avg("temperature").alias("temp_avg"),
            avg("humidity").alias("rh_avg"),
            avg("pressure").alias("press_avg"),
            count("*").alias("sample_n")
        )
        
        # Agregar alert_prob (por ahora NULL, se calculará con modelos probabilísticos después)
        metrics = metrics.withColumn("alert_prob", lit(None).cast("double"))
        
        return metrics.withColumnRenamed("window", "window_info")

