FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY config/ ./config/

# Exponer puerto para el servidor HTTP
EXPOSE 8080

# Comando por defecto (se puede sobrescribir)
CMD ["python", "src/main/python/etl_main.py"]

