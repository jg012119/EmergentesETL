# Solución para Problemas de Spark en Windows

Este documento explica cómo se resolvieron los problemas comunes de Spark en Windows.

## 🔧 Problema: HADOOP_HOME no configurado

### Error Original

```
java.lang.RuntimeException: java.io.FileNotFoundException: 
HADOOP_HOME and hadoop.home.dir are unset. 
-see https://wiki.apache.org/hadoop/WindowsProblems
```

### Causa

Spark en Windows intenta usar utilidades de Hadoop (como `winutils.exe`) que no están instaladas por defecto. Spark busca la variable de entorno `HADOOP_HOME` para encontrar estas utilidades.

### ✅ Solución Implementada

El código ahora detecta automáticamente si está corriendo en Windows y:

1. **Crea un HADOOP_HOME temporal** si no está configurado:
   ```python
   if platform.system() == "Windows" and not os.environ.get("HADOOP_HOME"):
       hadoop_home = os.path.join(tempfile.gettempdir(), "hadoop_home")
       os.makedirs(hadoop_home, exist_ok=True)
       os.makedirs(os.path.join(hadoop_home, "bin"), exist_ok=True)
       os.environ["HADOOP_HOME"] = hadoop_home
   ```

2. **Configura el checkpoint en un directorio temporal de Windows**:
   ```python
   if platform.system() == "Windows":
       checkpoint_dir = os.path.join(tempfile.gettempdir(), "spark-checkpoint")
   else:
       checkpoint_dir = "/tmp/spark-checkpoint"
   ```

3. **Configura el filesystem local** para evitar dependencias de winutils:
   ```python
   .config("spark.hadoop.fs.defaultFS", "file:///")
   ```

## 📋 Verificación

Después de aplicar esta solución, deberías ver en los logs:

```
INFO:__main__:HADOOP_HOME configurado para Windows: C:\Users\<usuario>\AppData\Local\Temp\hadoop_home
INFO:__main__:Spark session creada con paquetes: mysql:mysql-connector-java:8.0.33,org.mongodb.spark:mongo-spark-connector_2.12:10.2.0
INFO:__main__:Checkpoint location: C:\Users\<usuario>\AppData\Local\Temp\spark-checkpoint
```

Y **NO** deberías ver el error `HADOOP_HOME and hadoop.home.dir are unset`.

## ⚠️ Notas Importantes

1. **No necesitas instalar winutils.exe**: La solución evita la necesidad de winutils.exe configurando Spark para usar el filesystem local.

2. **Directorio temporal**: El HADOOP_HOME se crea en el directorio temporal de Windows (`%TEMP%`). Esto es seguro y se puede limpiar automáticamente.

3. **Checkpoint location**: Los checkpoints de Spark se guardan en un directorio temporal de Windows en lugar de `/tmp` (que no existe en Windows).

4. **Solo para Windows**: Esta configuración solo se aplica cuando se detecta que el sistema operativo es Windows. En Linux/Mac, se usa la configuración estándar.

## 🔍 Solución de Problemas

### Si el error persiste

1. **Verifica que estás usando la versión actualizada del código**:
   ```bash
   cd spark-etl
   python src/main/python/etl_main.py
   ```

2. **Limpia el directorio temporal de Spark** (opcional):
   ```powershell
   Remove-Item -Recurse -Force "$env:TEMP\spark-checkpoint" -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force "$env:TEMP\hadoop_home" -ErrorAction SilentlyContinue
   ```

3. **Verifica que Python puede crear directorios**:
   ```python
   import tempfile
   import os
   test_dir = os.path.join(tempfile.gettempdir(), "test")
   os.makedirs(test_dir, exist_ok=True)
   print(f"Directorio creado: {test_dir}")
   ```

### Si necesitas winutils.exe (no recomendado)

Si por alguna razón necesitas winutils.exe:

1. Descarga winutils.exe desde: https://github.com/steveloughran/winutils
2. Crea un directorio (ej: `C:\hadoop\bin`)
3. Coloca `winutils.exe` en ese directorio
4. Configura la variable de entorno:
   ```powershell
   $env:HADOOP_HOME = "C:\hadoop"
   ```

**Nota**: La solución implementada evita la necesidad de este paso.

## 📚 Referencias

- [Apache Spark Windows Problems](https://wiki.apache.org/hadoop/WindowsProblems)
- [WinUtils Repository](https://github.com/steveloughran/winutils)
- [Spark Configuration](https://spark.apache.org/docs/latest/configuration.html)

