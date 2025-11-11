"""
Cliente HTTP para enviar datos al servicio db-writer
"""
import requests
import logging
import json
from typing import List, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class DBWriterClient:
    """Cliente para enviar datos procesados al servicio db-writer"""
    
    def __init__(self):
        self.base_url = f"http://{Config.DB_WRITER_HOST}:{Config.DB_WRITER_PORT}"
        self.timeout = 30
    
    def send_metrics(self, table_name: str, metrics: List[Dict[str, Any]]) -> bool:
        """
        Envía métricas agregadas al servicio db-writer para escribir en MySQL
        
        Args:
            table_name: Nombre de la tabla (ej: "sound_metrics_1m")
            metrics: Lista de diccionarios con las métricas
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not metrics:
            logger.debug(f"No hay métricas para enviar a {table_name}")
            return True
        
        try:
            url = f"{self.base_url}/api/metrics"
            payload = {
                "table": table_name,
                "metrics": metrics
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Métricas enviadas a db-writer: {table_name} ({len(metrics)} registros)")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar métricas a db-writer {table_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar métricas a db-writer {table_name}: {e}")
            return False
    
    def send_readings(self, collection_name: str, readings: List[Dict[str, Any]]) -> bool:
        """
        Envía lecturas limpias al servicio db-writer para escribir en MongoDB
        
        Args:
            collection_name: Nombre de la colección (ej: "sound_readings_clean")
            readings: Lista de diccionarios con las lecturas
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not readings:
            logger.debug(f"No hay lecturas para enviar a {collection_name}")
            return True
        
        try:
            url = f"{self.base_url}/api/readings"
            payload = {
                "collection": collection_name,
                "readings": readings
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Lecturas enviadas a db-writer: {collection_name} ({len(readings)} documentos)")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar lecturas a db-writer {collection_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar lecturas a db-writer {collection_name}: {e}")
            return False
    
    def send_dataframe_as_json(self, df, table_or_collection: str, is_metrics: bool = True) -> bool:
        """
        Envía un DataFrame al db-writer usando foreachPartition para evitar collect()
        
        Args:
            df: DataFrame de Spark
            table_or_collection: Nombre de tabla (métricas) o colección (lecturas)
            is_metrics: True para métricas (MySQL), False para lecturas (MongoDB)
            
        Returns:
            True si se programó correctamente, False en caso contrario
        """
        try:
            # Para métricas, aplanar estructuras anidadas como window_info
            if is_metrics and "window_info" in df.columns:
                from pyspark.sql.functions import col
                df = df.select(
                    col("sensor_id"),
                    col("window_info.start").alias("window_start"),
                    col("window_info.end").alias("window_end"),
                    *[col(c) for c in df.columns if c not in ["sensor_id", "window_info"]]
                )
            
            # Usar foreachPartition para enviar datos sin collect()
            # Esto evita traer todos los datos al driver
            base_url = self.base_url
            timeout = self.timeout
            
            def send_partition(partition):
                """Función que se ejecuta en cada partición"""
                import requests
                import json
                import logging
                
                partition_logger = logging.getLogger(__name__)
                
                # Convertir cada fila a diccionario
                data_list = []
                for row in partition:
                    # Convertir Row a diccionario
                    row_dict = row.asDict()
                    # Convertir tipos que no son JSON serializables
                    for key, value in row_dict.items():
                        if hasattr(value, 'isoformat'):  # datetime
                            row_dict[key] = value.isoformat()
                        elif value is None:
                            row_dict[key] = None
                    data_list.append(row_dict)
                
                if not data_list:
                    return
                
                # Enviar batch al db-writer
                try:
                    if is_metrics:
                        url = f"{base_url}/api/metrics"
                        payload = {
                            "table": table_or_collection,
                            "metrics": data_list
                        }
                    else:
                        url = f"{base_url}/api/readings"
                        payload = {
                            "collection": table_or_collection,
                            "readings": data_list
                        }
                    
                    response = requests.post(url, json=payload, timeout=timeout)
                    response.raise_for_status()
                    partition_logger.info(f"Enviados {len(data_list)} registros a db-writer ({table_or_collection})")
                except Exception as e:
                    partition_logger.error(f"Error enviando partición a db-writer ({table_or_collection}): {e}")
            
            # Ejecutar foreachPartition (esto se ejecuta en los workers, no en el driver)
            df.foreachPartition(send_partition)
            
            logger.info(f"Datos programados para envío a db-writer: {table_or_collection}")
            return True
                
        except Exception as e:
            logger.error(f"Error al programar envío de DataFrame a db-writer {table_or_collection}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def health_check(self) -> bool:
        """Verifica que el servicio db-writer esté disponible"""
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"db-writer no está disponible: {e}")
            return False

