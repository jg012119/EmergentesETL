# Configuración de Variables de Entorno

Crea un archivo `.env` en la carpeta `spark-etl/` con las siguientes variables:

```env
# Configuración de Spark
SPARK_MASTER=local[*]
SPARK_APP_NAME=EmergentETL
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=2g

# Configuración del servidor HTTP
HTTP_HOST=0.0.0.0
HTTP_PORT=8082
HTTP_ENDPOINT=/api/data

# Configuración de MySQL
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=emergent_etl
MYSQL_USER=etl_user
MYSQL_PASSWORD=etl_password

# Configuración de MongoDB
# Opción 1: MongoDB Atlas (recomendado) - Solo necesitas la URI
MONGO_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/emergent_etl?retryWrites=true&w=majority

# Opción 2: MongoDB Local (solo si no usas Atlas)
# MONGO_HOST=mongo
# MONGO_PORT=27017
# MONGO_DATABASE=emergent_etl
# MONGO_USER=admin
# MONGO_PASSWORD=adminpassword

# Configuración de procesamiento
WINDOW_DURATION=1 minute
WINDOW_SLIDE=10 seconds
WATERMARK_DELAY=2 minutes
BATCH_INTERVAL=10 seconds

# Configuración de logging
LOG_LEVEL=INFO
```

## Descripción de Variables

- **SPARK_MASTER**: URL del master de Spark (local[*] para modo local)
- **SPARK_APP_NAME**: Nombre de la aplicación Spark
- **SPARK_DRIVER_MEMORY**: Memoria del driver
- **SPARK_EXECUTOR_MEMORY**: Memoria del executor
- **HTTP_HOST**: Host del servidor HTTP (0.0.0.0 para todas las interfaces)
- **HTTP_PORT**: Puerto del servidor HTTP
- **HTTP_ENDPOINT**: Endpoint para recibir datos
- **MYSQL_*****: Configuración de conexión a MySQL
- **MONGO_*****: Configuración de conexión a MongoDB
- **WINDOW_DURATION**: Duración de la ventana (ej: "1 minute")
- **WINDOW_SLIDE**: Intervalo de deslizamiento (ej: "10 seconds")
- **WATERMARK_DELAY**: Delay del watermark (ej: "2 minutes")
- **LOG_LEVEL**: Nivel de logging (DEBUG, INFO, WARN, ERROR)

