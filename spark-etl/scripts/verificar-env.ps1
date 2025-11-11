# Script para verificar la configuración del archivo .env

Write-Host "`n=== VERIFICACION DEL ARCHIVO .env ===" -ForegroundColor Cyan

$envFile = Join-Path $PSScriptRoot "..\.env"

if (-not (Test-Path $envFile)) {
    Write-Host "`n✗ ERROR: No se encontró el archivo .env" -ForegroundColor Red
    Write-Host "Ubicación esperada: $envFile" -ForegroundColor Yellow
    Write-Host "`nCrea el archivo .env en: spark-etl\.env" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✓ Archivo .env encontrado: $envFile" -ForegroundColor Green

# Leer el archivo .env
$envContent = Get-Content $envFile -Raw
$envLines = Get-Content $envFile

# Variables obligatorias
$requiredVars = @{
    "MYSQL_URI" = "URI completa de MySQL (ej: mysql://user:pass@host:port/db?ssl-mode=REQUIRED)"
    "MONGO_ATLAS_URI" = "URI completa de MongoDB Atlas (ej: mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true&w=majority)"
}

# Variables opcionales pero recomendadas
$optionalVars = @{
    "HTTP_PORT" = "8082"
    "LOG_LEVEL" = "INFO"
}

Write-Host "`n=== VARIABLES OBLIGATORIAS ===" -ForegroundColor Yellow
$allPresent = $true

foreach ($var in $requiredVars.Keys) {
    if ($envContent -match "$var\s*=") {
        # Extraer el valor (sin mostrar la contraseña completa)
        $line = $envLines | Where-Object { $_ -match "^$var\s*=" }
        if ($line) {
            $value = ($line -split '=', 2)[1].Trim()
            # Ocultar contraseñas
            if ($var -match "URI" -and $value -match "://.*:.*@") {
                $masked = $value -replace "://([^:]+):([^@]+)@", "://`$1:***@"
                Write-Host "  ✓ $var = $masked" -ForegroundColor Green
            } else {
                Write-Host "  ✓ $var = $value" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  ✗ $var - FALTA" -ForegroundColor Red
        Write-Host "    Descripción: $($requiredVars[$var])" -ForegroundColor Gray
        $allPresent = $false
    }
}

Write-Host "`n=== VARIABLES OPCIONALES ===" -ForegroundColor Yellow
foreach ($var in $optionalVars.Keys) {
    if ($envContent -match "$var\s*=") {
        $line = $envLines | Where-Object { $_ -match "^$var\s*=" }
        if ($line) {
            $value = ($line -split '=', 2)[1].Trim()
            Write-Host "  ✓ $var = $value" -ForegroundColor Green
        }
    } else {
        Write-Host "  ○ $var - No configurado (usará valor por defecto: $($optionalVars[$var]))" -ForegroundColor Gray
    }
}

Write-Host "`n=== RESUMEN ===" -ForegroundColor Cyan
if ($allPresent) {
    Write-Host "✓ Todas las variables obligatorias están presentes" -ForegroundColor Green
    Write-Host "`nTu configuración está lista para usar!" -ForegroundColor Green
    Write-Host "`nNOTA: Asegúrate de que:" -ForegroundColor Yellow
    Write-Host "  1. Las URIs contengan usuario, contraseña, host, puerto y base de datos" -ForegroundColor White
    Write-Host "  2. Las credenciales sean correctas" -ForegroundColor White
    Write-Host "  3. Las bases de datos existan (MySQL y MongoDB)" -ForegroundColor White
    exit 0
} else {
    Write-Host "✗ Faltan variables obligatorias" -ForegroundColor Red
    Write-Host "`nAgrega las variables faltantes a tu archivo .env" -ForegroundColor Yellow
    exit 1
}

