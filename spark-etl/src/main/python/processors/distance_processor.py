"""
Procesador para datos de sensores de distancia (EM310)
"""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, avg, max as spark_max, min as spark_min, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from processors.base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class DistanceProcessor(BaseProcessor):
    def get_schema(self):
        return StructType([
            StructField("source", StringType(), True),
            StructField("model", StringType(), True),
            StructField("ts_utc", TimestampType(), True),
            StructField("sensor_id", StringType(), True),
            StructField("addr", StringType(), True),
            StructField("distance", DoubleType(), True),
            StructField("status", StringType(), True),
            StructField("geo", StringType(), True),
        ])
    
    def validate_and_clean(self, df: DataFrame) -> DataFrame:
        """Valida y limpia datos de distancia"""
        # Filtrar valores fuera de rango razonable (0-100 m)
        df = df.filter(
            (col("distance").isNull() | ((col("distance") >= 0) & (col("distance") <= 100)))
        )
        
        # No usar df.count() para evitar problemas con Python workers
        logger.info("Datos de distancia validados")
        return df
    
    def aggregate_metrics(self, df: DataFrame) -> DataFrame:
        """Calcula métricas agregadas para distancia"""
        from pyspark.sql.functions import lit
        
        windowed = self.apply_window(df, "ts_utc")
        
        metrics = windowed.agg(
            avg("distance").alias("distance_avg"),
            spark_min("distance").alias("distance_min"),
            spark_max("distance").alias("distance_max"),
            count("*").alias("sample_n")
        )
        
        # Agregar anomaly_prob (por ahora NULL, se calculará con modelos probabilísticos después)
        metrics = metrics.withColumn("anomaly_prob", lit(None).cast("double"))
        
        return metrics.withColumnRenamed("window", "window_info")

