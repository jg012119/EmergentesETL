"""
Procesador para datos de sensores de sonido (WS302)
"""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, avg, max as spark_max, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from processors.base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class SoundProcessor(BaseProcessor):
    def get_schema(self):
        return StructType([
            StructField("source", StringType(), True),
            StructField("model", StringType(), True),
            StructField("ts_utc", TimestampType(), True),
            StructField("sensor_id", StringType(), True),
            StructField("addr", StringType(), True),
            StructField("LAeq", DoubleType(), True),
            StructField("LAI", DoubleType(), True),
            StructField("LAImax", DoubleType(), True),
            StructField("status", StringType(), True),
            StructField("geo", StringType(), True),  # Se puede parsear después
        ])
    
    def validate_and_clean(self, df: DataFrame) -> DataFrame:
        """Valida y limpia datos de sonido"""
        # Filtrar valores fuera de rango razonable (0-200 dB)
        df = df.filter(
            (col("LAeq").isNull() | ((col("LAeq") >= 0) & (col("LAeq") <= 200))) &
            (col("LAI").isNull() | ((col("LAI") >= 0) & (col("LAI") <= 200))) &
            (col("LAImax").isNull() | ((col("LAImax") >= 0) & (col("LAImax") <= 200)))
        )
        
        # No usar df.count() para evitar problemas con Python workers
        logger.info("Datos de sonido validados")
        return df
    
    def aggregate_metrics(self, df: DataFrame) -> DataFrame:
        """Calcula métricas agregadas para sonido"""
        from pyspark.sql.functions import lit
        
        windowed = self.apply_window(df, "ts_utc")
        
        # Usar funciones de agregación simples que no requieren Python workers
        # percentile_approx puede requerir Python workers, usar max como aproximación temporal
        metrics = windowed.agg(
            avg("LAeq").alias("laeq_avg"),
            avg("LAI").alias("lai_avg"),
            spark_max("LAImax").alias("laimax_max"),
            spark_max("LAeq").alias("p95_laeq"),  # Temporalmente usar max en lugar de percentile
            count("*").alias("sample_n")
        )
        
        # Agregar alert_prob (por ahora NULL, se calculará con modelos probabilísticos después)
        metrics = metrics.withColumn("alert_prob", lit(None).cast("double"))
        
        return metrics.withColumnRenamed("window", "window_info")

