# Instrucciones para Configurar MySQL Hosteado

## 📋 Script SQL Requerido

Necesitas ejecutar el script `database/mysql/init/01-schema-hosted.sql` en tu base de datos MySQL hosteada (Aiven Cloud).

## 🚀 Pasos para Ejecutar el Script

### Opción 1: Usando MySQL Workbench o cliente gráfico

1. Conecta a tu base de datos MySQL en Aiven Cloud usando las credenciales de tu `.env`
2. Abre el archivo `database/mysql/init/01-schema-hosted.sql`
3. **IMPORTANTE**: Si tu base de datos no se llama `defaultdb`, cambia la línea:
   ```sql
   USE defaultdb;
   ```
   Por el nombre de tu base de datos (ej: `USE emergent_etl;`)
4. Ejecuta el script completo

### Opción 2: Usando línea de comandos (mysql client)

```bash
# Conectarte a la base de datos
mysql -h mysql-db1234-db-emergentes.k.aivencloud.com \
      -P 21145 \
      -u avnadmin \
      -p \
      --ssl-mode=REQUIRED \
      defaultdb < database/mysql/init/01-schema-hosted.sql
```

### Opción 3: Usando la consola web de Aiven

1. Ve a tu proyecto en Aiven Cloud
2. Abre la consola SQL de tu servicio MySQL
3. Copia y pega el contenido de `database/mysql/init/01-schema-hosted.sql`
4. **IMPORTANTE**: Cambia `USE defaultdb;` por el nombre de tu base de datos si es diferente
5. Ejecuta el script

## 📊 Tablas que se Crearán

El script crea **9 tablas** en total:

### Tablas de Sonido (3)
- `sound_metrics_1m` - Métricas agregadas por minuto
- `sound_metrics_5m` - Métricas agregadas por 5 minutos
- `sound_metrics_1h` - Métricas agregadas por hora

### Tablas de Distancia (3)
- `distance_metrics_1m` - Métricas agregadas por minuto
- `distance_metrics_5m` - Métricas agregadas por 5 minutos
- `distance_metrics_1h` - Métricas agregadas por hora

### Tablas de Aire (3)
- `air_metrics_1m` - Métricas agregadas por minuto
- `air_metrics_5m` - Métricas agregadas por 5 minutos
- `air_metrics_1h` - Métricas agregadas por hora

## ⚠️ Nota Importante sobre el Nombre de la Base de Datos

Tu URI de MySQL actual es:
```
mysql://...@host:port/defaultdb?ssl-mode=REQUIRED
```

Esto significa que la base de datos se llama `defaultdb`. Si quieres usar otra base de datos:

1. **Opción A**: Cambia el nombre en la URI del `.env`:
   ```env
   MYSQL_URI=mysql://...@host:port/emergent_etl?ssl-mode=REQUIRED
   ```

2. **Opción B**: Cambia el `USE defaultdb;` en el script SQL por tu nombre de base de datos

## ✅ Verificación

Después de ejecutar el script, verifica que las tablas se crearon:

```sql
USE defaultdb;  -- o tu nombre de base de datos
SHOW TABLES;
```

Deberías ver las 9 tablas listadas.

## 🔍 Verificar Estructura de una Tabla

```sql
DESCRIBE sound_metrics_1m;
```

