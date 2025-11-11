# Solución de Problemas

## Problema: Error 401 al enviar a Spark

**Síntoma**: El listener-router muestra:
```
Error al enviar batch a Spark (intento 1/3)
error: "Request failed with status code 401"
```

**Causa**: El puerto 8080 está ocupado o Spark no está escuchando correctamente.

**Solución aplicada**: 
- Puerto de Spark cambiado a **8081** por defecto
- Listener-router actualizado para usar puerto **8081**

## Pasos para Corregir

### 1. Actualizar archivo `.env` del listener-router

Si tienes un archivo `.env` en `listener-router/`, asegúrate de que tenga:

```env
SPARK_PORT=8081
```

### 2. Reiniciar Spark

1. Detén Spark si está corriendo (Ctrl+C en la terminal de Spark)
2. Reinicia Spark:
```powershell
cd spark-etl
python src/main/python/etl_main.py
```

3. Verifica que esté escuchando:
```powershell
curl http://localhost:8081/health
```

Deberías ver: `{"status":"ok","queue_size":0}`

### 3. Reiniciar Listener/Router

Si el listener-router está corriendo, reinícialo para que tome la nueva configuración:

1. Detén el listener (Ctrl+C)
2. Reinicia:
```powershell
cd listener-router
npm run dev
```

## Verificar que Todo Funciona

### Verificar Spark está escuchando

```powershell
curl http://localhost:8081/health
curl http://localhost:8081/stats
```

### Verificar que el Listener puede enviar

En los logs del listener deberías ver:
```
Batch enviado a Spark
count: 10
status: 200
```

En lugar de errores 401.

### Verificar que Spark recibe datos

En los logs de Spark deberías ver:
```
Batch recibido: 10 eventos, queue_size: 10
Procesando batch de 10 eventos
Procesados X eventos de sonido
```

## Si el Puerto 8081 También Está Ocupado

Puedes cambiar a otro puerto (ej: 8082):

1. En `spark-etl/.env`:
```env
HTTP_PORT=8082
```

2. En `listener-router/.env`:
```env
SPARK_PORT=8082
```

3. Reinicia ambos servicios.

## Estado Actual del Sistema

✅ **Simulador**: Funcionando correctamente, enviando a Kafka
✅ **Kafka**: Recibiendo mensajes correctamente
✅ **Listener/Router**: Consumiendo de Kafka y procesando eventos
⚠️ **Spark**: Necesita reiniciarse con puerto 8081

