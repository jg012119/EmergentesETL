# Iniciar Sistema con Kafka

## Arquitectura

```
Simulador → Kafka (raw) → Listener/Router → Spark → Kafka (processed) → db-writer → MySQL/MongoDB
```

## Pasos para Iniciar

### 1. Verificar que Kafka está corriendo

```powershell
docker ps | Select-String "kafka"
```

Si no está corriendo:
```powershell
docker-compose up -d kafka zookeeper schema-registry
```

### 2. Verificar tópicos Kafka

```powershell
.\scripts\init-kafka-topics.ps1
```

Deberías ver:
- `em310.distance.raw.v1`
- `em500.air.raw.v1`
- `ws302.sound.raw.v1`
- `processed.metrics.v1` ✅
- `processed.readings.v1` ✅

### 3. Configurar variables de entorno

#### spark-etl/.env
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
MYSQL_URI=mysql://user:pass@host:port/db
MONGO_ATLAS_URI=mongodb+srv://...
HTTP_PORT=8082
LOG_LEVEL=INFO
```

#### db-writer/.env
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
MYSQL_URI=mysql://user:pass@host:port/db
MONGO_ATLAS_URI=mongodb+srv://...
LOG_LEVEL=info
```

### 4. Iniciar db-writer

```powershell
cd db-writer
npm run dev
```

Deberías ver:
```
=== Iniciando Servicio DB Writer ===
Modo: Consumidor Kafka
Tópicos: processed.metrics.v1, processed.readings.v1
✓ Servicio DB Writer iniciado correctamente
Consumiendo mensajes de Kafka y escribiendo a MySQL y MongoDB...
```

### 5. Iniciar Spark

En otra terminal:
```powershell
cd spark-etl
python src/main/python/etl_main.py
```

Deberías ver:
```
=== Iniciando Spark ETL ===
Spark session creada con paquetes: org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0
Procesadores y Kafka sink inicializados (Spark -> Kafka -> db-writer -> DBs)
```

### 6. Iniciar Listener/Router (opcional - si quieres procesar datos nuevos)

```powershell
cd listener-router
npm run dev
```

### 7. Iniciar Simulador (opcional - si quieres generar datos nuevos)

```powershell
cd simulator
npm run dev
```

## Verificación

### Verificar que Spark está escribiendo a Kafka

```powershell
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic processed.metrics.v1 --from-beginning --max-messages 5
```

### Verificar que db-writer está consumiendo

Revisar logs de db-writer:
```
✓ Métrica escrita a MySQL: sound_metrics_1m
✓ Lectura escrita a MongoDB: sound_readings_clean
```

### Verificar datos en las bases de datos

**MySQL:**
```sql
SELECT * FROM sound_metrics_1m LIMIT 10;
SELECT * FROM air_metrics_1m LIMIT 10;
SELECT * FROM distance_metrics_1m LIMIT 10;
```

**MongoDB:**
```javascript
db.sound_readings_clean.find().limit(10).pretty();
db.air_readings_clean.find().limit(10).pretty();
db.distance_readings_clean.find().limit(10).pretty();
```

## Troubleshooting

### db-writer no consume mensajes

1. Verificar que Kafka está corriendo: `docker ps | Select-String "kafka"`
2. Verificar que los tópicos existen: `docker exec kafka kafka-topics --list --bootstrap-server localhost:9092`
3. Verificar logs de db-writer para errores de conexión

### Spark no escribe a Kafka

1. Verificar `KAFKA_BOOTSTRAP_SERVERS` en `spark-etl/.env`
2. Verificar que el conector Kafka está descargado (Spark lo descarga automáticamente)
3. Verificar logs de Spark para errores

### No hay datos en las bases de datos

1. Verificar que db-writer está consumiendo (logs)
2. Verificar que Spark está procesando datos (logs)
3. Verificar conexiones a MySQL y MongoDB (logs de db-writer)

## Monitoreo

### Ver mensajes en Kafka

```powershell
# Métricas
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic processed.metrics.v1 --from-beginning

# Lecturas
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic processed.readings.v1 --from-beginning
```

### Ver estadísticas de tópicos

```powershell
docker exec kafka kafka-topics --describe --bootstrap-server localhost:9092 --topic processed.metrics.v1
docker exec kafka kafka-topics --describe --bootstrap-server localhost:9092 --topic processed.readings.v1
```

