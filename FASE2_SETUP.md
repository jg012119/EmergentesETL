# FASE 2: Simulador CSV → Kafka - Completada ✅

## Resumen

Se ha completado la implementación del simulador CSV que lee archivos y publica eventos a Kafka.

## Archivos Creados

### Estructura del Proyecto

```
simulator/
├── src/
│   ├── index.ts                    # Punto de entrada principal
│   ├── config.ts                   # Configuración desde variables de entorno
│   ├── logger.ts                   # Logger con Winston
│   ├── csv-reader.ts               # Lector de CSVs con streaming
│   ├── kafka-producer.ts          # Productor Kafka con retry logic
│   └── transformers/
│       ├── base-transformer.ts     # Clase base para transformadores
│       ├── sound-transformer.ts     # Transformador para WS302 (sonido)
│       ├── distance-transformer.ts  # Transformador para EM310 (distancia)
│       ├── air-transformer.ts      # Transformador para EM500 (aire)
│       └── index.ts                # Factory para obtener transformador
├── package.json                    # Dependencias y scripts
├── tsconfig.json                   # Configuración TypeScript
├── .gitignore                      # Archivos ignorados
├── README.md                       # Documentación del simulador
└── ENV_CONFIG.md                   # Documentación de variables de entorno
```

## Funcionalidades Implementadas

### ✅ Lector CSV
- Carga completa del CSV en memoria
- Streaming para archivos grandes
- Manejo de errores
- Reinicio automático al finalizar

### ✅ Productor Kafka
- Conexión con retry logic
- Envío idempotente
- Manejo de errores y logging
- Desconexión limpia

### ✅ Transformadores
- **SoundTransformer**: Transforma datos de WS302-915M (sonido)
  - Tópico: `ws302.sound.raw.v1`
  - Campos: LAeq, LAI, LAImax, status, tenant
  
- **DistanceTransformer**: Transforma datos de EM310-UDL-915M (distancia)
  - Tópico: `em310.distance.raw.v1`
  - Campos: distance, status
  
- **AirTransformer**: Transforma datos de EM500-CO2-915M (aire)
  - Tópico: `em500.air.raw.v1`
  - Campos: co2, temperature, humidity, pressure, statuses

### ✅ Modo Replay
- Emite 1 evento cada 10 segundos (configurable)
- Velocidad ajustable (SPEED_MULTIPLIER)
- Procesa múltiples archivos CSV simultáneamente
- Reinicio automático al finalizar cada archivo

### ✅ Logging
- Logging estructurado con Winston
- Niveles configurables (debug, info, warn, error)
- Logs a consola y archivos (combined.log, error.log)

## Instalación y Uso

### 1. Instalar Dependencias

```bash
cd simulator
npm install
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` (ver `ENV_CONFIG.md`):

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
CSV_DIRECTORY=../data/csv
SPEED_MULTIPLIER=1
INTERVAL_MS=10000
LOG_LEVEL=info
```

### 3. Ejecutar Simulador

**Modo desarrollo (con watch):**
```bash
npm run dev
```

**Modo producción:**
```bash
npm run build
npm start
```

**Modo rápido (10x velocidad para pruebas):**
```bash
SPEED_MULTIPLIER=10 npm run dev
```

## Detección Automática de Tipo de Sensor

El simulador detecta automáticamente el tipo de sensor basándose en el nombre del archivo:

- Archivos con **WS302** o **SONIDO** → Transformador de sonido
- Archivos con **EM310**, **SOTERRADOS** o **DISTANCE** → Transformador de distancia
- Archivos con **EM500**, **CO2** o **AIRE** → Transformador de aire

## Formato de Eventos

Los eventos se transforman al formato JSON canónico según el tipo:

### Sonido (ws302.sound.raw.v1)
```json
{
  "source": "csv-replay",
  "model": "WS302-915M",
  "ts_raw": "2024-11-03 10:15:20-04:00",
  "ts_utc": "2024-11-03T14:15:20Z",
  "tenant": "...",
  "sensor_id": "...",
  "addr": "...",
  "geo": "...",
  "LAeq": 68.4,
  "LAI": 65.2,
  "LAImax": 74.1,
  "status": "..."
}
```

### Distancia (em310.distance.raw.v1)
```json
{
  "source": "csv-replay",
  "model": "EM310-UDL-915M",
  "ts_utc": "2024-11-03T14:15:30Z",
  "sensor_id": "...",
  "addr": "...",
  "geo": "...",
  "distance": 1.83,
  "status": "..."
}
```

### Aire (em500.air.raw.v1)
```json
{
  "source": "csv-replay",
  "model": "EM500-CO2-915M",
  "ts_utc": "2024-11-03T14:15:40Z",
  "sensor_id": "...",
  "addr": "...",
  "geo": "...",
  "co2": 872,
  "co2_status": "OK",
  "temperature": 24.3,
  "temperature_status": "OK",
  "humidity": 48.2,
  "humidity_status": "OK",
  "pressure": 842.7,
  "pressure_status": "OK"
}
```

## Verificación

### Verificar que Kafka recibe mensajes

```bash
# Consumir mensajes de un tópico
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ws302.sound.raw.v1 \
  --from-beginning
```

### Verificar estadísticas de tópicos

```bash
docker exec kafka kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic ws302.sound.raw.v1
```

## Próximos Pasos

**FASE 3**: Listener/Router (Node.js)
- Consumir de Kafka (`*.raw.v1`)
- Enriquecer y normalizar datos
- Enviar directamente a Spark

## Estado de la FASE 2

✅ **COMPLETADA**

- [x] Proyecto Node.js con TypeScript inicializado
- [x] Lector CSV con streaming implementado
- [x] Productor Kafka con retry logic implementado
- [x] Transformadores para cada tipo de sensor creados
- [x] Modo velocidad ajustable implementado
- [x] Logging estructurado configurado
- [x] Documentación completa

