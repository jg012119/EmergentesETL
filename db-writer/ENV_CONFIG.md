# Configuración de Variables de Entorno - DB Writer

Este servicio requiere las siguientes variables de entorno. Copia `.env.example` a `.env` y configura los valores.

## Variables Requeridas

### Servidor
- `HOST`: Host donde escuchará el servidor (default: `0.0.0.0`)
- `PORT`: Puerto del servidor (default: `3001`)

### MySQL

**Opción 1: URI Completa (Recomendado para bases de datos hosteadas)**
- `MYSQL_URI`: URI completa de MySQL
  - Ejemplo: `mysql://user:password@host:port/database?ssl-mode=REQUIRED`

**Opción 2: Parámetros Individuales**
- `MYSQL_HOST`: Host de MySQL (default: `localhost`)
- `MYSQL_PORT`: Puerto de MySQL (default: `3306`)
- `MYSQL_DATABASE`: Nombre de la base de datos (default: `emergent_etl`)
- `MYSQL_USER`: Usuario de MySQL (default: `etl_user`)
- `MYSQL_PASSWORD`: Contraseña de MySQL (default: `etl_password`)

### MongoDB

**Opción 1: URI Completa (Recomendado para MongoDB Atlas)**
- `MONGO_ATLAS_URI`: URI completa de MongoDB Atlas
  - Ejemplo: `mongodb+srv://user:password@cluster.mongodb.net/database?retryWrites=true&w=majority`

**Opción 2: Parámetros Individuales**
- `MONGO_HOST`: Host de MongoDB (default: `localhost`)
- `MONGO_PORT`: Puerto de MongoDB (default: `27017`)
- `MONGO_DATABASE`: Nombre de la base de datos (default: `emergent_etl`)
- `MONGO_USER`: Usuario de MongoDB (default: `admin`)
- `MONGO_PASSWORD`: Contraseña de MongoDB (default: `adminpassword`)

### Logging
- `LOG_LEVEL`: Nivel de logging (default: `info`)
  - Valores: `error`, `warn`, `info`, `debug`

## Ejemplo de .env

```env
# Servidor
HOST=0.0.0.0
PORT=3001

# MySQL (usar URI completa para bases hosteadas)
MYSQL_URI=mysql://user:password@host:port/database?ssl-mode=REQUIRED

# MongoDB (usar URI completa para MongoDB Atlas)
MONGO_ATLAS_URI=mongodb+srv://user:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# Logging
LOG_LEVEL=info
```

## Notas

- Si se proporciona `MYSQL_URI`, se usará en lugar de los parámetros individuales
- Si se proporciona `MONGO_ATLAS_URI`, se usará en lugar de los parámetros individuales
- El servicio verifica la conexión al iniciar y registra un warning si no puede conectarse

