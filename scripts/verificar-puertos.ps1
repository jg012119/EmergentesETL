# Script para verificar y limpiar puertos ocupados

Write-Host "=== Verificación de Puertos ===" -ForegroundColor Cyan

# Verificar puerto 8080
Write-Host "`nPuerto 8080:" -ForegroundColor Yellow
$port8080 = netstat -ano | findstr :8080
if ($port8080) {
    Write-Host "  ⚠️  Puerto 8080 está OCUPADO" -ForegroundColor Red
    Write-Host $port8080
    $pid8080 = ($port8080 | Select-String -Pattern "LISTENING\s+(\d+)").Matches.Groups[1].Value
    if ($pid8080) {
        $proc8080 = Get-Process -Id $pid8080 -ErrorAction SilentlyContinue
        if ($proc8080) {
            Write-Host "  Proceso: $($proc8080.ProcessName) (PID: $pid8080)" -ForegroundColor Yellow
            Write-Host "  ¿Deseas detenerlo? (S/N): " -NoNewline -ForegroundColor Yellow
            $resp = Read-Host
            if ($resp -eq "S" -or $resp -eq "s") {
                Stop-Process -Id $pid8080 -Force
                Write-Host "  ✓ Proceso detenido" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "  ✓ Puerto 8080 está LIBRE" -ForegroundColor Green
}

# Verificar puerto 8081
Write-Host "`nPuerto 8081:" -ForegroundColor Yellow
$port8081 = netstat -ano | findstr :8081
if ($port8081) {
    Write-Host "  ⚠️  Puerto 8081 está OCUPADO" -ForegroundColor Red
    Write-Host $port8081
    $pid8081 = ($port8081 | Select-String -Pattern "LISTENING\s+(\d+)").Matches.Groups[1].Value
    if ($pid8081) {
        $proc8081 = Get-Process -Id $pid8081 -ErrorAction SilentlyContinue
        if ($proc8081) {
            Write-Host "  Proceso: $($proc8081.ProcessName) (PID: $pid8081)" -ForegroundColor Yellow
            Write-Host "  ¿Deseas detenerlo? (S/N): " -NoNewline -ForegroundColor Yellow
            $resp = Read-Host
            if ($resp -eq "S" -or $resp -eq "s") {
                Stop-Process -Id $pid8081 -Force
                Write-Host "  ✓ Proceso detenido" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "  ✓ Puerto 8081 está LIBRE" -ForegroundColor Green
}

Write-Host "`n=== Verificación completada ===" -ForegroundColor Cyan

