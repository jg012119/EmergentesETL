import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Config:
    # Spark
    SPARK_MASTER = os.getenv('SPARK_MASTER', 'local[*]')
    SPARK_APP_NAME = os.getenv('SPARK_APP_NAME', 'EmergentETL')
    SPARK_DRIVER_MEMORY = os.getenv('SPARK_DRIVER_MEMORY', '2g')
    SPARK_EXECUTOR_MEMORY = os.getenv('SPARK_EXECUTOR_MEMORY', '2g')
    
    # HTTP Server
    HTTP_HOST = os.getenv('HTTP_HOST', '0.0.0.0')
    HTTP_PORT = int(os.getenv('HTTP_PORT', '8082'))  # Cambiado a 8082 para evitar conflicto con Docker/WSL
    HTTP_ENDPOINT = os.getenv('HTTP_ENDPOINT', '/api/data')
    
    # DB Writer Service (servicio Node.js que escribe a MySQL y MongoDB)
    DB_WRITER_HOST = os.getenv('DB_WRITER_HOST', 'localhost')
    DB_WRITER_PORT = int(os.getenv('DB_WRITER_PORT', '3001'))
    
    # Kafka (para escribir datos procesados)
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092')
    
    # Puerto actual usado (se actualiza si se usa un puerto alternativo)
    _actual_port = None
    
    @classmethod
    def get_http_port(cls):
        """Obtiene el puerto HTTP actual (puede ser diferente al configurado si hubo conflicto)"""
        return cls._actual_port if cls._actual_port else cls.HTTP_PORT
    
    @classmethod
    def set_http_port(cls, port: int):
        """Establece el puerto HTTP actual"""
        cls._actual_port = port
    
    # MySQL (soporta URI completa o parámetros individuales)
    MYSQL_URI = os.getenv('MYSQL_URI', None)  # URI completa para MySQL hosteado (ej: mysql://user:pass@host:port/db)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'emergent_etl')
    MYSQL_USER = os.getenv('MYSQL_USER', 'etl_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'etl_password')
    
    # MongoDB (soporta MongoDB Atlas con URI o MongoDB local)
    MONGO_ATLAS_URI = os.getenv('MONGO_ATLAS_URI', None)  # URI completa para MongoDB Atlas
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
    MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'emergent_etl')
    MONGO_USER = os.getenv('MONGO_USER', 'admin')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'adminpassword')
    
    # Processing
    WINDOW_DURATION = os.getenv('WINDOW_DURATION', '1 minute')
    WINDOW_SLIDE = os.getenv('WINDOW_SLIDE', '10 seconds')
    WATERMARK_DELAY = os.getenv('WATERMARK_DELAY', '2 minutes')
    BATCH_INTERVAL = os.getenv('BATCH_INTERVAL', '10 seconds')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_mysql_url(cls):
        """Obtiene la URL JDBC de MySQL. Si hay MYSQL_URI, la parsea y convierte a JDBC."""
        # Si hay URI completa, convertirla a formato JDBC
        if cls.MYSQL_URI:
            # Parsear URI: mysql://user:pass@host:port/db?params
            import re
            from urllib.parse import urlparse, parse_qs
            
            try:
                # Parsear la URI completa
                parsed = urlparse(cls.MYSQL_URI)
                
                # Extraer componentes
                host = parsed.hostname
                port = parsed.port if parsed.port else 3306
                database = parsed.path.lstrip('/')  # Remover el / inicial
                
                # Si hay parámetros de query, agregarlos a la URL JDBC
                query_params = parsed.query
                
                # Construir URL JDBC
                jdbc_url = f"jdbc:mysql://{host}:{port}/{database}"
                if query_params:
                    jdbc_url += f"?{query_params}"
                
                return jdbc_url
            except Exception as e:
                logger.warning(f"No se pudo parsear MYSQL_URI: {e}, usando parámetros individuales")
        
        # Si no hay URI o no se pudo parsear, usar parámetros individuales
        return f"jdbc:mysql://{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"
    
    @classmethod
    def get_mysql_credentials(cls):
        """Obtiene las credenciales de MySQL. Si hay MYSQL_URI, las extrae de ahí."""
        if cls.MYSQL_URI:
            from urllib.parse import urlparse
            try:
                parsed = urlparse(cls.MYSQL_URI)
                user = parsed.username
                password = parsed.password
                database = parsed.path.lstrip('/')  # Remover el / inicial
                
                return {
                    'user': user,
                    'password': password,
                    'database': database
                }
            except Exception as e:
                logger.warning(f"No se pudieron extraer credenciales de MYSQL_URI: {e}, usando parámetros individuales")
        
        # Si no hay URI, usar parámetros individuales
        return {
            'user': cls.MYSQL_USER,
            'password': cls.MYSQL_PASSWORD,
            'database': cls.MYSQL_DATABASE
        }
    
    @classmethod
    def get_mongo_uri(cls):
        # Si hay URI de Atlas, usarla directamente
        if cls.MONGO_ATLAS_URI:
            return cls.MONGO_ATLAS_URI
        # Si no, construir URI para MongoDB local
        return f"mongodb://{cls.MONGO_USER}:{cls.MONGO_PASSWORD}@{cls.MONGO_HOST}:{cls.MONGO_PORT}/{cls.MONGO_DATABASE}?authSource=admin"

