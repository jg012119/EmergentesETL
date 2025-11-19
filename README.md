## Guía de despliegue - EmergentesETL

Este proyecto ha sido adaptado para funcionar de manera similar al proyecto Pr-ctica3BigData, utilizando una arquitectura basada en Kafka, Spark, MySQL y MongoDB.

---

## 🚀 Instalación y Uso

### Requisitos previos

- **Docker Desktop** (con al menos 2 CPUs y 8 GB de RAM asignados a Docker)
- **docker-compose** (ya viene con Docker Desktop reciente)
- Acceso a internet para descargar imágenes y dependencias

---

### 1. Levantar la infraestructura con Docker

Desde la raíz del proyecto:

```powershell
docker-compose down --volumes --remove-orphans
docker-compose up -d
```

Verifica que todos los contenedores estén en estado `Up`:

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

> Espera ~30 s hasta que `mysql` termine de inicializar (el script `sql/init.sql` crea las tablas automáticamente).

---

### 2. Ejecutar los producers por tipo de sensor

Los CSV no se procesan automáticamente para evitar re-procesamientos accidentales. Ejecuta cada productor:

```powershell
# EM310 (soterrados)
docker exec -d spark-master python3 /opt/spark/app/etl/spark_producer_em310.py

# EM500 (calidad del aire)
docker exec -d spark-master python3 /opt/spark/app/etl/spark_producer_em500.py

# WS302 (sonido)
docker exec -d spark-master python3 /opt/spark/app/etl/spark_producer_ws302.py
```

Cada script recorre su CSV, envía los mensajes a Kafka y termina. Puedes revisar los logs de Kafka o de los consumers si deseas confirmar el envío.

---

### 3. Verificar que los consumers están guardando datos

Los tres consumers (`spark-consumer-em310`, `spark-consumer-em500`, `spark-consumer-ws302`) se levantan automáticamente con Docker y clasifican los registros por tabla. Para validar que MySQL se está poblando:

```powershell
docker exec mysql mysql -uroot -p"Os51t=Ag/3=B" -e ^
"USE emergentETL;
 SELECT 'em310_soterrados' AS tabla, COUNT(*) FROM em310_soterrados
 UNION ALL
 SELECT 'em500_co2', COUNT(*) FROM em500_co2
 UNION ALL
 SELECT 'ws302_sonido', COUNT(*) FROM ws302_sonido;"
```

También puedes inspeccionar filas de ejemplo:

```powershell
docker exec mysql mysql -uroot -p"Os51t=Ag/3=B" -e ^
"USE emergentETL;
 SELECT device_name, time, co2, temperature, humidity FROM em500_co2 LIMIT 5;
 SELECT tenant_name, time, LAeq, LAI, LAImax FROM ws302_sonido LIMIT 5;"
```

Los consumers escriben simultáneamente en MongoDB Atlas (colección `sensores`).

---

### 4. Configuraciones clave

1. **MySQL (contenedor):**
   - Usuario: `root`
   - Contraseña: `Os51t=Ag/3=B`
   - Base de datos: `emergentETL`

2. **MongoDB Atlas:**
   - URI configurada directamente en los consumers (`app/etl/spark_consumer_*.py`). Si cambias las credenciales, actualiza la variable `MONGO_ATLAS_URI`.

3. **docker-compose.yml:**
   - Ya incluye Zookeeper, Kafka, Spark Master/Worker, MySQL, Mongo local y **tres consumers Spark independientes** (uno por tipo de sensor).

---

### 5. Apagar los servicios

```powershell
docker-compose down
```

Si necesitas liberar los datos de MySQL/Mongo locales:

```powershell
docker-compose down --volumes
```

---

### 6. Problemas frecuentes

- **MySQL rechaza conexiones**: espera unos segundos tras `docker-compose up -d`; los consumers reintentan automáticamente.
- **Kafka muestra offsets pero las tablas siguen vacías**: confirma que los producers hayan terminado sin errores (`docker logs spark-master | Select-String "🚀 PRODUCTOR"`).
- **Cambiaste credenciales**: recuerda actualizar tanto `docker-compose.yml` como los scripts `spark_consumer_*.py`.

---

## Estructura del Proyecto

```
EmergentesETL/
├── app/
│   └── etl/
│       ├── __init__.py
│       ├── spark_producer_em310.py
│       ├── spark_producer_em500.py
│       ├── spark_producer_ws302.py
│       ├── spark_consumer_em310.py
│       ├── spark_consumer_em500.py
│       └── spark_consumer_ws302.py
├── data/
│   ├── EM310-UDL-915M soterrados nov 2024.csv
│   ├── EM500-CO2-915M nov 2024.csv
│   └── WS302-915M SONIDO NOV 2024.csv
├── sql/
│   └── init.sql
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

Con estos pasos deberías poder replicar todo el flujo end-to-end. ¡Éxitos!

