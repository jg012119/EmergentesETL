# Solución al Error 404 - Conexión Spark-Listener

## 🔍 Problema Identificado

El listener-router está recibiendo **error 404** al intentar enviar datos a Spark porque:
1. El servidor HTTP de Spark no se está iniciando correctamente
2. El puerto 8081 estaba ocupado por Docker/WSL (procesos del sistema)
3. **SOLUCIONADO**: Puerto cambiado a 8082 para evitar conflictos

## ✅ Soluciones Aplicadas

### 1. Mejoras en el Servidor HTTP de Spark
- ✅ Detección automática de puertos ocupados
- ✅ Mensajes de error más claros con instrucciones
- ✅ Identificación del proceso que está usando el puerto

### 2. Scripts de Utilidad
- ✅ `scripts/limpiar-puertos.ps1`: Para limpiar puertos ocupados
- ✅ `scripts/diagnostico-conexion.ps1`: Para diagnosticar problemas de conexión

### 3. Documentación Actualizada
- ✅ `spark-etl/ENV_CONFIG.md`: Puerto por defecto actualizado a 8082
- ✅ `listener-router/src/config.ts`: Puerto Spark actualizado a 8082

## 🚀 Pasos para Resolver

### Paso 1: Reiniciar Spark (Puerto 8082)

**NOTA**: El puerto ha sido cambiado a **8082** para evitar conflictos con Docker/WSL que usan el puerto 8081.

```powershell
cd spark-etl
python src/main/python/etl_main.py
```

Deberías ver:
```
✓ Iniciando servidor HTTP en 0.0.0.0:8082
  Endpoint: /api/data
  Endpoint batch: /api/data/batch
  Health check: http://localhost:8082/health
```

### Paso 2: Verificar que Spark Esté Escuchando

En otra terminal:

```powershell
curl http://localhost:8082/health
```

Deberías recibir:
```json
{"status":"ok","queue_size":0}
```

### Paso 3: Verificar el Listener-Router

El listener-router debería conectarse automáticamente. En los logs deberías ver:

```
Batch enviado a Spark
count: 10
status: 200
```

En lugar de errores 404.

## 🔧 Configuración

### Spark (spark-etl)
- Puerto por defecto: **8082** (cambiado de 8081 para evitar conflicto con Docker/WSL)
- Endpoint: `/api/data`
- Endpoint batch: `/api/data/batch`
- Health check: `/health`

### Listener-Router
- Puerto Spark: **8082** (configurado en `listener-router/src/config.ts`)
- Endpoint: `/api/data/batch`

## 📝 Notas

- El puerto por defecto ahora es **8082** para evitar conflictos con Docker/WSL
- Si necesitas usar otro puerto, crea un archivo `.env` en `spark-etl/` con:
  ```
  HTTP_PORT=8083
  ```
  Y crea un `.env` en `listener-router/` con:
  ```
  SPARK_PORT=8083
  ```

## 🐛 Si el Problema Persiste

1. Ejecuta el diagnóstico:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/diagnostico-conexion.ps1
   ```

2. Verifica los logs de Spark para ver el error exacto

3. Verifica que no haya un archivo `.env` que esté sobrescribiendo el puerto

4. Asegúrate de que el listener-router esté configurado para usar el mismo puerto que Spark

