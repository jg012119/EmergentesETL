@echo off
REM ============================================
REM Setup Automatico - Sistema IoT Big Data ML
REM ============================================

echo.
echo ============================================
echo   Sistema IoT Big Data ML - Setup
echo ============================================
echo.

REM Verificar si Docker esta instalado
echo [1/8] Verificando Docker Desktop...
docker --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Docker Desktop no esta instalado!
    echo.
    echo Por favor instala Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Luego ejecuta este script nuevamente.
    pause
    exit /b 1
)
echo [OK] Docker Desktop encontrado

REM Verificar si Docker Compose esta disponible
echo [2/8] Verificando Docker Compose...
docker-compose --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose no esta disponible!
    pause
    exit /b 1
)
echo [OK] Docker Compose encontrado

REM Detener contenedores existentes
echo [3/8] Deteniendo contenedores existentes...
docker-compose down >nul 2>&1
echo [OK] Contenedores detenidos

REM Limpiar volumenes antiguos (opcional - comentado por seguridad)
REM echo [4/8] Limpiando volumenes antiguos...
REM docker-compose down -v >nul 2>&1
REM echo [OK] Volumenes limpiados

REM Construir imagenes
echo [4/8] Construyendo imagenes Docker (esto puede tardar varios minutos la primera vez)...
docker-compose build
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al construir las imagenes
    pause
    exit /b 1
)
echo [OK] Imagenes construidas exitosamente

REM Iniciar servicios base
echo [5/8] Iniciando servicios base (Kafka, MySQL, MongoDB, Spark)...
docker-compose up -d zookeeper kafka mysql mongodb spark-master spark-worker
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al iniciar servicios base
    pause
    exit /b 1
)
echo [OK] Servicios base iniciados

REM Esperar inicializacion
echo [6/8] Esperando inicializacion de servicios (30 segundos)...
timeout /t 30 /nobreak >nul
echo [OK] Servicios inicializados

REM Iniciar consumers y dashboard
echo [7/8] Iniciando consumers Spark y dashboard...
docker-compose up -d spark-consumer-em310 spark-consumer-em500 spark-consumer-ws302 dashboard
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al iniciar consumers/dashboard
    pause
    exit /b 1
)
echo [OK] Consumers y dashboard iniciados

REM Verificar estado
echo [8/8] Verificando estado de servicios...
timeout /t 5 /nobreak >nul
docker-compose ps

echo.
echo ============================================
echo   INSTALACION COMPLETADA
echo ============================================
echo.
echo Dashboard: http://localhost:8501
echo Spark Master UI: http://localhost:18080
echo Spark Worker UI: http://localhost:8081
echo.
echo IMPORTANTE: Para generar predicciones ML ejecuta:
echo   docker exec spark-ml-job /opt/spark/bin/spark-submit --master local[2] /opt/spark/app/etl/spark_ml_forecast.py
echo.
echo PRODUCTORES: No olvides iniciar los productores Python:
echo   cd app/producers
echo   python producer_em310.py
echo   python producer_em500.py
echo   python producer_ws302.py
echo.
echo Para ver logs de un servicio:
echo   docker logs -f [nombre_servicio]
echo.
echo Para detener todos los servicios:
echo   docker-compose down
echo.
echo ============================================

pause
