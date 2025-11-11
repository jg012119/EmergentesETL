# Guía para Iniciar el Sistema Completo

Esta guía te ayudará a iniciar todos los componentes del sistema ETL en el orden correcto.

## Prerequisitos

✅ Servicios Docker corriendo (Kafka, MySQL, MongoDB, etc.)
✅ Tópicos Kafka creados
✅ Archivos CSV en `data/csv/`
✅ Archivos `.env` configurados

## Orden de Inicio

### Paso 1: Iniciar Spark ETL (Terminal 1)

```powershell
cd spark-etl
python src/main/python/etl_main.py
```

**Espera a ver:**
```
=== Iniciando Spark ETL ===
Spark session creada
Servidor HTTP iniciado
```

El servidor HTTP estará disponible en `http://localhost:8082`

**Verificar:**
```powershell
curl http://localhost:8082/health
```

O en el navegador: http://localhost:8082/health

Deberías ver: `{"status":"ok","queue_size":0}`

---

### Paso 2: Iniciar Listener/Router (Terminal 2)

**Abre una nueva terminal** y ejecuta:

```powershell
cd listener-router
npm run dev
```

**Espera a ver:**
```
=== Iniciando Listener/Router ===
Conectado a Kafka como consumidor
Suscrito a tópicos: em310.distance.raw.v1, em500.air.raw.v1, ws302.sound.raw.v1
Listener/Router corriendo
```

---

### Paso 3: Iniciar Simulador (Terminal 3)

**Abre otra terminal** y ejecuta:

```powershell
cd simulator
npm run dev
```

**Espera a ver:**
```
=== Iniciando Simulador CSV → Kafka ===
CSV cargado: X filas
✓ Configurado: archivo.csv → tópico
Iniciando simulación...
```

---

## Verificar que Todo Funciona

### 1. Verificar que Kafka recibe mensajes

**Terminal 4:**
```powershell
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ws302.sound.raw.v1 --from-beginning
```

Deberías ver mensajes JSON apareciendo cada 10 segundos.

### 2. Verificar que el Listener procesa mensajes

En la **Terminal 2** (Listener/Router), deberías ver:
```
Mensaje recibido de ws302.sound.raw.v1
Evento procesado y enviado a Spark
```

### 3. Verificar que Spark recibe datos

En la **Terminal 1** (Spark), deberías ver:
```
Procesando batch de X eventos
Procesados X eventos de sonido
```

### 4. Verificar estadísticas del servidor Spark

```powershell
curl http://localhost:8082/stats
```

Deberías ver el tamaño de la cola y estadísticas.

---

## Solución de Problemas

### Spark no inicia

- Verifica que Java 11+ esté instalado: `java -version`
- Verifica que el archivo `.env` existe en `spark-etl/`
- Revisa los logs de error

### Listener no se conecta a Kafka

- Verifica que Kafka esté corriendo: `docker-compose ps`
- Verifica que el puerto 29092 esté accesible
- Revisa el archivo `.env` del listener-router

### Simulador no encuentra CSVs

- Verifica que los archivos estén en `data/csv/`
- Verifica la ruta en `simulator/.env`: `CSV_DIRECTORY=../data/csv`

### Listener no puede enviar a Spark

- Verifica que Spark esté corriendo en el puerto 8082
- Verifica `SPARK_HOST` y `SPARK_PORT` en `listener-router/.env` (debe ser 8082)
- Prueba: `curl http://localhost:8082/health`

---

## Flujo de Datos Esperado

```
CSV Files
    ↓
Simulador (cada 10s)
    ↓
Kafka (*.raw.v1)
    ↓
Listener/Router (enriquece)
    ↓
Spark HTTP API (/api/data)
    ↓
Spark ETL (procesa)
    ↓
MySQL (métricas) + MongoDB (lecturas)
```

---

## Detener el Sistema

Presiona `Ctrl+C` en cada terminal en orden inverso:
1. Simulador (Terminal 3)
2. Listener/Router (Terminal 2)
3. Spark ETL (Terminal 1)

Los servicios Docker seguirán corriendo. Para detenerlos:
```powershell
docker-compose down
```

---

## Próximos Pasos

Una vez que todo funcione:
- **FASE 6**: API Gateway con WebSockets
- **FASE 7**: Frontend React con dashboards

