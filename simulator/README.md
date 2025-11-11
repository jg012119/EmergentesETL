# Simulador CSV → Kafka

Simulador que lee archivos CSV y publica eventos a Kafka en modo replay (1 evento cada 10 segundos).

## Instalación

```bash
npm install
```

## Configuración

Copia `.env.example` a `.env` y ajusta las variables según tu entorno:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
CSV_DIRECTORY=../data/csv
SPEED_MULTIPLIER=1
INTERVAL_MS=10000
LOG_LEVEL=info
```

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

### Modo Rápido (para pruebas)

```bash
SPEED_MULTIPLIER=10 npm run dev
```

Esto enviará eventos 10 veces más rápido (cada 1 segundo en lugar de cada 10 segundos).

## Archivos CSV Soportados

El simulador detecta automáticamente el tipo de sensor basándose en el nombre del archivo:

- **WS302** o **SONIDO** → `ws302.sound.raw.v1`
- **EM310** o **SOTERRADOS** o **DISTANCE** → `em310.distance.raw.v1`
- **EM500** o **CO2** o **AIRE** → `em500.air.raw.v1`

## Estructura

```
simulator/
├── src/
│   ├── index.ts              # Punto de entrada
│   ├── config.ts             # Configuración
│   ├── logger.ts              # Logger (Winston)
│   ├── csv-reader.ts          # Lector de CSVs
│   ├── kafka-producer.ts      # Productor Kafka
│   └── transformers/          # Transformadores por tipo
│       ├── base-transformer.ts
│       ├── sound-transformer.ts
│       ├── distance-transformer.ts
│       ├── air-transformer.ts
│       └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

## Logs

Los logs se guardan en:
- `combined.log` - Todos los logs
- `error.log` - Solo errores

