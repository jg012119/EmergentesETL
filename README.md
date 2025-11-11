# EmergentesETL - Sistema de Procesamiento de Datos IoT

Sistema ETL completo para procesamiento de datos de sensores IoT (sonido, aire, soterrados) con análisis probabilístico, predicciones y dashboards en tiempo real.

## 📋 Tabla de Contenidos

- [Arquitectura General](#arquitectura-general)
- [Estado Actual](#estado-actual)
- [Pasos de Implementación](#pasos-de-implementación)
- [Configuración de Servicios](#configuración-de-servicios)
- [Esquemas de Datos](#esquemas-de-datos)
- [APIs y Contratos](#apis-y-contratos)
- [Despliegue](#despliegue)
- [Monitoreo](#monitoreo)

---

## 🏗️ Arquitectura General

```
CSV Files → Simulador (Node.js) → Kafka (raw.v1) 
    → Listener/Router (Node.js) → Spark Structured Streaming 
    → MySQL + MongoDB → API Gateway → Frontend React
```

### Componentes Principales

1. **Simulador CSV** (Node.js/TypeScript): Lee CSVs y emite eventos a Kafka cada 10s
2. **Kafka**: Broker con tópicos particionados y Schema Registry
3. **Listener/Router** (Node.js/TypeScript): Consume de Kafka, enriquece/normaliza y envía directamente a Spark
4. **Spark Structured Streaming**: Recibe datos del listener, realiza ETL, análisis probabilístico y predicciones
5. **MySQL**: KPIs y métricas agregadas
6. **MongoDB Atlas**: Documentos detallados y predicciones
7. **API Gateway** (Node.js/Express): REST API + WebSockets
8. **Frontend React**: Dashboards interactivos
9. **Prometheus + Grafana**: Monitoreo y métricas

---

## ✅ Estado Actual

### Implementado

- ✅ Docker Compose completo con Kafka, Zookeeper, Schema Registry, MySQL y MongoDB (`docker-compose.yml`)
- ✅ Esquemas de bases de datos (MySQL y MongoDB)
- ✅ Scripts de inicialización de tópicos Kafka
- ✅ Estructura de carpetas y archivos CSV organizados

### Pendiente de Implementar

- ⏳ Simulador CSV que publica a Kafka
- ⏳ Schema Registry y esquemas JSON/Avro
- ⏳ Listener/Router Node.js para enriquecimiento
- ⏳ Spark Structured Streaming con análisis probabilístico
- ⏳ Bases de datos MySQL y MongoDB
- ⏳ API Gateway con WebSockets
- ⏳ Frontend React con dashboards
- ⏳ Monitoreo con Prometheus/Grafana

---

## 🚀 Pasos de Implementación

### FASE 1: Infraestructura Kafka y Schema Registry

#### Paso 1.1: Actualizar Docker Compose

**Archivo**: `docker-compose.yml` (raíz del proyecto)

Agregar servicios:
- Schema Registry (Confluent)
- Kafka Connect (opcional)
- Zookeeper y Kafka (ya existe, verificar configuración)

**Tareas**:
- [ ] Crear `docker-compose.yml` en raíz con todos los servicios
- [ ] Configurar variables de entorno en `.env`
- [ ] Configurar tópicos Kafka con particiones y retención
- [ ] Verificar conectividad entre servicios

**Tópicos a crear**:
```
em310.distance.raw.v1 (partitions: 3, retention: 7d)
em500.air.raw.v1 (partitions: 3, retention: 7d)
ws302.sound.raw.v1 (partitions: 3, retention: 7d)
```

**Nota**: Los datos enriquecidos se envían directamente a Spark desde el Listener/Router, no se re-publican a Kafka.

#### Paso 1.2: Definir Esquemas JSON Schema

**Archivo**: `schemas/` (nuevo directorio)

Crear esquemas para cada tipo de sensor (solo raw, ya que los datos enriquecidos van directo a Spark):
- `em310-distance-raw.schema.json`
- `em500-air-raw.schema.json`
- `ws302-sound-raw.schema.json`

**Tareas**:
- [ ] Definir esquemas según estructura de eventos (ver sección Esquemas)
- [ ] Registrar esquemas en Schema Registry
- [ ] Validar compatibilidad forward/backward

---

### FASE 2: Simulador CSV → Kafka

#### Paso 2.1: Crear Simulador Node.js

**Directorio**: `simulator/`

**Archivos a crear**:
- `package.json` - Dependencias (kafkajs, csv-parser, dotenv)
- `src/index.ts` - Punto de entrada
- `src/csv-reader.ts` - Lector de CSVs
- `src/kafka-producer.ts` - Productor Kafka
- `src/transformers/` - Transformadores por tipo de sensor
- `.env.example` - Variables de entorno

**Funcionalidad**:
- Leer CSV línea por línea
- Emitir 1 registro cada 10 segundos (modo replay)
- Transformar a formato JSON canónico
- Publicar a tópico correspondiente (`*.raw.v1`)

**Tareas**:
- [ ] Inicializar proyecto Node.js con TypeScript
- [ ] Implementar lector CSV con streaming
- [ ] Implementar productor Kafka con retry logic
- [ ] Crear transformadores para cada tipo de sensor
- [ ] Agregar modo velocidad ajustable (1x, 10x para pruebas)
- [ ] Agregar logging estructurado

**Comandos**:
```bash
cd simulator
npm init -y
npm install kafkajs csv-parser dotenv winston
npm install -D typescript @types/node ts-node
```

---

### FASE 3: Listener/Router (Enriquecimiento)

#### Paso 3.1: Crear Microservicio Node.js

**Directorio**: `listener-router/`

**Archivos a crear**:
- `package.json`
- `src/index.ts` - Consumidor Kafka + Cliente Spark
- `src/enrichers/` - Lógica de enriquecimiento
- `src/validators/` - Validación de datos
- `src/geo-parser.ts` - Parseo de Location (lat/lng)
- `src/spark-client.ts` - Cliente para enviar datos a Spark

**Funcionalidad**:
- Consumir de `*.raw.v1` (Kafka)
- Validar y normalizar:
  - `time` → `ts_utc` (ISO 8601 UTC)
  - `deviceName` → `sensor_id`
  - `Location` → parsear a `geo: { lat, lng }`
- Enriquecer con metadatos
- **Enviar directamente a Spark** (vía HTTP API o socket directo, según implementación de Spark)

**Opciones de integración con Spark**:
1. **HTTP API de Spark**: Spark expone un endpoint REST para recibir datos
2. **Socket directo**: Conexión TCP/UDP directa a Spark
3. **Kafka Streams API**: Usar Kafka Streams como intermediario (no recomendado según requerimiento)

**Tareas**:
- [ ] Crear consumidor Kafka con grupos de consumidores
- [ ] Implementar normalización de timestamps
- [ ] Implementar parser de coordenadas geográficas
- [ ] Agregar validación de rangos razonables
- [ ] Implementar cliente para enviar datos a Spark (HTTP/socket)
- [ ] Implementar manejo de errores y retry logic
- [ ] Agregar métricas (Prometheus)
- [ ] Implementar batching para optimizar envío a Spark

---

### FASE 4: Spark Structured Streaming

#### Paso 4.1: Configurar Spark

**Directorio**: `spark-etl/`

**Archivos a crear**:
- `Dockerfile` - Imagen Spark
- `src/main/scala/` o `src/main/python/` - Código ETL
- `requirements.txt` (si Python) o `build.sbt` (si Scala)
- `config/spark-config.conf`

**Estructura del código**:
```
spark-etl/
├── src/
│   ├── main/
│   │   ├── python/
│   │   │   ├── etl_main.py
│   │   │   ├── processors/
│   │   │   │   ├── sound_processor.py
│   │   │   │   ├── distance_processor.py
│   │   │   │   └── air_processor.py
│   │   │   ├── models/
│   │   │   │   ├── gaussian_estimator.py
│   │   │   │   ├── ewma.py
│   │   │   │   └── ar1_predictor.py
│   │   │   └── sinks/
│   │   │       ├── mysql_sink.py
│   │   │       └── mongodb_sink.py
```

**Funcionalidad**:
1. **Limpieza y validación**:
   - Sonido: validar LAeq/LAI/LAImax (descartar outliers)
   - Distancia: distance ≥ 0, normalizar status
   - Aire: rangos físicos válidos (CO₂, temp, humedad, presión)

2. **Ventaneo**:
   - Ventana deslizante 1 min (slide 10s) para KPIs near-real-time
   - Ventanas 5 min y 1h para baselines

3. **Análisis probabilístico**:
   - Estimación Gaussiana online (μ, σ²) por sensor_id
   - Cálculo de z-scores y p-scores
   - EWMA para suavizado (α=0.3)
   - AR(1) para predicciones (1-3 pasos: 10s, 20s, 30s)

4. **Salidas**:
   - MySQL: agregados por ventana
   - MongoDB: readings_clean + predictions

**Tareas**:
- [ ] Configurar Spark para recibir datos del Listener/Router (HTTP API o socket)
- [ ] Implementar endpoint/servidor para recibir datos enriquecidos del listener
- [ ] Implementar validación y limpieza por tipo
- [ ] Implementar ventaneo con watermark (2 min)
- [ ] Implementar estimación Gaussiana incremental
- [ ] Implementar EWMA
- [ ] Implementar AR(1) para predicciones
- [ ] Implementar escritores a MySQL
- [ ] Implementar escritores a MongoDB
- [ ] Agregar tests unitarios

**Dependencias**:
```python
# requirements.txt
pyspark==3.5.0
pymongo
mysql-connector-python
numpy
scipy
```

---

### FASE 5: Bases de Datos

#### Paso 5.1: MySQL - Esquema de Tablas

**Archivo**: `database/mysql/schema.sql`

**Tablas a crear**:

```sql
-- Métricas de sonido (ventana 1 min)
CREATE TABLE sound_metrics_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    laeq_avg DECIMAL(10,2),
    lai_avg DECIMAL(10,2),
    laimax_max DECIMAL(10,2),
    p95_laeq DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start)
);

-- Métricas de distancia (ventana 1 min)
CREATE TABLE distance_metrics_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    distance_avg DECIMAL(10,2),
    distance_min DECIMAL(10,2),
    distance_max DECIMAL(10,2),
    anomaly_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start)
);

-- Métricas de aire (ventana 1 min)
CREATE TABLE air_metrics_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    co2_avg DECIMAL(10,2),
    temp_avg DECIMAL(10,2),
    rh_avg DECIMAL(10,2),
    press_avg DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start)
);

-- Similar para ventanas 5m y 1h
```

**Tareas**:
- [ ] Crear script de inicialización de esquema
- [ ] Configurar conexión desde Spark
- [ ] Agregar índices optimizados
- [ ] Configurar retención de datos (TTL opcional)

#### Paso 5.2: MongoDB - Colecciones

**Archivo**: `database/mongodb/collections.js` (referencia)

**Colecciones**:

```javascript
// Lecturas limpias de sonido
sound_readings_clean: {
  sensor_id: String,
  ts: ISODate,
  laeq: Number,
  lai: Number,
  laimax: Number,
  status: String,
  addr: String,
  geo: { lat: Number, lng: Number },
  z_score: Number,
  alert_prob: Number,
  window_id: String
}

// Lecturas limpias de distancia
distance_readings_clean: {
  sensor_id: String,
  ts: ISODate,
  distance: Number,
  status: String,
  addr: String,
  geo: { lat: Number, lng: Number },
  anomaly_prob: Number,
  window_id: String
}

// Lecturas limpias de aire
air_readings_clean: {
  sensor_id: String,
  ts: ISODate,
  co2: Number,
  temp: Number,
  rh: Number,
  press: Number,
  statuses: {
    co2: String,
    temp: String,
    rh: String,
    press: String
  },
  alert_prob: Number,
  window_id: String
}

// Predicciones
sound_predictions: {
  sensor_id: String,
  ts_ref: ISODate,
  horizon_s: Number, // 10, 20, 30
  metric: String, // "laeq", "co2", "distance"
  yhat: Number,
  yhat_low: Number,
  yhat_high: Number,
  model: String, // "AR1"
  quality: {
    r2: Number,
    mae: Number
  }
}
```

**Tareas**:
- [ ] Crear índices: `{ sensor_id: 1, ts: 1 }`
- [ ] Configurar TTL para datos antiguos (opcional)
- [ ] Configurar conexión desde Spark
- [ ] Configurar MongoDB Atlas (si se usa cloud)

---

### FASE 6: API Gateway

#### Paso 6.1: Crear API Node.js/Express

**Directorio**: `api-gateway/`

**Archivos a crear**:
- `package.json`
- `src/index.ts` - Servidor Express
- `src/routes/` - Rutas REST
- `src/websocket/` - Servidor WebSocket
- `src/middleware/` - Autenticación JWT, rate limiting
- `src/services/` - Clientes MySQL y MongoDB
- `.env.example`

**Endpoints REST**:

```typescript
// Métricas agregadas (MySQL)
GET /api/metrics/sound?from&to&sensor_id&window=1m|5m|1h
GET /api/metrics/distance?from&to&sensor_id&window=1m|5m|1h
GET /api/metrics/air?from&to&sensor_id&window=1m|5m|1h

// Lecturas detalladas (MongoDB)
GET /api/readings/sound?from&to&sensor_id&limit=100
GET /api/readings/distance?from&to&sensor_id&limit=100
GET /api/readings/air?from&to&sensor_id&limit=100

// Predicciones
GET /api/predictions?metric=laeq|co2|distance&sensor_id&from&horizon=10|20|30

// Autenticación
POST /api/auth/login
POST /api/auth/refresh
```

**WebSocket**:
```
WS /live
Mensaje cada 10s: {
  type: "sound" | "distance" | "air",
  sensor_id: string,
  window: { start, end },
  kpis: { ... },
  predictions: [ { horizon_s, yhat, yhat_low, yhat_high } ]
}
```

**Tareas**:
- [ ] Configurar Express con TypeScript
- [ ] Implementar autenticación JWT (roles: Alcalde, Director DGEyCI, Admin, Usuario)
- [ ] Implementar clientes MySQL y MongoDB
- [ ] Implementar endpoints de métricas
- [ ] Implementar endpoints de lecturas
- [ ] Implementar endpoints de predicciones
- [ ] Implementar servidor WebSocket
- [ ] Agregar rate limiting
- [ ] Agregar logging de auditoría
- [ ] Agregar validación de parámetros
- [ ] Agregar manejo de errores

**Dependencias**:
```json
{
  "express": "^4.18.0",
  "socket.io": "^4.5.0",
  "jsonwebtoken": "^9.0.0",
  "mysql2": "^3.6.0",
  "mongodb": "^6.0.0",
  "express-rate-limit": "^6.8.0",
  "winston": "^3.10.0"
}
```

---

### FASE 7: Frontend React

#### Paso 7.1: Crear Aplicación React

**Directorio**: `frontend/` (ya existe, expandir)

**Estructura**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   │   ├── SoundDashboard.tsx
│   │   │   ├── DistanceDashboard.tsx
│   │   │   └── AirDashboard.tsx
│   │   ├── Charts/
│   │   │   ├── TimeSeriesChart.tsx
│   │   │   ├── PredictionChart.tsx
│   │   │   └── MapView.tsx
│   │   ├── KPICard.tsx
│   │   └── Filters.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── hooks/
│   │   ├── useMetrics.ts
│   │   ├── usePredictions.ts
│   │   └── useWebSocket.ts
│   ├── context/
│   │   └── AuthContext.tsx
│   └── App.tsx
```

**Funcionalidad**:
- Dashboards por tipo de sensor (Aire, Sonido, Soterrados)
- Tarjetas KPI (μ, p95, alert_prob)
- Gráficos de series temporales (últimos 15, 60 min)
- Visualización de predicciones (línea punteada + bandas)
- Mapa con ubicaciones de sensores (si hay geo)
- Filtros: rango de tiempo, sensor, tipo
- Autenticación JWT
- Feature flags por rol

**Tareas**:
- [ ] Configurar React con TypeScript
- [ ] Instalar librerías de gráficos (recharts, chart.js, o similar)
- [ ] Implementar autenticación y gestión de sesión
- [ ] Implementar componentes de dashboard
- [ ] Implementar integración con API REST
- [ ] Implementar integración con WebSocket
- [ ] Implementar visualización de mapas (leaflet o similar)
- [ ] Agregar estilos (CSS Modules, Tailwind, o styled-components)
- [ ] Agregar manejo de errores y loading states
- [ ] Agregar tests (Jest, React Testing Library)

**Dependencias**:
```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.15.0",
  "axios": "^1.5.0",
  "socket.io-client": "^4.5.0",
  "recharts": "^2.8.0",
  "leaflet": "^1.9.4",
  "react-leaflet": "^4.2.1"
}
```

---

### FASE 8: Monitoreo

#### Paso 8.1: Prometheus

**Directorio**: `monitoring/prometheus/`

**Archivos**:
- `prometheus.yml` - Configuración
- `targets/` - Configuración de exporters

**Métricas a recopilar**:
- Kafka: throughput, lag de consumidores, tamaño de tópicos
- Spark: jobs activos, procesamiento de eventos/segundo
- API Gateway: requests/segundo, latencia, errores
- MySQL: conexiones, queries/segundo
- MongoDB: operaciones/segundo, conexiones

**Tareas**:
- [ ] Configurar Prometheus
- [ ] Configurar exporters (Kafka, Node, Spark, MySQL, Mongo)
- [ ] Definir alertas (ej: lag > 1 min, error rate > 5%)

#### Paso 8.2: Grafana

**Directorio**: `monitoring/grafana/`

**Archivos**:
- `dashboards/` - JSON de dashboards

**Dashboards a crear**:
- Kafka: throughput, lag, tamaño de tópicos
- Spark: jobs, procesamiento, latencia end-to-end
- API: requests, latencia, errores
- Bases de datos: queries, conexiones, uso de recursos

**Tareas**:
- [ ] Configurar Grafana
- [ ] Crear dashboards
- [ ] Configurar alertas visuales

---

### FASE 9: Docker Compose Completo

#### Paso 9.1: Integrar Todos los Servicios

**Archivo**: `docker-compose.yml` (raíz)

**Servicios**:
```yaml
services:
  zookeeper:
    # Ya existe
  
  kafka:
    # Ya existe
  
  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    # ...
  
  mysql:
    image: mysql:8.0
    # ...
  
  mongo:
    image: mongo:7.0
    # O usar MongoDB Atlas (cloud)
  
  simulator-csv:
    build: ./simulator
    # ...
  
  listener-router:
    build: ./listener-router
    depends_on:
      - kafka
      - spark-master
    # ...
  
  spark-master:
    build: ./spark-etl
    # Debe exponer un endpoint/servidor para recibir datos del listener-router
    # ...
  
  spark-worker-1:
    # ...
  
  spark-worker-2:
    # ...
  
  api-gateway:
    build: ./api-gateway
    # ...
  
  frontend:
    build: ./frontend
    # ...
  
  prometheus:
    # ...
  
  grafana:
    # ...
```

**Tareas**:
- [ ] Crear Dockerfiles para cada servicio
- [ ] Configurar networks y volúmenes
- [ ] Configurar variables de entorno (.env)
- [ ] Configurar healthchecks
- [ ] Configurar dependencias entre servicios
- [ ] Agregar scripts de inicialización

---

## 📊 Esquemas de Datos

### Evento Raw - Sonido (ws302.sound.raw.v1)

```json
{
  "source": "csv-replay",
  "model": "WS302-915M",
  "ts_raw": "2024-11-03 10:15:20-04:00",
  "ts_utc": "2024-11-03T14:15:20Z",
  "tenant": "<deviceInfo.tenantName>",
  "sensor_id": "<deviceInfo.deviceName>",
  "addr": "<deviceInfo.tags.Address>",
  "geo": "<deviceInfo.tags.Location>",
  "LAeq": 68.4,
  "LAI": 65.2,
  "LAImax": 74.1,
  "status": "<object.status>"
}
```

### Evento Raw - Distancia (em310.distance.raw.v1)

```json
{
  "source": "csv-replay",
  "model": "EM310-UDL-915M",
  "ts_utc": "2024-11-03T14:15:30Z",
  "sensor_id": "<deviceInfo.deviceName>",
  "addr": "<deviceInfo.tags.Address>",
  "geo": "<deviceInfo.tags.Location>",
  "distance": 1.83,
  "status": "<object.status>"
}
```

### Evento Raw - Aire (em500.air.raw.v1)

```json
{
  "source": "csv-replay",
  "model": "EM500-CO2-915M",
  "ts_utc": "2024-11-03T14:15:40Z",
  "sensor_id": "<deviceInfo.deviceName>",
  "addr": "<deviceInfo.tags.Address>",
  "geo": "<deviceInfo.tags.Location>",
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

### Evento ETL (enriquecido) - Enviado a Spark

Los eventos enriquecidos tienen el mismo formato que los raw, pero con las siguientes transformaciones aplicadas por el Listener/Router:
- `ts_utc` normalizado (ISO 8601 UTC)
- `geo` parseado a `{ lat: number, lng: number }` (en lugar de string)
- Campos adicionales de validación

**Nota**: Estos eventos se envían directamente desde el Listener/Router a Spark (no pasan por Kafka).

---

## 🔌 APIs y Contratos

### REST API

**Base URL**: `http://localhost:3000/api`

#### Métricas

```
GET /metrics/sound?from=2024-11-03T00:00:00Z&to=2024-11-03T23:59:59Z&sensor_id=WS302-001&window=1m

Response:
{
  "data": [
    {
      "sensor_id": "WS302-001",
      "window_start": "2024-11-03T10:00:00Z",
      "window_end": "2024-11-03T10:01:00Z",
      "laeq_avg": 68.4,
      "lai_avg": 65.2,
      "laimax_max": 74.1,
      "p95_laeq": 72.3,
      "alert_prob": 0.15,
      "sample_n": 6
    }
  ]
}
```

#### Lecturas

```
GET /readings/sound?from=2024-11-03T00:00:00Z&to=2024-11-03T23:59:59Z&sensor_id=WS302-001&limit=100

Response:
{
  "data": [
    {
      "sensor_id": "WS302-001",
      "ts": "2024-11-03T10:15:20Z",
      "laeq": 68.4,
      "lai": 65.2,
      "laimax": 74.1,
      "status": "OK",
      "addr": "Calle Principal 123",
      "geo": { "lat": -12.0464, "lng": -77.0428 },
      "z_score": 0.5,
      "alert_prob": 0.15
    }
  ],
  "total": 150,
  "limit": 100
}
```

#### Predicciones

```
GET /predictions?metric=laeq&sensor_id=WS302-001&from=2024-11-03T10:00:00Z&horizon=10

Response:
{
  "data": [
    {
      "sensor_id": "WS302-001",
      "ts_ref": "2024-11-03T10:15:20Z",
      "horizon_s": 10,
      "metric": "laeq",
      "yhat": 69.2,
      "yhat_low": 67.8,
      "yhat_high": 70.6,
      "model": "AR1",
      "quality": {
        "r2": 0.85,
        "mae": 1.2
      }
    }
  ]
}
```

### WebSocket

**Endpoint**: `ws://localhost:3000/live`

**Mensaje recibido cada 10s**:
```json
{
  "type": "sound",
  "sensor_id": "WS302-001",
  "window": {
    "start": "2024-11-03T10:15:00Z",
    "end": "2024-11-03T10:16:00Z"
  },
  "kpis": {
    "laeq_avg": 68.4,
    "p95_laeq": 72.3,
    "alert_prob": 0.15
  },
  "predictions": [
    {
      "horizon_s": 10,
      "yhat": 69.2,
      "yhat_low": 67.8,
      "yhat_high": 70.6
    },
    {
      "horizon_s": 20,
      "yhat": 70.1,
      "yhat_low": 68.5,
      "yhat_high": 71.7
    }
  ]
}
```

---

## 🐳 Despliegue

### Requisitos Previos

- Docker y Docker Compose instalados
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para scripts auxiliares)
- Java 11+ (para Spark, si se usa Scala)

### Pasos de Despliegue

1. **Clonar repositorio**:
```bash
git clone <repo-url>
cd EmergentesETL
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con credenciales y configuraciones
```

3. **Iniciar servicios**:
```bash
docker-compose up -d
```

4. **Verificar servicios**:
```bash
docker-compose ps
```

5. **Inicializar bases de datos**:
```bash
# MySQL
docker-compose exec mysql mysql -u root -p < database/mysql/schema.sql

# MongoDB (si local)
docker-compose exec mongo mongosh < database/mongodb/init.js
```

6. **Iniciar simulador**:
```bash
cd simulator
npm install
npm run start
```

7. **Verificar flujo**:
- Verificar que Kafka recibe mensajes
- Verificar que Spark procesa datos
- Verificar que MySQL y MongoDB reciben datos
- Acceder a frontend: http://localhost:3001
- Acceder a Grafana: http://localhost:3002

---

## 📈 Monitoreo

### Métricas Clave

- **Throughput**: Eventos procesados por segundo
- **Latencia end-to-end**: Tiempo desde CSV hasta dashboard
- **Lag de consumidores**: Retraso en procesamiento
- **Error rate**: Porcentaje de errores
- **Resource usage**: CPU, memoria, disco

### Alertas

- Lag > 1 minuto
- Error rate > 5%
- CPU > 80%
- Memoria > 90%
- Kafka broker down
- Spark job failed

---

## 🔒 Seguridad

### Autenticación

- JWT tokens con expiración
- Refresh tokens
- Roles: Alcalde, Director DGEyCI, Admin, Usuario

### Autorización

- Endpoints de solo lectura para usuarios
- Endpoints de configuración solo para Admin
- Logs de auditoría

### Variables de Entorno Sensibles

- Credenciales de bases de datos
- JWT secrets
- MongoDB Atlas connection strings
- Kafka bootstrap servers

**NUNCA** commitear `.env` al repositorio.

---

## 🧪 Pruebas

### Pruebas de Carga

El simulador puede acelerar la velocidad de emisión:
```bash
# 1x velocidad (normal)
npm run start

# 10x velocidad (stress test)
SPEED_MULTIPLIER=10 npm run start
```

### Pruebas Unitarias

```bash
# Simulador
cd simulator && npm test

# Listener/Router
cd listener-router && npm test

# API Gateway
cd api-gateway && npm test

# Frontend
cd frontend && npm test
```

---

## 📝 Notas de Implementación

### Orden Recomendado de Implementación

1. **Fase 1**: Infraestructura Kafka (docker-compose, tópicos, schemas)
2. **Fase 2**: Simulador CSV → Kafka
3. **Fase 3**: Listener/Router (enriquecimiento y envío directo a Spark)
4. **Fase 4**: Spark ETL básico (recibe datos del listener, sin análisis probabilístico)
5. **Fase 5**: Bases de datos (MySQL y MongoDB)
6. **Fase 6**: API Gateway básico (REST sin WebSocket)
7. **Fase 7**: Frontend básico (dashboards estáticos)
8. **Fase 8**: Análisis probabilístico en Spark
9. **Fase 9**: Predicciones en Spark
10. **Fase 10**: WebSocket en API Gateway
11. **Fase 11**: Integración completa frontend
12. **Fase 12**: Monitoreo (Prometheus + Grafana)

### Consideraciones

- **Escalabilidad**: Kafka particionado permite paralelismo; el listener puede escalar horizontalmente
- **Resiliencia**: Implementar retry logic en el listener para envío a Spark; dead letter queues en Kafka
- **Performance**: Comunicación directa listener→Spark reduce latencia; usar batching para optimizar envío
- **Mantenibilidad**: Código modular y bien documentado; separación clara de responsabilidades
- **Observabilidad**: Logging estructurado y métricas; monitorear latencia end-to-end (Kafka→Listener→Spark)
- **Integración Listener-Spark**: Definir claramente el protocolo de comunicación (HTTP REST, socket, etc.)

---

## 📚 Recursos

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

---

## 👥 Contribución

1. Crear branch desde `main`
2. Implementar cambios
3. Agregar tests
4. Crear Pull Request

---

## 📄 Licencia

[Especificar licencia]

---

## 🆘 Soporte

Para problemas o preguntas, crear un issue en el repositorio.
