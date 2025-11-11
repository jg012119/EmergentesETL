# Verificación de Servicios - Comandos Útiles

## ✅ Estado Actual

Todos los servicios están corriendo correctamente:

- ✅ **Kafka**: Tópicos creados exitosamente
- ✅ **MySQL**: 9 tablas creadas
- ✅ **MongoDB**: Base de datos inicializada
- ✅ **Zookeeper**: Healthy
- ✅ **Schema Registry**: Running

## Comandos para Verificar Servicios

### Ver Estado de Contenedores

```powershell
docker-compose ps
```

### Verificar Tópicos de Kafka

```powershell
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Verificar MySQL

**Ver todas las tablas:**
```powershell
docker exec mysql mysql -u etl_user -petl_password emergent_etl -e "SHOW TABLES;"
```

**Ver estructura de una tabla:**
```powershell
docker exec mysql mysql -u etl_user -petl_password emergent_etl -e "DESCRIBE sound_metrics_1m;"
```

**Contar registros en una tabla:**
```powershell
docker exec mysql mysql -u etl_user -petl_password emergent_etl -e "SELECT COUNT(*) FROM sound_metrics_1m;"
```

**Conectar interactivamente (si necesitas hacer consultas más complejas):**
```powershell
docker exec -it mysql mysql -u etl_user -petl_password emergent_etl
```

### Verificar MongoDB

**Ver todas las colecciones:**
```powershell
docker exec mongo mongosh emergent_etl -u admin -p adminpassword --quiet --eval "db.getCollectionNames()"
```

**Contar documentos en una colección:**
```powershell
docker exec mongo mongosh emergent_etl -u admin -p adminpassword --quiet --eval "db.sound_readings_clean.countDocuments()"
```

**Conectar interactivamente:**
```powershell
docker exec -it mongo mongosh -u admin -p adminpassword
```

Luego dentro de mongosh:
```javascript
use emergent_etl
show collections
db.sound_readings_clean.find().limit(5)
```

### Verificar Schema Registry

```powershell
curl http://localhost:8081/subjects
```

### Ver Logs de un Servicio

```powershell
docker-compose logs kafka
docker-compose logs mysql
docker-compose logs mongo
```

### Reiniciar un Servicio

```powershell
docker-compose restart mysql
docker-compose restart kafka
```

### Detener Todos los Servicios

```powershell
docker-compose down
```

### Iniciar Todos los Servicios

```powershell
docker-compose up -d
```

## Nota Importante

**NO necesitas borrar contenedores para verificar MySQL o MongoDB**. Simplemente ejecuta los comandos `docker exec` mostrados arriba. Los contenedores mantienen los datos en volúmenes Docker, así que aunque los detengas y reinicies, los datos persisten.

Solo necesitarías borrar un contenedor si:
- Quieres eliminar completamente los datos (usar `docker-compose down -v` para eliminar volúmenes)
- Hay un error de configuración que requiere recrear el contenedor

## Puertos de los Servicios

- **Zookeeper**: `localhost:2181`
- **Kafka**: `localhost:29092` (externo), `kafka:9092` (interno)
- **Schema Registry**: `http://localhost:8081`
- **MySQL**: `localhost:3307` (externo), `mysql:3306` (interno)
- **MongoDB**: `localhost:27017`

## Tópicos Kafka Creados

- `em310.distance.raw.v1` (3 particiones, retención 7 días)
- `em500.air.raw.v1` (3 particiones, retención 7 días)
- `ws302.sound.raw.v1` (3 particiones, retención 7 días)

## Tablas MySQL Creadas

- `sound_metrics_1m`, `sound_metrics_5m`, `sound_metrics_1h`
- `distance_metrics_1m`, `distance_metrics_5m`, `distance_metrics_1h`
- `air_metrics_1m`, `air_metrics_5m`, `air_metrics_1h`

## Colecciones MongoDB Creadas

- `sound_readings_clean`
- `distance_readings_clean`
- `air_readings_clean`
- `sound_predictions`
- `distance_predictions`
- `air_predictions`

