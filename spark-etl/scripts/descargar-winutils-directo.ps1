# Script para descargar winutils.exe directamente desde GitHub
# No requiere permisos de administrador ni Chocolatey

Write-Host "`n=== DESCARGANDO WINUTILS.EXE DIRECTAMENTE ===" -ForegroundColor Cyan

$hadoopHome = Join-Path $env:TEMP "hadoop_home"
$binDir = Join-Path $hadoopHome "bin"
$winutilsPath = Join-Path $binDir "winutils.exe"

# Crear directorios si no existen
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    Write-Host "✓ Directorio creado: $binDir" -ForegroundColor Green
}

# Verificar si ya existe
if (Test-Path $winutilsPath) {
    Write-Host "`n✓ winutils.exe ya existe en: $winutilsPath" -ForegroundColor Green
    $fileSize = (Get-Item $winutilsPath).Length / 1KB
    Write-Host "  Tamaño: $fileSize KB" -ForegroundColor Gray
    exit 0
}

# Versiones a intentar (desde la más reciente)
$hadoopVersions = @("3.3.5", "3.3.4", "3.3.3", "3.3.2", "3.3.1", "3.3.0")

Write-Host "`nDescargando winutils.exe..." -ForegroundColor Yellow
Write-Host "Destino: $winutilsPath" -ForegroundColor Gray

$downloadSuccess = $false
$successfulVersion = $null

# Intentar múltiples versiones
foreach ($hadoopVersion in $hadoopVersions) {
    Write-Host "`nIntentando versión Hadoop $hadoopVersion..." -ForegroundColor Gray
    
    # URLs posibles para esta versión
    $urls = @(
        "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-$hadoopVersion/bin/winutils.exe",
        "https://github.com/cdarlint/winutils/raw/master/hadoop-$hadoopVersion/bin/winutils.exe"
    )
    
    foreach ($url in $urls) {
        try {
            Write-Host "  Intentando: $url" -ForegroundColor DarkGray
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $url -OutFile $winutilsPath -ErrorAction Stop
            
            if (Test-Path $winutilsPath) {
                $fileSize = (Get-Item $winutilsPath).Length
                if ($fileSize -gt 0) {
                    $downloadSuccess = $true
                    $successfulVersion = $hadoopVersion
                    Write-Host "  ✓ Descarga exitosa!" -ForegroundColor Green
                    break
                } else {
                    Remove-Item $winutilsPath -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {
            Write-Host "  ✗ Falló" -ForegroundColor DarkRed
            continue
        }
    }
    
    if ($downloadSuccess) {
        break
    }
}

if ($downloadSuccess) {
    $fileSize = (Get-Item $winutilsPath).Length / 1KB
    Write-Host "`n✓ winutils.exe descargado exitosamente!" -ForegroundColor Green
    Write-Host "  Versión Hadoop: $successfulVersion" -ForegroundColor White
    Write-Host "  Ubicación: $winutilsPath" -ForegroundColor White
    Write-Host "  Tamaño: $fileSize KB" -ForegroundColor White
    
    # Configurar HADOOP_HOME para esta sesión
    $env:HADOOP_HOME = $hadoopHome
    Write-Host "`n✓ HADOOP_HOME configurado: $hadoopHome" -ForegroundColor Green
    
    Write-Host "`n=== COMPLETADO ===" -ForegroundColor Green
    Write-Host "`nAhora puedes reiniciar Spark y debería funcionar correctamente." -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`n✗ No se pudo descargar winutils.exe desde ninguna URL" -ForegroundColor Red
    Write-Host "`n=== SOLUCIÓN MANUAL ===" -ForegroundColor Yellow
    Write-Host "1. Visita: https://github.com/cdarlint/winutils" -ForegroundColor White
    Write-Host "2. Navega a: hadoop-3.3.5/bin/" -ForegroundColor White
    Write-Host "3. Haz clic en 'winutils.exe'" -ForegroundColor White
    Write-Host "4. Haz clic en el botón 'Download' o 'Raw'" -ForegroundColor White
    Write-Host "5. Guarda el archivo en: $winutilsPath" -ForegroundColor White
    exit 1
}

