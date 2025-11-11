# Script de diagnóstico para conexión Spark-Listener

Write-Host "=== Diagnóstico de Conexión Spark-Listener ===" -ForegroundColor Cyan

# 1. Verificar puertos
Write-Host "`n1. Verificación de Puertos:" -ForegroundColor Yellow

$port8080 = netstat -ano | findstr :8080 | Select-String "LISTENING"
$port8081 = netstat -ano | findstr :8081 | Select-String "LISTENING"

if ($port8080) {
    Write-Host "  ⚠️  Puerto 8080: OCUPADO" -ForegroundColor Red
    $pid8080 = ($port8080 | Select-String -Pattern "LISTENING\s+(\d+)").Matches.Groups[1].Value
    if ($pid8080) {
        $proc = Get-Process -Id $pid8080 -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "     Proceso: $($proc.ProcessName) (PID: $pid8080)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ✓ Puerto 8080: LIBRE" -ForegroundColor Green
}

if ($port8081) {
    Write-Host "  ⚠️  Puerto 8081: OCUPADO" -ForegroundColor Red
    $pid8081 = ($port8081 | Select-String -Pattern "LISTENING\s+(\d+)").Matches.Groups[1].Value
    if ($pid8081) {
        $proc = Get-Process -Id $pid8081 -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "     Proceso: $($proc.ProcessName) (PID: $pid8081)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ✓ Puerto 8081: LIBRE" -ForegroundColor Green
}

# 2. Verificar configuración de Spark
Write-Host "`n2. Configuración de Spark:" -ForegroundColor Yellow
$sparkConfig = Get-Content "spark-etl\src\main\python\config.py" | Select-String "HTTP_PORT"
if ($sparkConfig) {
    Write-Host "  $sparkConfig" -ForegroundColor White
}

# 3. Verificar configuración de Listener
Write-Host "`n3. Configuración de Listener:" -ForegroundColor Yellow
$listenerConfig = Get-Content "listener-router\src\config.ts" | Select-String "port:"
if ($listenerConfig) {
    Write-Host "  $listenerConfig" -ForegroundColor White
}

# 4. Probar conexión HTTP
Write-Host "`n4. Prueba de Conexión:" -ForegroundColor Yellow

# Probar puerto 8080
try {
    $response8080 = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Puerto 8080: Servidor respondiendo" -ForegroundColor Green
    Write-Host "     Status: $($response8080.StatusCode)" -ForegroundColor White
} catch {
    Write-Host "  ✗ Puerto 8080: No responde" -ForegroundColor Red
}

# Probar puerto 8081
try {
    $response8081 = Invoke-WebRequest -Uri "http://localhost:8081/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Puerto 8081: Servidor respondiendo" -ForegroundColor Green
    Write-Host "     Status: $($response8081.StatusCode)" -ForegroundColor White
    $body = $response8081.Content | ConvertFrom-Json
    Write-Host "     Queue size: $($body.queue_size)" -ForegroundColor White
} catch {
    Write-Host "  ✗ Puerto 8081: No responde" -ForegroundColor Red
}

# 5. Verificar procesos Python/Spark
Write-Host "`n5. Procesos Python/Spark:" -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    foreach ($proc in $pythonProcs) {
        Write-Host "  Python (PID: $($proc.Id)) - $($proc.Path)" -ForegroundColor White
    }
} else {
    Write-Host "  No hay procesos Python corriendo" -ForegroundColor Yellow
}

Write-Host "`n=== Diagnóstico completado ===" -ForegroundColor Cyan
Write-Host "`nRecomendaciones:" -ForegroundColor Yellow
Write-Host "  1. Si el puerto 8081 está ocupado, detén el proceso con: Stop-Process -Id <PID> -Force" -ForegroundColor White
Write-Host "  2. Reinicia Spark después de liberar el puerto" -ForegroundColor White
Write-Host "  3. Verifica que el listener-router esté configurado para usar el puerto 8081" -ForegroundColor White

