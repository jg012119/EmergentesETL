# Script para instalar winutils.exe usando Chocolatey
# Este es el método más fácil y automático

Write-Host "`n=== INSTALACION DE WINUTILS CON CHOCOLATEY ===" -ForegroundColor Cyan

# Verificar si Chocolatey está instalado
$chocoInstalled = $false
try {
    $chocoVersion = choco --version 2>$null
    if ($chocoVersion) {
        $chocoInstalled = $true
        Write-Host "`n✓ Chocolatey está instalado (versión: $chocoVersion)" -ForegroundColor Green
    }
} catch {
    $chocoInstalled = $false
}

if (-not $chocoInstalled) {
    Write-Host "`n✗ Chocolatey NO está instalado" -ForegroundColor Red
    Write-Host "`nVamos a instalarlo primero..." -ForegroundColor Yellow
    Write-Host "`nIMPORTANTE: Necesitas ejecutar PowerShell como Administrador" -ForegroundColor Red
    Write-Host "`nPresiona cualquier tecla para continuar con la instalación de Chocolatey..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    try {
        Write-Host "`nInstalando Chocolatey..." -ForegroundColor Cyan
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Verificar instalación
        $chocoVersion = choco --version
        Write-Host "`n✓ Chocolatey instalado exitosamente (versión: $chocoVersion)" -ForegroundColor Green
        $chocoInstalled = $true
    } catch {
        Write-Host "`n✗ Error al instalar Chocolatey:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host "`nSolución:" -ForegroundColor Yellow
        Write-Host "1. Abre PowerShell como Administrador" -ForegroundColor White
        Write-Host "2. Ejecuta este script nuevamente" -ForegroundColor White
        Write-Host "3. O instala Chocolatey manualmente desde: https://chocolatey.org/install" -ForegroundColor White
        exit 1
    }
}

# Instalar winutils
Write-Host "`n=== INSTALANDO WINUTILS ===" -ForegroundColor Cyan
Write-Host "Esto puede tardar unos minutos..." -ForegroundColor Yellow

try {
    choco install winutils -y
    
    Write-Host "`n✓ winutils.exe instalado exitosamente!" -ForegroundColor Green
    
    # Verificar ubicación
    $hadoopHome = $env:HADOOP_HOME
    if (-not $hadoopHome) {
        $hadoopHome = "$env:TEMP\hadoop_home"
    }
    
    $winutilsPath = Join-Path $hadoopHome "bin\winutils.exe"
    
    if (Test-Path $winutilsPath) {
        Write-Host "`n✓ winutils.exe encontrado en: $winutilsPath" -ForegroundColor Green
        $fileSize = (Get-Item $winutilsPath).Length / 1KB
        Write-Host "  Tamaño: $fileSize KB" -ForegroundColor White
    } else {
        Write-Host "`n⚠ winutils.exe no encontrado en la ubicación esperada" -ForegroundColor Yellow
        Write-Host "  Buscando en otras ubicaciones..." -ForegroundColor Yellow
        
        # Buscar en ubicaciones comunes
        $commonPaths = @(
            "C:\ProgramData\chocolatey\lib\winutils",
            "C:\tools\hadoop",
            "$env:USERPROFILE\hadoop"
        )
        
        $found = $false
        foreach ($path in $commonPaths) {
            $testPath = Join-Path $path "bin\winutils.exe"
            if (Test-Path $testPath) {
                Write-Host "  ✓ Encontrado en: $testPath" -ForegroundColor Green
                $found = $true
                break
            }
        }
        
        if (-not $found) {
            Write-Host "  ✗ No se encontró en ubicaciones comunes" -ForegroundColor Red
            Write-Host "`nVerifica la instalación con: choco list winutils" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n=== COMPLETADO ===" -ForegroundColor Green
    Write-Host "`nAhora puedes reiniciar Spark y debería funcionar correctamente." -ForegroundColor Cyan
    
} catch {
    Write-Host "`n✗ Error al instalar winutils:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nSolución alternativa:" -ForegroundColor Yellow
    Write-Host "1. Verifica que Chocolatey esté funcionando: choco --version" -ForegroundColor White
    Write-Host "2. Intenta manualmente: choco install winutils -y" -ForegroundColor White
    Write-Host "3. O descarga manualmente desde GitHub (ver INSTALAR_WINUTILS.md)" -ForegroundColor White
    exit 1
}

