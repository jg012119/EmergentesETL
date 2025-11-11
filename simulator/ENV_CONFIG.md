# Configuración de Variables de Entorno

Crea un archivo `.env` en la carpeta `simulator/` con las siguientes variables:

```env
# Configuración de Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_CLIENT_ID=emergent-etl-simulator

# Configuración de CSVs
CSV_DIRECTORY=../data/csv

# Configuración de simulación
SPEED_MULTIPLIER=1
INTERVAL_MS=10000

# Configuración de logging
LOG_LEVEL=info
```

## Descripción de Variables

- **KAFKA_BOOTSTRAP_SERVERS**: Dirección del broker de Kafka (puerto externo)
- **KAFKA_CLIENT_ID**: Identificador del cliente Kafka
- **CSV_DIRECTORY**: Ruta relativa o absoluta al directorio con los archivos CSV
- **SPEED_MULTIPLIER**: Multiplicador de velocidad (1 = normal, 10 = 10x más rápido)
- **INTERVAL_MS**: Intervalo en milisegundos entre eventos (por defecto 10000 = 10 segundos)
- **LOG_LEVEL**: Nivel de logging (debug, info, warn, error)

