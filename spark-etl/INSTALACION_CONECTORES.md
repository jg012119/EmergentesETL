# Instalación de Conectores para Spark

Este documento explica cómo se configuran los conectores necesarios para que Spark pueda escribir a MySQL y MongoDB.

## 🔧 Problema Resuelto

Antes de esta configuración, Spark mostraba los siguientes errores:

1. **MySQL**: `ClassNotFoundException: com.mysql.cj.jdbc.Driver`
2. **MongoDB**: `ClassNotFoundException: mongo.DefaultSource`

## ✅ Solución Implementada

Los conectores se configuran automáticamente en `etl_main.py` cuando se crea la sesión de Spark. Los paquetes se descargan automáticamente desde Maven Central la primera vez que inicias Spark.

### Paquetes Configurados

1. **MySQL JDBC Driver**:
   - `mysql:mysql-connector-java:8.0.33`
   - Permite a Spark conectarse a MySQL usando JDBC

2. **MongoDB Spark Connector**:
   - `org.mongodb.spark:mongo-spark-connector_2.12:10.2.0`
   - Permite a Spark escribir directamente a MongoDB usando el conector nativo

## 📦 Descarga Automática

La primera vez que inicies Spark con esta configuración:

1. Spark detectará que faltan los JARs
2. Los descargará automáticamente desde Maven Central
3. Los guardará en caché local (`~/.ivy2/cache` o similar)
4. El proceso puede tardar **2-5 minutos** la primera vez

**Nota**: Las siguientes veces que inicies Spark, usará los JARs en caché y será mucho más rápido.

## 🚀 Uso

No necesitas hacer nada adicional. Simplemente:

1. Asegúrate de que tu `.env` tenga las URIs correctas:
   ```env
   MYSQL_URI=mysql://user:pass@host:port/database?ssl-mode=REQUIRED
   MONGO_ATLAS_URI=mongodb+srv://user:pass@cluster.mongodb.net/database?retryWrites=true&w=majority
   ```

2. Inicia Spark normalmente:
   ```bash
   cd spark-etl
   python src/main/python/etl_main.py
   ```

3. Espera a que descargue los paquetes (solo la primera vez)

4. Los conectores estarán disponibles automáticamente

## 🔍 Verificación

Si los conectores se descargaron correctamente, verás en los logs:

```
INFO:__main__:Spark session creada con paquetes: mysql:mysql-connector-java:8.0.33,org.mongodb.spark:mongo-spark-connector_2.12:10.2.0
```

Y **NO** verás los errores `ClassNotFoundException` cuando Spark intente escribir a las bases de datos.

## ⚠️ Solución de Problemas

### Si los paquetes no se descargan

1. **Verifica tu conexión a Internet**: Spark necesita acceso a Maven Central
2. **Revisa los logs**: Busca errores de descarga o timeout
3. **Descarga manual**: Puedes descargar los JARs manualmente y colocarlos en `$SPARK_HOME/jars/`

### Si ves errores de versión incompatible

1. Verifica la versión de Spark: `pyspark.__version__`
2. Ajusta la versión del conector de MongoDB si es necesario
3. Para Spark 3.5.0, usa `mongo-spark-connector_2.12:10.2.0`

### Si los errores persisten después de reiniciar

1. Limpia la caché de Spark: `rm -rf ~/.ivy2/cache`
2. Reinicia Spark
3. Espera a que descargue los paquetes nuevamente

## 📚 Referencias

- [MySQL Connector/J](https://dev.mysql.com/doc/connector-j/8.0/en/)
- [MongoDB Spark Connector](https://www.mongodb.com/docs/spark-connector/current/)
- [Spark Packages](https://spark-packages.org/)

