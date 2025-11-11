# Script para detener procesos de Python relacionados con Spark ETL

Write-Host "`n=== DETENIENDO PROCESOS DE SPARK ===" -ForegroundColor Cyan

# Buscar procesos de Python relacionados con el proyecto
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*EmergentesETL*" -or 
    $_.Path -like "*venv*" -or
    (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | 
     Select-Object -ExpandProperty CommandLine) -like "*etl_main*"
}

if (-not $pythonProcs) {
    Write-Host "No se encontraron procesos de Python relacionados con Spark" -ForegroundColor Yellow
    exit 0
}

Write-Host "`nProcesos encontrados:" -ForegroundColor Yellow
foreach ($proc in $pythonProcs) {
    Write-Host "  PID: $($proc.Id) - $($proc.ProcessName) - $($proc.Path)" -ForegroundColor White
}

Write-Host "`n¿Deseas detener estos procesos? (S/N): " -NoNewline -ForegroundColor Yellow
$resp = Read-Host

if ($resp -eq "S" -or $resp -eq "s") {
    foreach ($proc in $pythonProcs) {
        try {
            Write-Host "Deteniendo PID $($proc.Id)..." -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force
            Write-Host "  ✓ Proceso $($proc.Id) detenido" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Error al detener proceso $($proc.Id): $_" -ForegroundColor Red
        }
    }
    
    # Verificar que se detuvieron
    Start-Sleep -Seconds 1
    $remaining = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -like "*EmergentesETL*" -or $_.Path -like "*venv*"
    }
    
    if (-not $remaining) {
        Write-Host "`n✓ Todos los procesos fueron detenidos correctamente" -ForegroundColor Green
    } else {
        Write-Host "`n⚠ Algunos procesos aún están activos:" -ForegroundColor Yellow
        foreach ($proc in $remaining) {
            Write-Host "  PID: $($proc.Id)" -ForegroundColor White
        }
    }
} else {
    Write-Host "`nOperación cancelada" -ForegroundColor Yellow
}

