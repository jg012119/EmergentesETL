# Monitoreo de Escrituras de Datos

Este documento explica cómo verificar que los datos se están escribiendo correctamente en las bases de datos.

## Estado del Sistema

### Componentes Requeridos

1. **db-writer** (Node.js)
   - Puerto: `3001`
   - Health check: `http://localhost:3001/health`
   - Debe estar corriendo antes de iniciar Spark

2. **Spark ETL** (Python)
   - Puerto HTTP: `8082`
   - Health check: `http://localhost:8082/health`
   - Procesa datos y los envía al db-writer

## Verificación Rápida

Ejecuta el script de monitoreo:

```powershell
.\scripts\monitorear-escrituras.ps1
```

Este script verifica:
- ✅ db-writer está corriendo y respondiendo
- ✅ Spark HTTP está corriendo y respondiendo
- ✅ Procesos activos
- ✅ Puertos en uso

## Logs de Escritura

### En Spark (Terminal de Spark)

Busca estos mensajes que indican que los datos se están enviando:

```
INFO:__main__:Procesados X eventos de sonido
INFO:db_writer_client:Métricas enviadas a db-writer: sound_metrics_1m (X registros)
INFO:db_writer_client:Lecturas enviadas a db-writer: sound_readings_clean (X documentos)
```

### En db-writer (Terminal de db-writer)

Busca estos mensajes que indican que los datos se están recibiendo y escribiendo:

```
[info]: Recibidas métricas para sound_metrics_1m: X registros
[info]: Escritas X métricas en MySQL para la tabla sound_metrics_1m
[info]: Recibidas lecturas para sound_readings_clean: X documentos
[info]: Escritas X lecturas en MongoDB para la colección sound_readings_clean
```

## Verificar Datos en las Bases de Datos

### MySQL

Conecta a tu base de datos MySQL y ejecuta:

```sql
-- Ver métricas de sonido
SELECT * FROM sound_metrics_1m ORDER BY window_start DESC LIMIT 10;

-- Ver métricas de aire
SELECT * FROM air_metrics_1m ORDER BY window_start DESC LIMIT 10;

-- Ver métricas de distancia
SELECT * FROM distance_metrics_1m ORDER BY window_start DESC LIMIT 10;

-- Contar registros por tabla
SELECT 
    'sound_metrics_1m' as tabla, COUNT(*) as registros FROM sound_metrics_1m
UNION ALL
SELECT 
    'air_metrics_1m' as tabla, COUNT(*) as registros FROM air_metrics_1m
UNION ALL
SELECT 
    'distance_metrics_1m' as tabla, COUNT(*) as registros FROM distance_metrics_1m;
```

### MongoDB Atlas

Conecta a MongoDB Atlas y ejecuta:

```javascript
// Usar la base de datos
use emergent_etl;

// Ver lecturas de sonido
db.sound_readings_clean.find().sort({ts_utc: -1}).limit(10);

// Ver lecturas de aire
db.air_readings_clean.find().sort({ts_utc: -1}).limit(10);

// Contar documentos por colección
db.sound_readings_clean.countDocuments();
db.air_readings_clean.countDocuments();
db.distance_readings_clean.countDocuments();
```

## Solución de Problemas

### No se ven datos en los logs

1. **Verifica que db-writer esté corriendo:**
   ```powershell
   # En otra terminal
   cd db-writer
   npm run dev
   ```

2. **Verifica que Spark esté corriendo:**
   ```powershell
   # En otra terminal
   cd spark-etl
   python src/main/python/etl_main.py
   ```

3. **Verifica que el simulador esté enviando datos:**
   ```powershell
   # En otra terminal
   cd simulator
   npm run dev
   ```

### Errores de "Python worker failed to connect back"

Si ves este error, significa que `toJSON().collect()` todavía está causando problemas. En este caso:

1. Verifica que `winutils.exe` esté instalado correctamente
2. Revisa los logs de Spark para ver el error completo
3. Considera usar una alternativa como `foreachPartition` (requiere más cambios)

### db-writer no recibe datos

1. **Verifica la conexión:**
   ```powershell
   # Health check
   Invoke-WebRequest -Uri "http://localhost:3001/health"
   ```

2. **Verifica las variables de entorno:**
   - `DB_WRITER_HOST` en `spark-etl/.env` debe ser `localhost`
   - `DB_WRITER_PORT` en `spark-etl/.env` debe ser `3001`

3. **Revisa los logs de db-writer** para ver si hay errores de conexión a MySQL o MongoDB

### Datos no aparecen en las bases de datos

1. **Verifica las credenciales:**
   - MySQL: Revisa `MYSQL_URI` en `db-writer/.env`
   - MongoDB: Revisa `MONGO_ATLAS_URI` en `db-writer/.env`

2. **Verifica que las tablas/colecciones existan:**
   - MySQL: Ejecuta `database/mysql/init/01-schema-hosted.sql`
   - MongoDB: Las colecciones se crean automáticamente, pero verifica que la base de datos exista

3. **Revisa los logs de db-writer** para ver errores de escritura

## Flujo de Datos Esperado

```
Simulador → Kafka → Listener → Spark → db-writer → MySQL/MongoDB
```

1. **Simulador**: Lee CSV y publica a Kafka
2. **Kafka**: Almacena mensajes
3. **Listener**: Consume de Kafka y envía a Spark
4. **Spark**: Procesa, agrega y envía a db-writer
5. **db-writer**: Escribe en MySQL y MongoDB

Cada paso debe tener logs indicando el progreso.

## Próximos Pasos

Una vez que veas datos fluyendo:

1. ✅ Verifica que los datos aparezcan en MySQL
2. ✅ Verifica que los datos aparezcan en MongoDB
3. ✅ Revisa la calidad de los datos (valores, timestamps, etc.)
4. ✅ Implementa modelos probabilísticos (Gaussiano, EWMA, AR1)
5. ✅ Configura el API Gateway para consultar los datos

