# Guía para Instalar winutils.exe en Windows

## 🔧 Problema

Spark requiere `winutils.exe` en Windows para realizar operaciones de archivos. Sin este archivo, Spark falla con el error:

```
Could not locate Hadoop executable: C:\Users\...\hadoop_home\bin\winutils.exe
```

## ✅ Solución: Instalar winutils.exe

### Opción 1: Descarga Automática con Script (⭐ RECOMENDADO - Más Fácil)

**No requiere permisos de administrador ni Chocolatey**

Ejecuta este script desde PowerShell:

```powershell
.\spark-etl\scripts\descargar-winutils-directo.ps1
```

O con la ruta completa:

```powershell
& "C:\Users\jg012\Downloads\EmergentesETL\spark-etl\scripts\descargar-winutils-directo.ps1"
```

Este script:
- Descarga automáticamente `winutils.exe` desde GitHub
- Lo coloca en la ubicación correcta
- Configura `HADOOP_HOME` automáticamente
- No requiere permisos de administrador

### Opción 2: Usar Chocolatey (Requiere permisos de administrador)

Esta es la forma más sencilla y automática de instalar `winutils.exe`.

#### Paso 1: Instalar Chocolatey (si no lo tienes)

Abre PowerShell **como Administrador** y ejecuta:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### Paso 2: Instalar winutils

Una vez instalado Chocolatey, ejecuta:

```powershell
choco install winutils -y
```

Esto instalará automáticamente `winutils.exe` en la ubicación correcta y configurará `HADOOP_HOME`.

#### Verificación

Después de instalar, verifica:

```powershell
Test-Path "$env:HADOOP_HOME\bin\winutils.exe"
```

O si `HADOOP_HOME` no está configurado:

```powershell
Test-Path "$env:TEMP\hadoop_home\bin\winutils.exe"
```

### Opción 2: Descarga Manual desde GitHub

Si prefieres no usar Chocolatey:

1. **Visita el repositorio de winutils:**
   - https://github.com/cdarlint/winutils

2. **Navega a la carpeta:**
   - `hadoop-3.3.5/bin/` (recomendado - más reciente)
   - Haz clic en `winutils.exe`
   - Haz clic en el botón **"Download"** o **"Raw"** para descargar

3. **Coloca el archivo:**
   ```powershell
   # Crear directorio si no existe
   $hadoopHome = "$env:TEMP\hadoop_home"
   New-Item -ItemType Directory -Path "$hadoopHome\bin" -Force
   
   # Mover el archivo descargado a la ubicación correcta
   # (ajusta la ruta según donde descargaste el archivo)
   Move-Item -Path "$env:USERPROFILE\Downloads\winutils.exe" -Destination "$hadoopHome\bin\winutils.exe" -Force
   ```

### Opción 3: Descargar desde Maven Central

Algunas versiones están disponibles en Maven Central. Busca en:
- https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/

## 🔍 Verificación

Después de colocar `winutils.exe`, verifica que existe:

```powershell
Test-Path "$env:TEMP\hadoop_home\bin\winutils.exe"
```

Debería retornar `True`.

## 🚀 Configurar HADOOP_HOME (Opcional pero Recomendado)

Para hacer la configuración permanente:

```powershell
$hadoopHome = "$env:TEMP\hadoop_home"
[System.Environment]::SetEnvironmentVariable('HADOOP_HOME', $hadoopHome, 'User')
```

Luego reinicia tu terminal/PowerShell.

## ⚠️ Nota Importante

- El archivo `winutils.exe` es necesario **solo en Windows**
- En Linux/Mac, Spark funciona sin este archivo
- Si usas Docker o WSL, no necesitas `winutils.exe`

## 🔄 Después de Instalar

1. Reinicia Spark
2. El código ahora detectará automáticamente `winutils.exe`
3. Verás en los logs: `winutils.exe encontrado en: ...`

## 📚 Referencias

- [Repositorio winutils](https://github.com/cdarlint/winutils)
- [Repositorio alternativo](https://github.com/steveloughran/winutils)
- [Documentación Spark Windows](https://spark.apache.org/docs/latest/)

