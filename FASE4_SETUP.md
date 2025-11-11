# FASE 4: Spark Structured Streaming - Completada ✅ (Básica)

## Resumen

Se ha completado la implementación básica de Spark ETL que recibe datos del Listener/Router, realiza procesamiento y está preparado para escribir a MySQL y MongoDB.

## Archivos Creados

### Estructura del Proyecto

```
spark-etl/
├── src/main/python/
│   ├── etl_main.py              # Aplicación principal
│   ├── config.py                # Configuración desde variables de entorno
│   ├── http_server.py           # Servidor HTTP Flask para recibir datos
│   ├── processors/              # Procesadores por tipo de sensor
│   │   ├── __init__.py
│   │   ├── base_processor.py    # Clase base abstracta
│   │   ├── sound_processor.py   # Procesador para WS302 (sonido)
│   │   ├── distance_processor.py # Procesador para EM310 (distancia)
│   │   └── air_processor.py      # Procesador para EM500 (aire)
│   └── sinks/                   # Escritores a bases de datos
│       ├── __init__.py
│       ├── mysql_sink.py        # Escritor a MySQL
│       └── mongodb_sink.py      # Escritor a MongoDB
├── Dockerfile                   # Imagen Docker con Java y Python
├── requirements.txt             # Dependencias Python
├── .gitignore
├── README.md
└── ENV_CONFIG.md
```

## Funcionalidades Implementadas

### ✅ Servidor HTTP
- Endpoint `/api/data` para eventos individuales
- Endpoint `/api/data/batch` para batches
- Health check y estadísticas
- Cola en memoria para eventos (events_queue)

### ✅ Procesadores por Tipo de Sensor
- **SoundProcessor**: Procesa datos de sonido (WS302)
  - Validación: LAeq, LAI, LAImax (0-200 dB)
  - Métricas: avg(LAeq), avg(LAI), max(LAImax), p95(LAeq)
  
- **DistanceProcessor**: Procesa datos de distancia (EM310)
  - Validación: distance (0-100 m)
  - Métricas: avg, min, max(distance)
  
- **AirProcessor**: Procesa datos de aire (EM500)
  - Validación: CO₂ (0-10000 ppm), temp (-50-100°C), humedad (0-100%), presión (0-2000 hPa)
  - Métricas: avg(co2, temp, humidity, pressure)

### ✅ Ventaneo
- Ventana deslizante configurable (por defecto 1 min)
- Slide configurable (por defecto 10s)
- Watermark de 2 minutos para manejar datos tardíos

### ✅ Escritores a Bases de Datos
- **MySQLSink**: Escribe métricas agregadas a MySQL
- **MongoDBSink**: Escribe lecturas limpias a MongoDB
- Fallback a PyMongo si el conector Spark no está disponible

### ⏳ Pendiente (Fase Avanzada)
- Modelos probabilísticos (Gaussiano, EWMA, AR1)
- Cálculo de z-scores y p-scores
- Predicciones con AR(1)

## Instalación y Uso

### 1. Instalar Dependencias

```bash
cd spark-etl
pip install -r requirements.txt
```

**Nota**: Necesitas tener Java 11+ instalado para Spark.

### 2. Configurar Variables de Entorno

Crear archivo `.env` (ver `ENV_CONFIG.md`):

```env
SPARK_MASTER=local[*]
HTTP_HOST=0.0.0.0
HTTP_PORT=8080
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=emergent_etl
MYSQL_USER=etl_user
MYSQL_PASSWORD=etl_password
# Opción 1: MongoDB Atlas (solo URI)
MONGO_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/emergent_etl?retryWrites=true&w=majority

# Opción 2: MongoDB Local (solo si no usas Atlas)
# MONGO_HOST=mongo
# MONGO_PORT=27017
# MONGO_DATABASE=emergent_etl
# MONGO_USER=admin
# MONGO_PASSWORD=adminpassword
```

### 3. Ejecutar Spark ETL

```bash
python src/main/python/etl_main.py
```

Esto iniciará:
- Servidor HTTP en el puerto 8080
- Procesamiento de eventos en background

## Endpoints HTTP

### Recibir Evento Individual
```bash
POST http://localhost:8080/api/data
Content-Type: application/json

{
  "source": "csv-replay",
  "model": "WS302-915M",
  "ts_utc": "2024-11-03T14:15:20Z",
  "sensor_id": "WS302-001",
  "LAeq": 68.4,
  ...
}
```

### Recibir Batch
```bash
POST http://localhost:8080/api/data/batch
Content-Type: application/json

{
  "events": [
    { ... },
    { ... }
  ]
}
```

### Health Check
```bash
GET http://localhost:8080/health
```

## Flujo de Procesamiento

1. **Recepción**: El servidor HTTP recibe eventos del Listener/Router
2. **Cola**: Los eventos se almacenan en `events_queue` (memoria)
3. **Separación**: Se separan eventos por tipo de sensor
4. **Validación**: Se validan y limpian según rangos razonables
5. **Ventaneo**: Se aplican ventanas deslizantes
6. **Agregación**: Se calculan métricas agregadas
7. **Escritura**: Se escriben a MySQL (métricas) y MongoDB (lecturas)

## Notas Importantes

### Escritura a Bases de Datos

Los escritores están implementados pero **comentados** en `etl_main.py` porque:
- Requieren conectores JDBC para MySQL (incluido en Spark)
- Requieren conector MongoDB para Spark (puede necesitar instalación adicional)

Para habilitar la escritura, descomenta las líneas en `etl_main.py`:
```python
mysql_sink.write_metrics(metrics, "sound_metrics_1m")
mongo_sink.write_readings(df, "sound_readings_clean")
```

### Cola en Memoria

Actualmente usa una cola en memoria (`events_queue`). En producción, considera usar:
- Redis
- RabbitMQ
- Kafka (otro tópico)

### Modelos Probabilísticos

Los modelos probabilísticos (Gaussiano, EWMA, AR1) se implementarán en una fase posterior cuando se necesiten las predicciones.

## Docker

Para ejecutar con Docker:

```bash
# Construir imagen
docker build -t spark-etl .

# Ejecutar
docker run -p 8080:8080 --env-file .env \
  --network emergentesetl_emergent-etl-network \
  spark-etl
```

## Verificación

### Verificar que el servidor está corriendo

```bash
curl http://localhost:8080/health
```

### Verificar estadísticas

```bash
curl http://localhost:8080/stats
```

### Enviar evento de prueba

```bash
curl -X POST http://localhost:8080/api/data \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "model": "WS302-915M",
    "ts_utc": "2024-11-03T14:15:20Z",
    "sensor_id": "test-001",
    "LAeq": 68.4,
    "LAI": 65.2,
    "LAImax": 74.1
  }'
```

## Próximos Pasos

**FASE 5**: Ya completada (bases de datos)
**FASE 6**: API Gateway con WebSockets
**FASE 7**: Frontend React

## Estado de la FASE 4

✅ **COMPLETADA (Básica)**

- [x] Estructura del proyecto Spark creada
- [x] Servidor HTTP para recibir datos implementado
- [x] Procesadores por tipo de sensor implementados
- [x] Validación y limpieza de datos implementada
- [x] Ventaneo con watermark implementado
- [x] Agregación de métricas implementada
- [x] Escritores a MySQL y MongoDB implementados
- [x] Dockerfile creado
- [ ] Modelos probabilísticos (pendiente para fase avanzada)
- [ ] Predicciones AR(1) (pendiente para fase avanzada)

