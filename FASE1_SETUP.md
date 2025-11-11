# FASE 1: Infraestructura Kafka y Schema Registry - Completada ✅

## Resumen

Se ha completado la configuración inicial de la infraestructura base del proyecto.

## Cambios Realizados

### 1. Estructura de Carpetas

- ✅ Creada carpeta `data/csv/` para almacenar los archivos CSV
- ✅ Movidos los archivos CSV desde `venv/Include/` a `data/csv/`
- ✅ Creadas carpetas para scripts de inicialización de bases de datos:
  - `database/mysql/init/`
  - `database/mongodb/init/`
- ✅ Creada carpeta `scripts/` para scripts de utilidad

### 2. Docker Compose

- ✅ Creado `docker-compose.yml` en la raíz del proyecto con:
  - **Zookeeper**: Coordinación de Kafka
  - **Kafka**: Broker de mensajería (puertos 9092 interno, 29092 externo)
  - **Schema Registry**: Registro de esquemas (puerto 8081)
  - **MySQL**: Base de datos relacional (puerto 3306)
  - **MongoDB**: Base de datos NoSQL (puerto 27017)
  - Servicios comentados para fases futuras (simulator, listener-router, spark, api-gateway, frontend, prometheus, grafana)

### 3. Esquemas de Bases de Datos

#### MySQL (`database/mysql/init/01-schema.sql`)
- ✅ Tablas de métricas de sonido (1m, 5m, 1h)
- ✅ Tablas de métricas de distancia (1m, 5m, 1h)
- ✅ Tablas de métricas de aire (1m, 5m, 1h)
- ✅ Índices optimizados para consultas por sensor y ventana temporal

#### MongoDB (`database/mongodb/init/01-init.js`)
- ✅ Colecciones de lecturas limpias (sound, distance, air)
- ✅ Colecciones de predicciones (sound, distance, air)
- ✅ Índices para consultas eficientes

### 4. Scripts de Utilidad

- ✅ `scripts/init-kafka-topics.sh` - Script bash para crear tópicos Kafka
- ✅ `scripts/init-kafka-topics.ps1` - Script PowerShell para Windows

### 5. Configuración

- ✅ Actualizado `backend/cliente.py` para usar nueva ruta `data/csv/`
- ✅ Creado `.gitignore` para proteger archivos sensibles
- ✅ Creado `ENV_VARIABLES.md` con documentación de variables de entorno

## Próximos Pasos

### Para Iniciar los Servicios

1. **Crear archivo `.env`** (ver `ENV_VARIABLES.md`)

2. **Iniciar servicios**:
```bash
docker-compose up -d
```

3. **Verificar que los servicios estén corriendo**:
```bash
docker-compose ps
```

4. **Inicializar tópicos de Kafka** (Windows PowerShell):
```powershell
.\scripts\init-kafka-topics.ps1
```

O en Linux/Mac:
```bash
chmod +x scripts/init-kafka-topics.sh
./scripts/init-kafka-topics.sh
```

5. **Verificar tópicos creados**:
```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Verificar Conectividad

- **Kafka**: `localhost:29092` (externo) o `kafka:9092` (interno)
- **Schema Registry**: `http://localhost:8081`
- **MySQL**: `localhost:3307` (puerto externo, 3306 interno)
- **MongoDB**: `localhost:27017`

### Verificar Bases de Datos

**MySQL**:
```bash
docker exec -it mysql mysql -u etl_user -p emergent_etl
# Password: etl_password
SHOW TABLES;
```

**MongoDB**:
```bash
docker exec -it mongo mongosh -u admin -p adminpassword
use emergent_etl
show collections
```

## Archivos CSV Disponibles

Los siguientes archivos CSV están disponibles en `data/csv/`:
- `EM500-CO2-915M nov 2024.csv` - Datos de sensores de aire
- `EM500-CO2-915M nov 2024 (1).csv` - Duplicado
- `WS302-915M SONIDO NOV 2024 (1).csv` - Datos de sensores de sonido

**Nota**: Falta el archivo `EM310-UDL-915M soterrados nov 2024.csv` que se menciona en la configuración. Agregarlo cuando esté disponible.

## Estado de la FASE 1

✅ **COMPLETADA**

- [x] Estructura de carpetas creada
- [x] Archivos CSV movidos
- [x] Docker Compose configurado
- [x] Esquemas de bases de datos creados
- [x] Scripts de inicialización creados
- [x] Documentación actualizada

## Siguiente Fase

**FASE 2**: Simulador CSV → Kafka
- Crear simulador Node.js que lea CSVs y publique a Kafka
- Implementar transformadores por tipo de sensor
- Configurar emisión de eventos cada 10 segundos

