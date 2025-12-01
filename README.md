# 📊 Sistema IoT Big Data ETL con Machine Learning

Sistema completo de procesamiento en tiempo real de datos IoT con capacidades de Big Data y predicciones mediante Machine Learning usando Apache Spark.

## 🎯 Descripción del Proyecto

Pipeline ETL distribuido que procesa datos de sensores IoT en tiempo real, almacena información en bases de datos relacionales y NoSQL, y genera predicciones futuras mediante modelos de Machine Learning.

### Sensores Soportados:
- **EM310 Soterrados** - Sensores de distancia
- **EM500 CO2** - Sensores de calidad de aire (CO2, temperatura, humedad, presión)
- **WS302 Sonido** - Sensores de nivel de ruido (LAeq, LAI, LAImax)

## 🏗️ Arquitectura del Sistema

```
Productores IoT → Kafka → Spark Streaming → MySQL + MongoDB
                                    ↓
                            Spark ML (Regresión)
                                    ↓
                          Predicciones (24h futuro)
                                    ↓
                          Dashboard Streamlit
```

### Componentes Principales:

1. **Apache Kafka** - Message broker para streaming de datos
2. **Apache Spark** - Procesamiento distribuido y Machine Learning
3. **MySQL** - Base de datos relacional para datos estructurados
4. **MongoDB Atlas** - Base de datos NoSQL para datos no estructurados
5. **Streamlit** - Dashboard interactivo con visualizaciones
6. **Docker** - Contenerización de todos los servicios

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```cmd
.\setup.cmd
```

Este script automáticamente:
- ✅ Verifica e instala Docker Desktop
- ✅ Detiene contenedores existentes
- ✅ Construye las imágenes Docker
- ✅ Inicia todos los servicios
- ✅ Verifica el estado de los servicios

### Opción 2: Manual

```bash
# 1. Construir imágenes
docker-compose build

# 2. Iniciar servicios principales
docker-compose up -d zookeeper kafka mysql mongodb spark-master spark-worker

# 3. Esperar 30 segundos para inicialización

# 4. Iniciar productores
cd app/producers
python producer_em310.py &
python producer_em500.py &
python producer_ws302.py &

# 5. Iniciar consumers y dashboard
docker-compose up -d spark-consumer-em310 spark-consumer-em500 spark-consumer-ws302 dashboard

# 6. Ejecutar job de ML (opcional)
docker exec spark-ml-job /opt/spark/bin/spark-submit --master local[2] /opt/spark/app/etl/spark_ml_forecast.py
```

## 📋 Requisitos Previos

- **Docker Desktop** (Windows/Mac) o **Docker + Docker Compose** (Linux)
- **Python 3.9+** (para productores locales)
- **8GB RAM mínimo** (16GB recomendado)
- **10GB espacio en disco**

### Puertos Utilizados:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Dashboard | 8501 | Interfaz web Streamlit |
| Kafka | 9092 | Broker interno |
| Kafka | 29092 | Broker externo |
| MySQL | 3307 | Base de datos |
| MongoDB | 27017 | Base de datos NoSQL |
| Spark Master UI | 18080 | Interfaz web Spark |
| Spark Worker UI | 8081 | Worker UI |
| Zookeeper | 2181 | Coordinación Kafka |

## 🤖 Machine Learning

### Modelos Implementados:

El sistema entrena **3 modelos de regresión** por cada métrica:

1. **Linear Regression** - Modelo lineal simple y rápido
2. **Random Forest Regressor** - Ensemble de árboles de decisión
3. **Gradient Boosting Trees (GBT)** - Boosting secuencial

**Selección Automática**: El sistema evalúa los 3 modelos usando R² y selecciona automáticamente el mejor para cada métrica.

### Métricas Predichas:

- **EM310**: distance (1 métrica) → 24 predicciones
- **EM500**: co2, temperature, humidity, pressure (4 métricas) → 96 predicciones
- **WS302**: LAeq, LAI, LAImax (3 métricas) → 72 predicciones

**Total: 192 predicciones** para las próximas 24 horas

### Características de ML:

- ✅ Detección de anomalías con Z-score (±3σ)
- ✅ Evaluación con R² (coeficiente de determinación)
- ✅ Feature engineering automático
- ✅ Train/Test split (80/20)
- ✅ Predicciones horarias para 24 horas

### Ejecutar Job de ML:

```bash
# Actualizar predicciones con datos más recientes
docker exec spark-ml-job /opt/spark/bin/spark-submit --master local[2] /opt/spark/app/etl/spark_ml_forecast.py
```

**Nota**: Las predicciones NO se actualizan automáticamente. Ejecuta este comando cuando quieras regenerar predicciones con los datos más recientes.

## 📊 Dashboard

Accede al dashboard en: **http://localhost:8501**

### Características:

- 📈 Visualizaciones interactivas con Plotly
- 🔄 Auto-refresh cada 10 segundos
- 📊 Gráficos separados para:
  - Datos históricos en tiempo real
  - Predicciones ML futuras
- 📉 Estadísticas por sensor (promedio, máximo, mínimo)
- 🎯 Selector de tipo de sensor
- 📏 Control de cantidad de registros a mostrar

## 💾 Bases de Datos

### MySQL (Datos Estructurados)

**Tablas:**
- `em310_soterrados` - Datos de sensores de distancia
- `em500_co2` - Datos de calidad de aire
- `ws302_sonido` - Datos de nivel de ruido
- `predicciones` - Predicciones ML con modelo usado

**Conexión:**
```
Host: localhost
Port: 3307
User: root
Password: Os51t=Ag/3=B
Database: emergentETL
```

### MongoDB Atlas (Datos No Estructurados)

**Colecciones:**
- `em310_soterrados`
- `em500_co2`
- `ws302_sonido`

**URI:** `mongodb+srv://BDETLEmergentes:12345@bdemergetesetl.lwsmez4.mongodb.net/`

## 📁 Estructura del Proyecto

```
EmergentesETL/
├── app/
│   ├── dashboard/
│   │   ├── app.py                    # Dashboard Streamlit
│   │   └── Dockerfile
│   ├── etl/
│   │   ├── spark_consumer_em310.py   # Consumer EM310
│   │   ├── spark_consumer_em500.py   # Consumer EM500
│   │   ├── spark_consumer_ws302.py   # Consumer WS302
│   │   └── spark_ml_forecast.py      # Job de Machine Learning
│   └── producers/
│       ├── producer_em310.py         # Productor EM310
│       ├── producer_em500.py         # Productor EM500
│       └── producer_ws302.py         # Productor WS302
├── sql/
│   └── init.sql                      # Schema MySQL
├── docker-compose.yml                # Orquestación de servicios
├── Dockerfile                        # Imagen Spark custom
├── setup.cmd                         # Script de instalación automática
└── README.md
```

## 🔧 Configuración

### Variables de Entorno

**MySQL:**
```env
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Os51t=Ag/3=B
DB_NAME=emergentETL
```

**MongoDB:**
```env
MONGO_ATLAS_URI=mongodb+srv://BDETLEmergentes:12345@bdemergetesetl.lwsmez4.mongodb.net/
MONGO_DB_NAME=BDETLEmergentes
```

**Kafka:**
```env
KAFKA_BROKER=kafka:9092
KAFKA_TOPIC=datos_sensores
```

## 🛠️ Comandos Útiles

### Ver logs de un servicio:
```bash
docker logs -f <nombre_servicio>
```

### Reiniciar un servicio:
```bash
docker-compose restart <nombre_servicio>
```

### Detener todos los servicios:
```bash
docker-compose down
```

### Limpiar volúmenes y empezar desde cero:
```bash
docker-compose down -v
docker-compose up -d
```

### Verificar estado de los servicios:
```bash
docker-compose ps
```

### Acceder a un contenedor:
```bash
docker exec -it <nombre_servicio> bash
```

### Ver datos en MySQL:
```bash
docker exec -it mysql mysql -uroot -p'Os51t=Ag/3=B' -e "SELECT COUNT(*) FROM emergentETL.predicciones;"
```

## 🐛 Troubleshooting

### Dashboard no carga
```bash
docker-compose restart dashboard
docker logs -f dashboard
```

### No hay datos en MySQL
```bash
# Verificar productores están corriendo
# Verificar consumers están activos
docker logs -f spark-consumer-em310
```

### Job de ML falla
```bash
# Verificar que hay suficientes datos
docker exec mysql mysql -uroot -p'Os51t=Ag/3=B' -e "SELECT COUNT(*) FROM emergentETL.em310_soterrados;"

# Ver logs del job
docker logs spark-ml-job
```

### Puertos ocupados
```bash
# Cambiar puertos en docker-compose.yml
# Ejemplo: "8502:8501" en lugar de "8501:8501"
```

## � Flujo de Datos

1. **Productores** generan datos simulados de sensores IoT cada 5 segundos
2. **Kafka** recibe y bufferea los mensajes en el topic `datos_sensores`
3. **Spark Consumers** procesan el stream en tiempo real
4. **Datos** se guardan simultáneamente en:
   - MySQL (estructurado)
   - MongoDB Atlas (no estructurado)
5. **Job ML** (manual) entrena modelos y genera predicciones
6. **Dashboard** visualiza datos históricos y predicciones

## 🎓 Tecnologías Utilizadas

- **Apache Spark 3.5.3** - Big Data processing
- **Apache Kafka 7.5.0** - Message streaming
- **MySQL 8.0** - Base de datos relacional
- **MongoDB 6.0** - Base de datos NoSQL
- **Streamlit** - Dashboard interactivo
- **Plotly** - Visualizaciones interactivas
- **PySpark ML** - Machine Learning distribuido
- **Docker & Docker Compose** - Contenerización

## 👥 Autores

Desarrollado para el curso de Bases de Datos Emergentes

## 📝 Licencia

Este proyecto es de uso académico.

## 🚀 Próximas Mejoras

- [ ] Automatizar job de ML con cron
- [ ] Implementar validación cruzada avanzada
- [ ] Agregar más modelos ML (LSTM, Prophet)
- [ ] Sistema de alertas basado en umbrales
- [ ] API REST para acceso a datos
- [ ] Persistencia de modelos entrenados
- [ ] Dockerización de productores

---

**Dashboard URL**: http://localhost:8501  
**Spark Master UI**: http://localhost:18080  
**Spark Worker UI**: http://localhost:8081
