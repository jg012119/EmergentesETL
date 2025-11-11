# Script PowerShell para inicializar los tópicos de Kafka en Windows
# Uso: .\scripts\init-kafka-topics.ps1

$KAFKA_BOOTSTRAP_SERVER = if ($env:KAFKA_BOOTSTRAP_SERVER) { $env:KAFKA_BOOTSTRAP_SERVER } else { "localhost:29092" }

Write-Host "Inicializando tópicos de Kafka en ${KAFKA_BOOTSTRAP_SERVER}..." -ForegroundColor Cyan

# Función para crear un tópico
function Create-Topic {
    param(
        [string]$TopicName,
        [int]$Partitions = 3,
        [long]$Retention = 604800000  # 7 días en milisegundos
    )
    
    Write-Host "Creando tópico: ${TopicName}" -ForegroundColor Yellow
    
    docker exec kafka kafka-topics `
        --create `
        --bootstrap-server localhost:9092 `
        --topic "${TopicName}" `
        --partitions "${Partitions}" `
        --replication-factor 1 `
        --config retention.ms="${Retention}" `
        --if-not-exists
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Tópico ${TopicName} creado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Tópico ${TopicName} ya existe o error al crearlo" -ForegroundColor Yellow
    }
}

# Verificar que Kafka está corriendo
$kafkaRunning = docker ps --filter "name=kafka" --format "{{.Names}}"
if (-not $kafkaRunning) {
    Write-Host "❌ Error: Kafka no está corriendo. Por favor inicia los servicios con: docker-compose up -d" -ForegroundColor Red
    exit 1
}

# Tópicos raw (datos sin procesar desde el simulador)
Create-Topic -TopicName "em310.distance.raw.v1" -Partitions 3 -Retention 604800000
Create-Topic -TopicName "em500.air.raw.v1" -Partitions 3 -Retention 604800000
Create-Topic -TopicName "ws302.sound.raw.v1" -Partitions 3 -Retention 604800000

Write-Host ""
Write-Host "Creando tópicos para datos procesados (Spark -> db-writer)..." -ForegroundColor Cyan

# Tópicos procesados (datos procesados por Spark para db-writer)
# Métricas agregadas para MySQL
Create-Topic -TopicName "processed.metrics.v1" -Partitions 3 -Retention 604800000
# Lecturas limpias para MongoDB
Create-Topic -TopicName "processed.readings.v1" -Partitions 3 -Retention 604800000

Write-Host ""
Write-Host "✓ Tópicos creados exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "Tópicos disponibles:" -ForegroundColor Cyan
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

