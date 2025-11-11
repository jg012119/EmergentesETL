#!/bin/bash

# Script para inicializar los tópicos de Kafka
# Uso: ./scripts/init-kafka-topics.sh

KAFKA_BOOTSTRAP_SERVER=${KAFKA_BOOTSTRAP_SERVER:-localhost:29092}

echo "Inicializando tópicos de Kafka en ${KAFKA_BOOTSTRAP_SERVER}..."

# Función para crear un tópico
create_topic() {
    local topic_name=$1
    local partitions=${2:-3}
    local retention=${3:-604800000}  # 7 días en milisegundos
    
    echo "Creando tópico: ${topic_name}"
    
    docker exec kafka kafka-topics \
        --create \
        --bootstrap-server localhost:9092 \
        --topic "${topic_name}" \
        --partitions "${partitions}" \
        --replication-factor 1 \
        --config retention.ms="${retention}" \
        --if-not-exists || echo "Tópico ${topic_name} ya existe o error al crearlo"
}

# Tópicos raw (datos sin procesar desde el simulador)
create_topic "em310.distance.raw.v1" 3 604800000  # 7 días
create_topic "em500.air.raw.v1" 3 604800000
create_topic "ws302.sound.raw.v1" 3 604800000

echo ""
echo "✓ Tópicos creados exitosamente"
echo ""
echo "Tópicos disponibles:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

