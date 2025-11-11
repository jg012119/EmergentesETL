# Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# ============================================
# CONFIGURACIÓN DE BASES DE DATOS
# ============================================

# MySQL
# Nota: El puerto externo es 3307 (no 3306) para evitar conflictos con MySQL local
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=emergent_etl
MYSQL_USER=etl_user
MYSQL_PASSWORD=etl_password

# MongoDB
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=adminpassword
MONGO_DATABASE=emergent_etl

# ============================================
# CONFIGURACIÓN DE KAFKA
# ============================================
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_BOOTSTRAP_SERVERS_INTERNAL=kafka:9092

# ============================================
# CONFIGURACIÓN DE SPARK
# ============================================
SPARK_HOST=spark-master
SPARK_PORT=7077

# ============================================
# CONFIGURACIÓN DE API GATEWAY
# ============================================
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION=24h

# ============================================
# CONFIGURACIÓN DE MONITOREO
# ============================================
GRAFANA_ADMIN_PASSWORD=admin

# ============================================
# CONFIGURACIÓN DE MONGODB ATLAS (OPCIONAL)
# ============================================
# Si usas MongoDB Atlas en lugar de local, descomenta y configura:
# MONGO_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/emergent_etl?retryWrites=true&w=majority
```

## Notas

- **NUNCA** commitees el archivo `.env` al repositorio (debe estar en `.gitignore`)
- Cambia las contraseñas por defecto en producción
- El `JWT_SECRET` debe ser una cadena aleatoria segura

