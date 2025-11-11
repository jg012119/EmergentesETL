# Script para limpiar puertos ocupados

param(
    [int]$Port = 8081
)

Write-Host "=== Limpieza de Puerto $Port ===" -ForegroundColor Cyan

# Obtener procesos que usan el puerto
$connections = netstat -ano | findstr ":$Port" | findstr "LISTENING"

if (-not $connections) {
    Write-Host "Puerto $Port esta LIBRE" -ForegroundColor Green
    exit 0
}

Write-Host "`nPuerto $Port esta OCUPADO:" -ForegroundColor Yellow
Write-Host $connections

# Extraer PIDs
$processIds = @()
foreach ($line in $connections) {
    $match = $line | Select-String -Pattern "LISTENING\s+(\d+)"
    if ($match) {
        $processId = $match.Matches.Groups[1].Value
        if ($processId -and $processId -notin $processIds) {
            $processIds += $processId
        }
    }
}

if ($processIds.Count -eq 0) {
    Write-Host "`nNo se pudieron identificar los procesos" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nProcesos encontrados:" -ForegroundColor Yellow
foreach ($processId in $processIds) {
    $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "  PID: $processId - $($proc.ProcessName) - $($proc.Path)" -ForegroundColor White
    } else {
        Write-Host "  PID: $processId - (proceso no encontrado)" -ForegroundColor Yellow
    }
}

Write-Host "`nDeseas detener estos procesos? (S/N): " -NoNewline -ForegroundColor Yellow
$resp = Read-Host

if ($resp -eq "S" -or $resp -eq "s") {
    foreach ($processId in $processIds) {
        try {
            $proc = Get-Process -Id $processId -ErrorAction Stop
            Stop-Process -Id $processId -Force
            Write-Host "  Proceso $processId ($($proc.ProcessName)) detenido" -ForegroundColor Green
        } catch {
            $errorMsg = $_.Exception.Message
            Write-Host "  No se pudo detener el proceso $processId : $errorMsg" -ForegroundColor Red
        }
    }
    
    # Esperar un momento y verificar
    Start-Sleep -Seconds 2
    $stillOccupied = netstat -ano | findstr ":$Port" | findstr "LISTENING"
    if (-not $stillOccupied) {
        Write-Host "`nPuerto $Port liberado correctamente" -ForegroundColor Green
    } else {
        Write-Host "`nEl puerto $Port aun esta ocupado (puede estar en estado TIME_WAIT)" -ForegroundColor Yellow
        Write-Host "   Espera unos segundos y vuelve a intentar" -ForegroundColor White
    }
} else {
    Write-Host "`nOperacion cancelada" -ForegroundColor Yellow
}
