# DB Writer - Servicio de Escritura a Bases de Datos

Microservicio que recibe datos procesados de Spark y los escribe a MySQL y MongoDB usando drivers nativos de Node.js.

## Funcionalidad

1. **Recibe métricas de Spark**: Endpoint `/api/metrics` para escribir métricas agregadas a MySQL
2. **Recibe lecturas de Spark**: Endpoint `/api/readings` para escribir lecturas limpias a MongoDB
3. **Escritura robusta**: Manejo de errores que permite que el sistema continúe funcionando

## Instalación

```bash
npm install
```

## Configuración

Copia `.env.example` a `.env` y configura las variables de entorno:

```bash
cp .env.example .env
```

Variables importantes:
- `MYSQL_URI`: URI completa de MySQL (o usa parámetros individuales)
- `MONGO_ATLAS_URI`: URI completa de MongoDB Atlas (o usa parámetros individuales)
- `PORT`: Puerto del servidor (default: 3001)

## Uso

### Desarrollo

```bash
npm run dev
```

### Producción

```bash
npm run build
npm start
```

## Endpoints

### POST /api/metrics

Escribe métricas agregadas a MySQL.

**Body:**
```json
{
  "table": "sound_metrics_1m",
  "metrics": [
    {
      "sensor_id": "WS302-001",
      "window_start": "2024-11-10T16:00:00Z",
      "window_end": "2024-11-10T16:01:00Z",
      "laeq_avg": 68.5,
      "p95_laeq": 72.3,
      "alert_prob": 0.15
    }
  ]
}
```

### POST /api/readings

Escribe lecturas limpias a MongoDB.

**Body:**
```json
{
  "collection": "sound_readings_clean",
  "readings": [
    {
      "sensor_id": "WS302-001",
      "ts_utc": "2024-11-10T16:00:15Z",
      "laeq": 68.5,
      "model": "WS302"
    }
  ]
}
```

### GET /health

Health check del servicio.

## Estructura

```
db-writer/
├── src/
│   ├── index.ts              # Servidor Express y endpoints
│   ├── config.ts             # Configuración
│   ├── logger.ts              # Logger
│   ├── mysql-client.ts        # Cliente MySQL
│   └── mongodb-client.ts       # Cliente MongoDB
├── package.json
├── tsconfig.json
└── README.md
```

## Ventajas

- ✅ No requiere Python workers (evita problemas en Windows)
- ✅ Drivers nativos de Node.js (más rápidos y estables)
- ✅ Manejo robusto de errores
- ✅ Escritura asíncrona no bloqueante
- ✅ Pool de conexiones para mejor rendimiento

