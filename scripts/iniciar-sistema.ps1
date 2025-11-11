# Script para iniciar todo el sistema ETL
# Este script te guiará paso a paso para iniciar todos los componentes

Write-Host "`n=== INICIANDO SISTEMA ETL ===" -ForegroundColor Cyan
Write-Host "Este script te guiará para iniciar todos los componentes" -ForegroundColor Yellow

# Verificar prerequisitos
Write-Host "`n=== VERIFICANDO PREREQUISITOS ===" -ForegroundColor Cyan

# 1. Verificar Docker
$dockerRunning = $false
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✓ Docker instalado" -ForegroundColor Green
        $dockerRunning = $true
    }
} catch {
    Write-Host "✗ Docker no encontrado" -ForegroundColor Red
}

# 2. Verificar que Docker Compose esté corriendo
if ($dockerRunning) {
    try {
        $dockerPs = docker ps 2>$null
        if ($dockerPs -match "kafka") {
            Write-Host "✓ Kafka está corriendo" -ForegroundColor Green
        } else {
            Write-Host "⚠ Kafka no está corriendo" -ForegroundColor Yellow
            Write-Host "  Iniciando Docker Compose..." -ForegroundColor Yellow
            docker-compose up -d
            Start-Sleep -Seconds 5
        }
    } catch {
        Write-Host "⚠ Error verificando Docker" -ForegroundColor Yellow
    }
}

# 3. Verificar winutils.exe
$winutilsPath = "$env:TEMP\hadoop_home\bin\winutils.exe"
if (Test-Path $winutilsPath) {
    Write-Host "✓ winutils.exe encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠ winutils.exe no encontrado" -ForegroundColor Yellow
    Write-Host "  Ejecuta: .\spark-etl\scripts\descargar-winutils-directo.ps1" -ForegroundColor Cyan
}

# 4. Verificar archivos .env
$sparkEnv = "spark-etl\.env"
$listenerEnv = "listener-router\.env"
$simulatorEnv = "simulator\.env"

$envFilesOk = $true
if (-not (Test-Path $sparkEnv)) {
    Write-Host "✗ spark-etl\.env no encontrado" -ForegroundColor Red
    $envFilesOk = $false
} else {
    Write-Host "✓ spark-etl\.env encontrado" -ForegroundColor Green
}

if (-not (Test-Path $listenerEnv)) {
    Write-Host "⚠ listener-router\.env no encontrado (puede tener valores por defecto)" -ForegroundColor Yellow
} else {
    Write-Host "✓ listener-router\.env encontrado" -ForegroundColor Green
}

if (-not (Test-Path $simulatorEnv)) {
    Write-Host "⚠ simulator\.env no encontrado (puede tener valores por defecto)" -ForegroundColor Yellow
} else {
    Write-Host "✓ simulator\.env encontrado" -ForegroundColor Green
}

Write-Host "`n=== INSTRUCCIONES DE INICIO ===" -ForegroundColor Cyan
Write-Host "`nAbre 3 terminales PowerShell y ejecuta en este orden:" -ForegroundColor Yellow

Write-Host "`n1. TERMINAL 1 - Spark ETL:" -ForegroundColor Green
Write-Host "   cd spark-etl" -ForegroundColor White
Write-Host "   python src/main/python/etl_main.py" -ForegroundColor Cyan
Write-Host "   `n   Espera a ver: 'Spark session creada' y 'Servidor HTTP iniciado'" -ForegroundColor Gray
Write-Host "   Luego verifica: curl http://localhost:8082/health" -ForegroundColor Gray

Write-Host "`n2. TERMINAL 2 - Listener/Router:" -ForegroundColor Green
Write-Host "   cd listener-router" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host "   `n   Espera a ver: 'Conectado a Kafka' y 'Listener/Router corriendo'" -ForegroundColor Gray

Write-Host "`n3. TERMINAL 3 - Simulador:" -ForegroundColor Green
Write-Host "   cd simulator" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host "   `n   Espera a ver: 'CSV cargado' y 'Iniciando simulación...'" -ForegroundColor Gray

Write-Host "`n=== FLUJO DE DATOS ===" -ForegroundColor Cyan
Write-Host "CSV → Simulador → Kafka → Listener → Spark → MySQL + MongoDB" -ForegroundColor White

Write-Host "`n=== VERIFICACION ===" -ForegroundColor Cyan
Write-Host "Después de iniciar todo, verifica:" -ForegroundColor Yellow
Write-Host "  1. Spark recibe datos: Deberías ver 'Procesando batch de X eventos'" -ForegroundColor White
Write-Host "  2. Listener procesa: Deberías ver 'Mensaje recibido' y 'enviado a Spark'" -ForegroundColor White
Write-Host "  3. Simulador envía: Deberías ver mensajes cada 10 segundos" -ForegroundColor White

Write-Host "`n=== DETENER SISTEMA ===" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C en cada terminal (en orden inverso):" -ForegroundColor Yellow
Write-Host "  1. Simulador (Terminal 3)" -ForegroundColor White
Write-Host "  2. Listener (Terminal 2)" -ForegroundColor White
Write-Host "  3. Spark (Terminal 1)" -ForegroundColor White

Write-Host "`n¡Listo para iniciar! Abre las 3 terminales y sigue los pasos." -ForegroundColor Green

