# Script para descargar winutils.exe para Spark en Windows
# Este script descarga winutils.exe desde un repositorio confiable

Write-Host "`n=== DESCARGANDO WINUTILS.EXE ===" -ForegroundColor Cyan

# Versiones compatibles con Spark 3.5.0 (intentar desde la más reciente)
$hadoopVersions = @("3.3.5", "3.3.4", "3.3.3", "3.3.2", "3.3.1", "3.3.0")
$hadoopHome = Join-Path $env:TEMP "hadoop_home"
$binDir = Join-Path $hadoopHome "bin"
$winutilsPath = Join-Path $binDir "winutils.exe"

# Crear directorios si no existen
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    Write-Host "Directorio creado: $binDir" -ForegroundColor Green
}

# Verificar si ya existe
if (Test-Path $winutilsPath) {
    Write-Host "`n✓ winutils.exe ya existe en: $winutilsPath" -ForegroundColor Green
    Write-Host "Tamaño: $((Get-Item $winutilsPath).Length / 1KB) KB" -ForegroundColor Gray
    exit 0
}

Write-Host "`nDescargando winutils.exe..." -ForegroundColor Yellow
Write-Host "Destino: $winutilsPath" -ForegroundColor Gray

$downloadSuccess = $false
$lastError = $null
$successfulVersion = $null

# Intentar múltiples versiones de Hadoop (desde la más reciente)
foreach ($hadoopVersion in $hadoopVersions) {
    Write-Host "`nIntentando versión Hadoop $hadoopVersion..." -ForegroundColor Gray
    
    # Intentar múltiples URLs para cada versión
    $winutilsUrls = @(
        "https://github.com/cdarlint/winutils/raw/master/hadoop-$hadoopVersion/bin/winutils.exe",
        "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-$hadoopVersion/bin/winutils.exe"
    )
    
    foreach ($winutilsUrl in $winutilsUrls) {
        try {
            # Descargar winutils.exe
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $winutilsUrl -OutFile $winutilsPath -ErrorAction Stop
            $downloadSuccess = $true
            $successfulVersion = $hadoopVersion
            break
        } catch {
            $lastError = $_.Exception.Message
            continue
        }
    }
    
    if ($downloadSuccess) {
        break
    }
}

if ($downloadSuccess) {
    
    if (Test-Path $winutilsPath) {
        $fileSize = (Get-Item $winutilsPath).Length / 1KB
        Write-Host "`n✓ winutils.exe descargado exitosamente!" -ForegroundColor Green
        Write-Host "  Versión Hadoop: $successfulVersion" -ForegroundColor White
        Write-Host "  Ubicación: $winutilsPath" -ForegroundColor White
        Write-Host "  Tamaño: $fileSize KB" -ForegroundColor White
        
        # Configurar HADOOP_HOME
        $env:HADOOP_HOME = $hadoopHome
        Write-Host "`n✓ HADOOP_HOME configurado: $hadoopHome" -ForegroundColor Green
        Write-Host "`nNOTA: Esta variable de entorno es solo para esta sesión." -ForegroundColor Yellow
        Write-Host "Para hacerla permanente, ejecuta:" -ForegroundColor Yellow
        Write-Host "  [System.Environment]::SetEnvironmentVariable('HADOOP_HOME', '$hadoopHome', 'User')" -ForegroundColor Cyan
    } else {
        Write-Host "`n✗ Error: El archivo no se descargó correctamente" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n✗ Error: No se pudo descargar winutils.exe desde ninguna URL" -ForegroundColor Red
    Write-Host "Último error: $lastError" -ForegroundColor Red
    Write-Host "`n=== SOLUCIÓN MANUAL ===" -ForegroundColor Yellow
    Write-Host "1. Visita: https://github.com/cdarlint/winutils" -ForegroundColor White
    Write-Host "2. Navega a una de estas carpetas:" -ForegroundColor White
    foreach ($ver in $hadoopVersions) {
        Write-Host "   - hadoop-$ver/bin/" -ForegroundColor Gray
    }
    Write-Host "3. Descarga: winutils.exe" -ForegroundColor White
    Write-Host "4. Colócalo en: $winutilsPath" -ForegroundColor White
    Write-Host "`nO usa WSL/Docker para evitar este problema en Windows." -ForegroundColor Cyan
    exit 1
}

Write-Host "`n=== COMPLETADO ===" -ForegroundColor Green

