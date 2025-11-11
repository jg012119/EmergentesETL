# Solución: Escritura Directa a Bases de Datos

## Problema

Spark en Windows tiene problemas persistentes con Python workers cuando se intenta:
- Usar `collect()` para traer datos al driver
- Usar `toJSON().collect()` para convertir DataFrames a JSON
- Usar `foreachPartition()` para procesar particiones

Todos estos métodos requieren que Spark lance procesos Python workers que fallan con:
```
org.apache.spark.SparkException: Python worker failed to connect back.
Caused by: java.net.SocketTimeoutException: Accept timed out
```

## Solución Implementada

Se cambió a **escritura directa** usando los conectores nativos de Spark que se ejecutan completamente en **Java/Scala** y **NO requieren Python workers**:

### MySQL
- **Conector**: JDBC (Java)
- **Método**: `df.write.format("jdbc").save()`
- **Ventaja**: Ejecución nativa en Java, sin Python workers

### MongoDB
- **Conector**: Spark-MongoDB (Java/Scala)
- **Método**: `df.write.format("mongo").save()`
- **Ventaja**: Ejecución nativa en Java/Scala, sin Python workers

## Cambios Realizados

1. **Deshabilitado db-writer**: El servicio Node.js `db-writer` ya no se usa temporalmente
2. **Habilitados conectores directos**: Se usan `MySQLSink` y `MongoDBSink` directamente
3. **Sin Python workers**: Las escrituras se ejecutan completamente en Java/Scala

## Código Actual

```python
# Inicializar sinks directos (NO requieren Python workers)
mysql_sink = MySQLSink(spark)
mongo_sink = MongoDBSink(spark)

# Escribir directamente
mysql_sink.write_metrics(metrics, "sound_metrics_1m")
mongo_sink.write_readings(df, "sound_readings_clean")
```

## Ventajas

✅ **NO requiere Python workers** - Todo se ejecuta en Java/Scala  
✅ **Más eficiente** - Escritura nativa sin overhead de Python  
✅ **Sin problemas de conexión** - No hay timeouts de Python workers  
✅ **Funciona en Windows** - Sin problemas conocidos  

## Desventajas

⚠️ **db-writer deshabilitado** - No se puede usar el servicio Node.js intermedio  
⚠️ **Menos flexibilidad** - No se puede agregar lógica de negocio en Node.js antes de escribir  

## Próximos Pasos

Si en el futuro se necesita usar `db-writer` nuevamente, se pueden explorar:

1. **Usar WSL2** - Ejecutar Spark en WSL2 donde Python workers funcionan mejor
2. **Usar Docker** - Ejecutar Spark en un contenedor Linux
3. **Usar Spark en modo cluster** - Ejecutar Spark en un cluster remoto (no local)
4. **Investigar más a fondo** - El problema de Python workers puede tener solución con configuraciones específicas

## Estado Actual

✅ **Escrituras habilitadas** usando conectores directos  
✅ **Sin errores de Python workers**  
✅ **Datos fluyendo a MySQL y MongoDB**  

## Verificación

Para verificar que los datos se están escribiendo:

1. **MySQL**: Consulta las tablas `sound_metrics_1m`, `air_metrics_1m`, etc.
2. **MongoDB**: Consulta las colecciones `sound_readings_clean`, etc.
3. **Logs de Spark**: Busca mensajes como "Métricas escritas a MySQL" y "Lecturas escritas a MongoDB"

