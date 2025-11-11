# Spark ETL - Procesamiento de Datos IoT

Aplicación Spark que recibe datos del Listener/Router, realiza ETL, análisis probabilístico y escribe a MySQL y MongoDB.

## Estructura

```
spark-etl/
├── src/main/python/
│   ├── etl_main.py              # Aplicación principal
│   ├── config.py                # Configuración
│   ├── http_server.py           # Servidor HTTP para recibir datos
│   ├── processors/              # Procesadores por tipo de sensor
│   │   ├── base_processor.py
│   │   ├── sound_processor.py
│   │   ├── distance_processor.py
│   │   └── air_processor.py
│   └── sinks/                   # Escritores a bases de datos
│       ├── mysql_sink.py
│       └── mongodb_sink.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Instalación

### Local (sin Docker)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env según tu configuración

# Ejecutar
python src/main/python/etl_main.py
```

### Docker

```bash
# Construir imagen
docker build -t spark-etl .

# Ejecutar
docker run -p 8080:8080 --env-file .env spark-etl
```

## Configuración

Ver `.env.example` para todas las variables de entorno disponibles.

## Endpoints HTTP

- `POST /api/data` - Recibe un evento individual
- `POST /api/data/batch` - Recibe un batch de eventos
- `GET /health` - Health check
- `GET /stats` - Estadísticas del servidor

## Procesamiento

1. **Recepción**: El servidor HTTP recibe eventos del Listener/Router
2. **Validación**: Se validan y limpian los datos según el tipo de sensor
3. **Ventaneo**: Se aplican ventanas deslizantes (1 min, slide 10s)
4. **Agregación**: Se calculan métricas agregadas
5. **Escritura**: Se escriben a MySQL (métricas) y MongoDB (lecturas)

## Notas

- Los escritores a MySQL y MongoDB están comentados inicialmente hasta que se configuren los conectores
- El procesamiento usa una cola en memoria (events_queue) - en producción usar una cola más robusta
- Los modelos probabilísticos (Gaussiano, EWMA, AR1) se implementarán en una fase posterior

