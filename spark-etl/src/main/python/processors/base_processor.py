"""
Procesador base para datos de sensores
"""
from abc import ABC, abstractmethod
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, window, count, avg, max as spark_max, min as spark_min, to_timestamp, when
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import logging

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    def __init__(self, spark: SparkSession, window_duration: str = "1 minute", window_slide: str = "10 seconds"):
        self.spark = spark
        self.window_duration = window_duration
        self.window_slide = window_slide
        
    @abstractmethod
    def get_schema(self) -> StructType:
        """Define el esquema de los datos para este tipo de sensor"""
        pass
    
    @abstractmethod
    def validate_and_clean(self, df: DataFrame) -> DataFrame:
        """Valida y limpia los datos"""
        pass
    
    @abstractmethod
    def aggregate_metrics(self, df: DataFrame) -> DataFrame:
        """Calcula métricas agregadas por ventana"""
        pass
    
    def create_streaming_df(self, events: list) -> DataFrame:
        """Crea un DataFrame de Spark desde una lista de eventos"""
        if not events:
            # Retornar DataFrame vacío con el esquema correcto
            return self.spark.createDataFrame([], self.get_schema())
        
        # Normalizar eventos: convertir tipos antes de crear DataFrame
        normalized_events = self._normalize_events(events)
        
        # Crear esquema temporal con ts_utc como StringType para aceptar strings ISO 8601
        schema_with_string_ts = self._get_schema_with_string_timestamp()
        
        # Convertir eventos normalizados a DataFrame con ts_utc como string
        df = self.spark.createDataFrame(normalized_events, schema=schema_with_string_ts)
        
        # Convertir ts_utc de string ISO 8601 a Timestamp usando funciones nativas de Spark
        # Reemplazar 'Z' por '+00:00' para formato estándar
        from pyspark.sql.functions import regexp_replace, coalesce
        
        # Intentar primero con milisegundos, luego sin milisegundos
        ts_str_clean = regexp_replace(col("ts_utc"), "Z$", "+00:00")
        df = df.withColumn(
            "ts_utc",
            coalesce(
                to_timestamp(ts_str_clean, "yyyy-MM-dd'T'HH:mm:ss.SSSXXX"),
                to_timestamp(ts_str_clean, "yyyy-MM-dd'T'HH:mm:ssXXX"),
                to_timestamp(col("ts_utc"))  # Fallback: parseo automático
            )
        )
        
        return df
    
    def _normalize_events(self, events: list) -> list:
        """Normaliza los eventos: convierte tipos de datos (int -> float, etc.)"""
        normalized = []
        schema = self.get_schema()
        
        # Crear mapa de tipos esperados por campo
        field_types = {field.name: field.dataType for field in schema.fields}
        
        for event in events:
            normalized_event = {}
            for key, value in event.items():
                if key not in field_types:
                    # Campo no está en el esquema, omitirlo
                    continue
                
                expected_type = field_types[key]
                
                # Normalizar según el tipo esperado
                if isinstance(expected_type, DoubleType):
                    # Convertir int/float a float
                    if value is None:
                        normalized_event[key] = None
                    elif isinstance(value, (int, float)):
                        normalized_event[key] = float(value)
                    else:
                        try:
                            normalized_event[key] = float(value)
                        except (ValueError, TypeError):
                            normalized_event[key] = None
                elif isinstance(expected_type, StringType):
                    # Asegurar que sea string
                    normalized_event[key] = str(value) if value is not None else None
                elif isinstance(expected_type, TimestampType):
                    # Mantener como string para conversión posterior
                    normalized_event[key] = str(value) if value is not None else None
                else:
                    # Otros tipos, mantener como están
                    normalized_event[key] = value
            
            normalized.append(normalized_event)
        
        return normalized
    
    def _get_schema_with_string_timestamp(self) -> StructType:
        """Obtiene el esquema con ts_utc como StringType para permitir conversión desde ISO 8601"""
        schema = self.get_schema()
        # Crear nuevo esquema reemplazando TimestampType por StringType para ts_utc
        fields = []
        for field in schema.fields:
            if field.name == "ts_utc" and isinstance(field.dataType, TimestampType):
                fields.append(StructField(field.name, StringType(), field.nullable, field.metadata))
            else:
                fields.append(field)
        return StructType(fields)
    
    def apply_window(self, df: DataFrame, timestamp_col: str = "ts_utc") -> DataFrame:
        """Aplica ventaneo deslizante a los datos"""
        # Temporalmente deshabilitar watermark para evitar problemas con Python workers
        # El watermark puede causar problemas de conexión en Windows
        return df.groupBy(
            window(col(timestamp_col), self.window_duration, self.window_slide),
            col("sensor_id")
        )

