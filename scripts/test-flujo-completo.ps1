# Script para probar el flujo completo del sistema ETL
# Uso: .\scripts\test-flujo-completo.ps1

Write-Host "`n=== PRUEBA DEL FLUJO COMPLETO ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar servicios Docker
Write-Host "1. Verificando servicios Docker..." -ForegroundColor Yellow
$services = docker-compose ps --format "{{.Name}}: {{.Status}}"
$healthyServices = $services | Select-String -Pattern "healthy|Up"
if ($healthyServices.Count -ge 5) {
    Write-Host "  ✓ Servicios Docker corriendo" -ForegroundColor Green
    $services | ForEach-Object { Write-Host "    $_" }
} else {
    Write-Host "  ✗ Algunos servicios no están corriendo" -ForegroundColor Red
    Write-Host "    Ejecuta: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Verificar tópicos Kafka
Write-Host "2. Verificando tópicos Kafka..." -ForegroundColor Yellow
$topics = docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>$null
$requiredTopics = @("em310.distance.raw.v1", "em500.air.raw.v1", "ws302.sound.raw.v1")
$allTopicsExist = $true

foreach ($topic in $requiredTopics) {
    if ($topics -match $topic) {
        Write-Host "  ✓ Tópico $topic existe" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Tópico $topic NO existe" -ForegroundColor Red
        $allTopicsExist = $false
    }
}

if (-not $allTopicsExist) {
    Write-Host "    Ejecuta: .\scripts\init-kafka-topics.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 3. Verificar archivos CSV
Write-Host "3. Verificando archivos CSV..." -ForegroundColor Yellow
$csvFiles = Get-ChildItem -Path "data\csv\*.csv" -ErrorAction SilentlyContinue
if ($csvFiles.Count -gt 0) {
    Write-Host "  ✓ Archivos CSV encontrados: $($csvFiles.Count)" -ForegroundColor Green
    $csvFiles | ForEach-Object { Write-Host "    - $($_.Name)" }
} else {
    Write-Host "  ✗ No se encontraron archivos CSV en data\csv\" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 4. Verificar configuración del simulador
Write-Host "4. Verificando configuración del simulador..." -ForegroundColor Yellow
if (Test-Path "simulator\.env") {
    Write-Host "  ✓ Archivo .env del simulador existe" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Archivo .env del simulador no existe" -ForegroundColor Yellow
    Write-Host "    Crea simulator\.env con:" -ForegroundColor Yellow
    Write-Host "    KAFKA_BOOTSTRAP_SERVERS=localhost:29092" -ForegroundColor Gray
    Write-Host "    CSV_DIRECTORY=../data/csv" -ForegroundColor Gray
}

Write-Host ""

# 5. Verificar configuración del listener-router
Write-Host "5. Verificando configuración del listener-router..." -ForegroundColor Yellow
if (Test-Path "listener-router\.env") {
    Write-Host "  ✓ Archivo .env del listener-router existe" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Archivo .env del listener-router no existe" -ForegroundColor Yellow
    Write-Host "    Crea listener-router\.env con:" -ForegroundColor Yellow
    Write-Host "    KAFKA_BOOTSTRAP_SERVERS=localhost:29092" -ForegroundColor Gray
    Write-Host "    SPARK_HOST=localhost" -ForegroundColor Gray
    Write-Host "    SPARK_PORT=8080" -ForegroundColor Gray
}

Write-Host ""

# 6. Verificar configuración de Spark
Write-Host "6. Verificando configuración de Spark..." -ForegroundColor Yellow
if (Test-Path "spark-etl\.env") {
    Write-Host "  ✓ Archivo .env de Spark existe" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Archivo .env de Spark no existe" -ForegroundColor Yellow
    Write-Host "    Crea spark-etl\.env (ver ENV_CONFIG.md)" -ForegroundColor Yellow
}

Write-Host ""

# 7. Resumen
Write-Host "=== RESUMEN ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para iniciar el flujo completo:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Terminal 1 - Spark ETL:" -ForegroundColor White
Write-Host "   cd spark-etl" -ForegroundColor Gray
Write-Host "   python src/main/python/etl_main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Terminal 2 - Listener/Router:" -ForegroundColor White
Write-Host "   cd listener-router" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Terminal 3 - Simulador:" -ForegroundColor White
Write-Host "   cd simulator" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Verificar mensajes en Kafka:" -ForegroundColor White
Write-Host "   docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ws302.sound.raw.v1 --from-beginning" -ForegroundColor Gray
Write-Host ""

