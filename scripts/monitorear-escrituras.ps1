# Script para monitorear las escrituras de datos
# Verifica que Spark esté enviando datos al db-writer

Write-Host "`n=== MONITOREO DE ESCRITURAS ===" -ForegroundColor Cyan
Write-Host "Este script verifica que los datos fluyan correctamente`n" -ForegroundColor Yellow

# Verificar db-writer
Write-Host "1. Verificando db-writer..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    $json = $response.Content | ConvertFrom-Json
    Write-Host "   ✓ db-writer está corriendo" -ForegroundColor Green
    Write-Host "   Status: $($json.status)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ db-writer no está respondiendo" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar: cd db-writer; npm run dev" -ForegroundColor Yellow
    exit 1
}

# Verificar Spark HTTP
Write-Host "`n2. Verificando Spark HTTP..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8082/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✓ Spark HTTP está respondiendo" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Spark HTTP no está respondiendo" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar: cd spark-etl; python src/main/python/etl_main.py" -ForegroundColor Yellow
    exit 1
}

# Verificar procesos
Write-Host "`n3. Verificando procesos..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue

if ($pythonProcs) {
    Write-Host "   ✓ Spark está corriendo (PID: $($pythonProcs[0].Id))" -ForegroundColor Green
} else {
    Write-Host "   ✗ Spark no está corriendo" -ForegroundColor Red
}

if ($nodeProcs) {
    Write-Host "   ✓ Node.js está corriendo (probablemente db-writer)" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Node.js no está corriendo" -ForegroundColor Yellow
}

# Verificar puertos
Write-Host "`n4. Verificando puertos..." -ForegroundColor Yellow
$port3001 = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
$port8082 = Get-NetTCPConnection -LocalPort 8082 -ErrorAction SilentlyContinue

if ($port3001) {
    Write-Host "   ✓ Puerto 3001 en uso (db-writer)" -ForegroundColor Green
} else {
    Write-Host "   ✗ Puerto 3001 libre" -ForegroundColor Red
}

if ($port8082) {
    Write-Host "   ✓ Puerto 8082 en uso (Spark HTTP)" -ForegroundColor Green
} else {
    Write-Host "   ✗ Puerto 8082 libre" -ForegroundColor Red
}

Write-Host "`n=== INSTRUCCIONES ===" -ForegroundColor Cyan
Write-Host "Para ver los logs de escritura:" -ForegroundColor Yellow
Write-Host "  1. Revisa la terminal de Spark para ver:" -ForegroundColor White
Write-Host "     - 'Métricas enviadas a db-writer: ...'" -ForegroundColor Gray
Write-Host "     - 'Lecturas enviadas a db-writer: ...'" -ForegroundColor Gray
Write-Host "  2. Revisa la terminal de db-writer para ver:" -ForegroundColor White
Write-Host "     - 'Recibidas métricas para ...'" -ForegroundColor Gray
Write-Host "     - 'Recibidas lecturas para ...'" -ForegroundColor Gray
Write-Host "     - 'Escritas X métricas en MySQL...'" -ForegroundColor Gray
Write-Host "     - 'Escritas X lecturas en MongoDB...'" -ForegroundColor Gray
Write-Host "`nPara verificar datos en las bases de datos:" -ForegroundColor Yellow
Write-Host "  - MySQL: Consulta las tablas sound_metrics_1m, air_metrics_1m, etc." -ForegroundColor White
Write-Host "  - MongoDB: Consulta las colecciones sound_readings_clean, etc." -ForegroundColor White

Write-Host "`n✓ Monitoreo completado" -ForegroundColor Green

