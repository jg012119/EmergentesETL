# Cómo Consultar los Datos Procesados

Este documento explica cómo ver y consultar los datos que el sistema ETL ha procesado y almacenado.

## 📊 Ubicación de los Datos

Los datos se almacenan en dos bases de datos:

1. **MySQL (Hosteado)**: Métricas agregadas por ventanas de tiempo
2. **MongoDB Atlas**: Lecturas limpias y detalladas de los sensores

---

## 🗄️ MySQL - Métricas Agregadas

### Tablas Disponibles

**Sonido (WS302):**
- `sound_metrics_1m` - Métricas de 1 minuto
- `sound_metrics_5m` - Métricas de 5 minutos
- `sound_metrics_1h` - Métricas de 1 hora

**Distancia (EM310):**
- `distance_metrics_1m` - Métricas de 1 minuto
- `distance_metrics_5m` - Métricas de 5 minutos
- `distance_metrics_1h` - Métricas de 1 hora

**Aire (EM500):**
- `air_metrics_1m` - Métricas de 1 minuto
- `air_metrics_5m` - Métricas de 5 minutos
- `air_metrics_1h` - Métricas de 1 hora

### Opción 1: Consola Web de Aiven (Recomendado)

Si usas Aiven Cloud para MySQL:

1. Inicia sesión en [Aiven Console](https://console.aiven.io/)
2. Selecciona tu proyecto y servicio MySQL
3. Abre la **Consola SQL** o **Query Editor**
4. Ejecuta tus consultas SQL

### Opción 2: MySQL Workbench

1. Descarga e instala [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)
2. Crea una nueva conexión con los datos de tu `MYSQL_URI`:
   - Host: (extrae de tu URI)
   - Puerto: (extrae de tu URI)
   - Usuario: (extrae de tu URI)
   - Contraseña: (extrae de tu URI)
   - Base de datos: `defaultdb` (o la que uses)
3. Conecta y ejecuta consultas

### Opción 3: Línea de Comandos (MySQL Client)

```bash
# Conectar a MySQL hosteado
mysql -h <host> -P <puerto> -u <usuario> -p<contraseña> <base_de_datos>
```

**Ejemplo de consultas útiles:**

```sql
-- Ver todas las tablas
SHOW TABLES;

-- Contar registros en una tabla
SELECT COUNT(*) FROM sound_metrics_1m;

-- Ver los últimos 10 registros de sonido
SELECT * FROM sound_metrics_1m 
ORDER BY window_start DESC 
LIMIT 10;

-- Ver métricas por sensor
SELECT sensor_id, 
       AVG(laeq_avg) as promedio_laeq,
       MAX(laimax_max) as max_laimax,
       COUNT(*) as total_ventanas
FROM sound_metrics_1m
GROUP BY sensor_id;

-- Ver métricas de las últimas 24 horas
SELECT * FROM sound_metrics_1m
WHERE window_start >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY window_start DESC;

-- Ver métricas de aire recientes
SELECT sensor_id, 
       window_start,
       co2_avg,
       temp_avg,
       rh_avg,
       press_avg
FROM air_metrics_1m
ORDER BY window_start DESC
LIMIT 20;
```

---

## 🍃 MongoDB Atlas - Lecturas Detalladas

### Colecciones Disponibles

**Lecturas Limpias:**
- `sound_readings_clean` - Lecturas de sonido validadas
- `distance_readings_clean` - Lecturas de distancia validadas
- `air_readings_clean` - Lecturas de aire validadas

**Predicciones (cuando se implementen):**
- `sound_predictions`
- `distance_predictions`
- `air_predictions`

### Opción 1: MongoDB Atlas Web UI (Recomendado)

1. Inicia sesión en [MongoDB Atlas](https://cloud.mongodb.com/)
2. Selecciona tu cluster
3. Haz clic en **Browse Collections**
4. Selecciona la base de datos `emergent_etl`
5. Explora las colecciones y documentos

### Opción 2: MongoDB Compass

1. Descarga e instala [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Conecta usando tu `MONGO_ATLAS_URI`
3. Navega a la base de datos `emergent_etl`
4. Explora las colecciones

### Opción 3: Línea de Comandos (mongosh)

```bash
# Conectar a MongoDB Atlas
mongosh "<MONGO_ATLAS_URI>"
```

**Ejemplo de consultas útiles:**

```javascript
// Cambiar a la base de datos
use emergent_etl

// Ver todas las colecciones
show collections

// Contar documentos en una colección
db.sound_readings_clean.countDocuments()

// Ver los últimos 10 documentos de sonido
db.sound_readings_clean.find()
  .sort({ ts_utc: -1 })
  .limit(10)
  .pretty()

// Ver lecturas de un sensor específico
db.sound_readings_clean.find({ 
  sensor_id: "WS302-001" 
})
  .sort({ ts_utc: -1 })
  .limit(20)
  .pretty()

// Ver lecturas de aire recientes
db.air_readings_clean.find()
  .sort({ ts_utc: -1 })
  .limit(10)
  .pretty()

// Buscar lecturas con valores altos de CO2
db.air_readings_clean.find({
  co2: { $gt: 1000 }
})
  .sort({ ts_utc: -1 })
  .pretty()

// Agregación: promedio de LAeq por sensor
db.sound_readings_clean.aggregate([
  {
    $group: {
      _id: "$sensor_id",
      promedio_laeq: { $avg: "$LAeq" },
      max_laeq: { $max: "$LAeq" },
      count: { $sum: 1 }
    }
  },
  { $sort: { promedio_laeq: -1 } }
])
```

---

## 🔍 Verificar si Hay Datos

### Verificar MySQL

```sql
-- Verificar si hay datos en las tablas principales
SELECT 
  'sound_metrics_1m' as tabla, COUNT(*) as registros FROM sound_metrics_1m
UNION ALL
SELECT 
  'distance_metrics_1m', COUNT(*) FROM distance_metrics_1m
UNION ALL
SELECT 
  'air_metrics_1m', COUNT(*) FROM air_metrics_1m;
```

### Verificar MongoDB

```javascript
// Verificar conteos en todas las colecciones
db.getCollectionNames().forEach(function(collection) {
  var count = db[collection].countDocuments();
  print(collection + ": " + count + " documentos");
});
```

---

## 📝 Nota Importante

**⚠️ Actualmente las escrituras están deshabilitadas temporalmente** para diagnosticar problemas de conexión. Una vez que se resuelvan los errores, los datos comenzarán a escribirse automáticamente a las bases de datos.

Para verificar si el sistema está escribiendo datos, revisa los logs de Spark. Deberías ver mensajes como:
- `Métricas escritas a MySQL: sound_metrics_1m`
- `Lecturas escritas a MongoDB: sound_readings_clean`

---

## 🛠️ Herramientas Recomendadas

- **MySQL**: [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) o [DBeaver](https://dbeaver.io/)
- **MongoDB**: [MongoDB Compass](https://www.mongodb.com/products/compass) o [Studio 3T](https://studio3t.com/)
- **Ambas**: [DBeaver](https://dbeaver.io/) (soporta MySQL y MongoDB)

---

## 📊 Ejemplo de Consulta Completa

### MySQL: Dashboard de Métricas

```sql
-- Resumen de métricas de sonido por sensor
SELECT 
  sensor_id,
  COUNT(*) as total_ventanas,
  AVG(laeq_avg) as promedio_laeq,
  MAX(laimax_max) as max_laimax,
  AVG(alert_prob) as probabilidad_alerta_promedio,
  MIN(window_start) as primera_lectura,
  MAX(window_start) as ultima_lectura
FROM sound_metrics_1m
GROUP BY sensor_id
ORDER BY promedio_laeq DESC;
```

### MongoDB: Análisis de Lecturas

```javascript
// Análisis de lecturas de aire por sensor
db.air_readings_clean.aggregate([
  {
    $group: {
      _id: "$sensor_id",
      promedio_co2: { $avg: "$co2" },
      promedio_temp: { $avg: "$temperature" },
      promedio_hum: { $avg: "$humidity" },
      max_co2: { $max: "$co2" },
      min_temp: { $min: "$temperature" },
      total_lecturas: { $sum: 1 },
      primera_lectura: { $min: "$ts_utc" },
      ultima_lectura: { $max: "$ts_utc" }
    }
  },
  { $sort: { promedio_co2: -1 } }
])
```

---

## 🔗 Acceso Rápido

- **MySQL Hosteado**: Usa tu `MYSQL_URI` del archivo `.env`
- **MongoDB Atlas**: Usa tu `MONGO_ATLAS_URI` del archivo `.env`
- **Base de datos MySQL**: `defaultdb` (o la que configuraste)
- **Base de datos MongoDB**: `emergent_etl`

