# FASE 3: Listener/Router (Enriquecimiento) - Completada ✅

## Resumen

Se ha completado la implementación del microservicio Listener/Router que consume eventos de Kafka, los enriquece/normaliza y los envía directamente a Spark.

## Archivos Creados

### Estructura del Proyecto

```
listener-router/
├── src/
│   ├── index.ts                    # Punto de entrada principal
│   ├── config.ts                   # Configuración desde variables de entorno
│   ├── logger.ts                   # Logger con Winston
│   ├── kafka-consumer.ts           # Consumidor Kafka con grupos
│   ├── data-processor.ts           # Procesador principal de datos
│   ├── spark-client.ts             # Cliente HTTP para Spark (con batching)
│   ├── geo-parser.ts               # Parser de coordenadas geográficas
│   ├── enrichers/
│   │   ├── timestamp-enricher.ts   # Normalización de timestamps
│   │   └── index.ts
│   └── validators/
│       ├── range-validator.ts       # Validación de rangos razonables
│       └── index.ts
├── package.json
├── tsconfig.json
├── .gitignore
├── README.md
└── ENV_CONFIG.md
```

## Funcionalidades Implementadas

### ✅ Consumidor Kafka
- Conexión con grupos de consumidores
- Suscripción a múltiples tópicos (`*.raw.v1`)
- Manejo de errores y reconexión automática
- Logging detallado de mensajes recibidos

### ✅ Enriquecimiento de Datos
- **Normalización de timestamps**: Convierte cualquier formato a ISO 8601 UTC
- **Parser de coordenadas**: Parsea strings de ubicación a `{ lat, lng }`
- **Normalización de sensor_id**: Usa `deviceName` o `tenant` como fallback

### ✅ Validación de Rangos
- **Sonido**: LAeq, LAI, LAImax (0-200 dB)
- **Distancia**: distance (0-100 m)
- **Aire**: CO₂ (0-10000 ppm), temp (-50-100°C), humedad (0-100%), presión (0-2000 hPa)
- Marca eventos con errores de validación pero no los descarta

### ✅ Cliente Spark
- Envío individual de eventos
- **Batching**: Agrupa eventos antes de enviar (tamaño y timeout configurables)
- **Retry logic**: Reintentos con delay exponencial
- Manejo de errores y logging

### ✅ Procesamiento de Datos
- Procesa eventos de los 3 tipos de sensores
- Enriquece con metadatos
- Valida rangos según tipo de sensor
- Prepara eventos para Spark

## Instalación y Uso

### 1. Instalar Dependencias

```bash
cd listener-router
npm install
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` (ver `ENV_CONFIG.md`):

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_GROUP_ID=listener-router-group
KAFKA_CLIENT_ID=emergent-etl-listener-router

SPARK_HOST=localhost
SPARK_PORT=8080
SPARK_ENDPOINT=/api/data
SPARK_PROTOCOL=http
SPARK_TIMEOUT=30000

BATCH_SIZE=10
BATCH_TIMEOUT=5000
MAX_RETRIES=3
RETRY_DELAY=1000

LOG_LEVEL=info
```

### 3. Ejecutar Listener/Router

**Modo desarrollo:**
```bash
npm run dev
```

**Modo producción:**
```bash
npm run build
npm start
```

## Tópicos Consumidos

- `em310.distance.raw.v1` - Sensores de distancia (EM310)
- `em500.air.raw.v1` - Sensores de aire (EM500)
- `ws302.sound.raw.v1` - Sensores de sonido (WS302)

## Batching

Los eventos se agrupan en batches antes de enviarse a Spark:

- **Tamaño**: 10 eventos por defecto (configurable)
- **Timeout**: 5 segundos por defecto (configurable)

El batch se envía cuando:
1. Se alcanza el tamaño máximo (`BATCH_SIZE`)
2. Se alcanza el timeout (`BATCH_TIMEOUT`)

## Retry Logic

Si falla el envío a Spark:
- Se reintenta hasta 3 veces (configurable con `MAX_RETRIES`)
- Delay exponencial entre reintentos
- Logs detallados de errores

## Formato de Eventos Enriquecidos

Los eventos enviados a Spark tienen el mismo formato que los raw, pero con:

```json
{
  "source": "csv-replay",
  "model": "WS302-915M",
  "ts_utc": "2024-11-03T14:15:20Z",  // Normalizado a ISO 8601 UTC
  "sensor_id": "WS302-001",           // Normalizado
  "addr": "Calle Principal 123",
  "geo": {                            // Parseado de string a objeto
    "lat": -12.0464,
    "lng": -77.0428
  },
  "LAeq": 68.4,
  "LAI": 65.2,
  "LAImax": 74.1,
  "status": "OK",
  "_validated": true,                 // Campo agregado
  "_validation_errors": []            // Campo agregado (si hay errores)
}
```

## Nota Importante sobre Spark

Este servicio espera que Spark tenga un endpoint HTTP disponible en:
- `http://localhost:8080/api/data` (para eventos individuales)
- `http://localhost:8080/api/data/batch` (para batches)

**Si Spark aún no está implementado**, este servicio puede correr pero los eventos fallarán al enviarse. Los logs mostrarán los errores, pero el servicio seguirá funcionando y procesando eventos.

Cuando implementes Spark en la FASE 4, asegúrate de crear estos endpoints.

## Verificación

### Verificar que consume de Kafka

Los logs mostrarán:
```
Mensaje recibido de ws302.sound.raw.v1
Evento procesado y enviado a Spark
```

### Verificar estadísticas del consumidor

```bash
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group listener-router-group
```

## Próximos Pasos

**FASE 4**: Spark Structured Streaming
- Crear servidor HTTP para recibir datos del listener
- Implementar ETL y análisis probabilístico
- Escribir a MySQL y MongoDB

## Estado de la FASE 3

✅ **COMPLETADA**

- [x] Proyecto Node.js con TypeScript inicializado
- [x] Consumidor Kafka con grupos implementado
- [x] Normalización de timestamps implementada
- [x] Parser de coordenadas geográficas implementado
- [x] Validación de rangos razonables implementada
- [x] Cliente Spark con HTTP API implementado
- [x] Batching para optimizar envío implementado
- [x] Retry logic implementado
- [x] Documentación completa

