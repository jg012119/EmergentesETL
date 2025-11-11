# Listener/Router - Enriquecimiento y Envío a Spark

Microservicio que consume eventos de Kafka, los enriquece/normaliza y los envía directamente a Spark.

## Funcionalidad

1. **Consume de Kafka**: Lee eventos de los tópicos `*.raw.v1`
2. **Enriquece datos**:
   - Normaliza timestamps a ISO 8601 UTC
   - Parsea coordenadas geográficas (lat/lng)
   - Valida rangos razonables de valores
3. **Envía a Spark**: Envía eventos enriquecidos directamente a Spark (HTTP API)

## Instalación

```bash
npm install
```

## Configuración

Copia `ENV_CONFIG.md` para ver las variables de entorno necesarias y crea un archivo `.env`.

## Uso

### Desarrollo

```bash
npm run dev
```

### Producción

```bash
npm run build
npm start
```

## Tópicos Consumidos

- `em310.distance.raw.v1` - Datos de sensores de distancia
- `em500.air.raw.v1` - Datos de sensores de aire
- `ws302.sound.raw.v1` - Datos de sensores de sonido

## Estructura

```
listener-router/
├── src/
│   ├── index.ts              # Punto de entrada
│   ├── config.ts             # Configuración
│   ├── logger.ts              # Logger
│   ├── kafka-consumer.ts      # Consumidor Kafka
│   ├── data-processor.ts      # Procesador de datos
│   ├── spark-client.ts         # Cliente Spark
│   ├── geo-parser.ts          # Parser de coordenadas
│   ├── enrichers/             # Enriquecimiento
│   │   └── timestamp-enricher.ts
│   └── validators/             # Validación
│       └── range-validator.ts
├── package.json
├── tsconfig.json
└── README.md
```

## Batching

Los eventos se agrupan en batches antes de enviarse a Spark:
- **Tamaño**: Por defecto 10 eventos (configurable con `BATCH_SIZE`)
- **Timeout**: Por defecto 5 segundos (configurable con `BATCH_TIMEOUT`)

El batch se envía cuando:
- Se alcanza el tamaño máximo
- Se alcanza el timeout

## Retry Logic

Si falla el envío a Spark:
- Se reintenta hasta `MAX_RETRIES` veces
- Delay exponencial entre reintentos
- Logs de errores para debugging

## Nota sobre Spark

Este servicio espera que Spark tenga un endpoint HTTP disponible en:
- `http://localhost:8080/api/data` (eventos individuales)
- `http://localhost:8080/api/data/batch` (batches)

Si Spark aún no está implementado, este servicio puede correr pero los eventos fallarán al enviarse. Los logs mostrarán los errores.

