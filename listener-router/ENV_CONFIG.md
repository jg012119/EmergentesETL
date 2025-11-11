# Configuración de Variables de Entorno

Crea un archivo `.env` en la carpeta `listener-router/` con las siguientes variables:

```env
# Configuración de Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_GROUP_ID=listener-router-group
KAFKA_CLIENT_ID=emergent-etl-listener-router

# Configuración de Spark
SPARK_HOST=localhost
SPARK_PORT=8080
SPARK_ENDPOINT=/api/data
SPARK_PROTOCOL=http
SPARK_TIMEOUT=30000

# Configuración de procesamiento
BATCH_SIZE=10
BATCH_TIMEOUT=5000
MAX_RETRIES=3
RETRY_DELAY=1000

# Configuración de logging
LOG_LEVEL=info
```

## Descripción de Variables

- **KAFKA_BOOTSTRAP_SERVERS**: Dirección del broker de Kafka
- **KAFKA_GROUP_ID**: ID del grupo de consumidores
- **KAFKA_CLIENT_ID**: Identificador del cliente Kafka
- **SPARK_HOST**: Host donde está corriendo Spark
- **SPARK_PORT**: Puerto del servidor Spark
- **SPARK_ENDPOINT**: Endpoint para enviar datos a Spark
- **SPARK_PROTOCOL**: Protocolo (http o https)
- **SPARK_TIMEOUT**: Timeout para requests a Spark (ms)
- **BATCH_SIZE**: Tamaño del batch antes de enviar a Spark
- **BATCH_TIMEOUT**: Tiempo máximo antes de enviar batch (ms)
- **MAX_RETRIES**: Número máximo de reintentos
- **RETRY_DELAY**: Delay entre reintentos (ms)
- **LOG_LEVEL**: Nivel de logging (debug, info, warn, error)

