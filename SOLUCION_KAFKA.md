# Solución: Spark → Kafka → db-writer → MySQL/MongoDB

## Problema Original

Spark en Windows tiene problemas persistentes con Python workers cuando se intenta:
- Usar `collect()` para traer datos al driver
- Usar `toJSON().collect()` para convertir DataFrames a JSON
- Usar `foreachPartition()` para procesar particiones
- Enviar datos vía HTTP a db-writer

Todos estos métodos requieren que Spark lance procesos Python workers que fallan con:
```
org.apache.spark.SparkException: Python worker failed to connect back.
Caused by: java.net.SocketTimeoutException: Accept timed out
```

## Solución Implementada: Kafka como Intermediario

Se implementó una arquitectura donde:
1. **Spark** escribe datos procesados a **Kafka** usando el conector Kafka de Spark (Java/Scala - NO requiere Python workers)
2. **db-writer** consume de **Kafka** y escribe a **MySQL** y **MongoDB**

### Flujo de Datos

```
Spark ETL → Kafka (processed.metrics.v1, processed.readings.v1) → db-writer → MySQL/MongoDB
```

## Componentes

### 1. Tópicos Kafka

- **`processed.metrics.v1`**: Métricas agregadas para MySQL
- **`processed.readings.v1`**: Lecturas limpias para MongoDB

### 2. Spark KafkaSink

**Archivo**: `spark-etl/src/main/python/sinks/kafka_sink.py`

- Usa el conector Kafka de Spark (`org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0`)
- Se ejecuta completamente en **Java/Scala** - NO requiere Python workers
- Convierte DataFrames a JSON y los escribe a Kafka
- Agrega metadata (`_table_name` o `_collection_name`) para que db-writer sepa dónde escribir

### 3. db-writer KafkaConsumer

**Archivo**: `db-writer/src/kafka-consumer.ts`

- Consume de los tópicos `processed.metrics.v1` y `processed.readings.v1`
- Extrae metadata (`_table_name` o `_collection_name`)
- Escribe a MySQL o MongoDB según corresponda

## Ventajas

✅ **NO requiere Python workers** - Todo se ejecuta en Java/Scala (Spark) y Node.js (db-writer)  
✅ **Más robusto** - Kafka proporciona garantías de entrega y retención  
✅ **Escalable** - Múltiples instancias de db-writer pueden consumir en paralelo  
✅ **Desacoplado** - Spark y db-writer no están acoplados directamente  
✅ **Funciona en Windows** - Sin problemas conocidos  

## Configuración

### Spark

**Archivo**: `spark-etl/.env`

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
```

### db-writer

**Archivo**: `db-writer/.env`

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
```

## Inicialización

1. **Crear tópicos Kafka**:
   ```powershell
   .\scripts\init-kafka-topics.ps1
   ```

2. **Iniciar db-writer**:
   ```powershell
   cd db-writer
   npm install  # Instalar kafkajs
   npm run dev
   ```

3. **Iniciar Spark**:
   ```powershell
   cd spark-etl
   python src/main/python/etl_main.py
   ```

## Verificación

### Verificar que Spark está escribiendo a Kafka

```powershell
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic processed.metrics.v1 --from-beginning
```

### Verificar que db-writer está consumiendo

Revisar los logs de db-writer:
```
✓ Métrica escrita a MySQL: sound_metrics_1m
✓ Lectura escrita a MongoDB: sound_readings_clean
```

### Verificar datos en las bases de datos

- **MySQL**: Consulta las tablas `sound_metrics_1m`, `air_metrics_1m`, etc.
- **MongoDB**: Consulta las colecciones `sound_readings_clean`, etc.

## Comparación con Soluciones Anteriores

| Solución | Python Workers | Robustez | Escalabilidad | Estado |
|----------|----------------|----------|----------------|--------|
| Escritura directa (JDBC/MongoDB) | ❌ No | ✅ Alta | ⚠️ Media | ✅ Funciona |
| HTTP a db-writer | ❌ Sí (collect) | ⚠️ Media | ⚠️ Media | ❌ Falla |
| **Kafka** | ❌ **No** | ✅ **Alta** | ✅ **Alta** | ✅ **Funciona** |

## Próximos Pasos

- [ ] Agregar métricas de Kafka (mensajes enviados/consumidos)
- [ ] Implementar dead letter queue para mensajes fallidos
- [ ] Agregar retry logic en db-writer
- [ ] Configurar particionado por sensor_id para mejor distribución

