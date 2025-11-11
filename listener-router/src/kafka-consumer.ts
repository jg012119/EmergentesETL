import { Kafka, Consumer, EachMessagePayload } from 'kafkajs';
import { config } from './config';
import { logger } from './logger';
import { DataProcessor, RawEvent } from './data-processor';
import { SparkClient } from './spark-client';

export class KafkaConsumer {
  private kafka: Kafka;
  private consumer: Consumer;
  private dataProcessor: DataProcessor;
  private sparkClient: SparkClient;
  private isRunning: boolean = false;

  // Tópicos a consumir
  private readonly topics = [
    'em310.distance.raw.v1',
    'em500.air.raw.v1',
    'ws302.sound.raw.v1',
  ];

  constructor() {
    this.kafka = new Kafka({
      clientId: config.kafka.clientId,
      brokers: config.kafka.bootstrapServers.split(','),
      retry: {
        initialRetryTime: 100,
        retries: 8,
        maxRetryTime: 30000,
        multiplier: 2,
      },
    });

    this.consumer = this.kafka.consumer({
      groupId: config.kafka.groupId,
      sessionTimeout: 30000,
      heartbeatInterval: 3000,
    });

    this.dataProcessor = new DataProcessor();
    this.sparkClient = new SparkClient();
  }

  async connect(): Promise<void> {
    try {
      await this.consumer.connect();
      logger.info('Conectado a Kafka como consumidor');

      // Suscribirse a los tópicos
      await this.consumer.subscribe({
        topics: this.topics,
        fromBeginning: false, // Consumir solo mensajes nuevos
      });

      logger.info(`Suscrito a tópicos: ${this.topics.join(', ')}`);
    } catch (error) {
      logger.error('Error al conectar a Kafka', { error });
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    try {
      // Enviar batch pendiente antes de desconectar
      await this.sparkClient.flush();
      
      await this.consumer.disconnect();
      this.isRunning = false;
      logger.info('Desconectado de Kafka');
    } catch (error) {
      logger.error('Error al desconectar de Kafka', { error });
      throw error;
    }
  }

  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('El consumidor ya está corriendo');
      return;
    }

    await this.connect();

    this.isRunning = true;
    logger.info('Iniciando consumo de mensajes de Kafka...');

    await this.consumer.run({
      eachMessage: async (payload: EachMessagePayload) => {
        await this.processMessage(payload);
      },
    });
  }

  private async processMessage(payload: EachMessagePayload): Promise<void> {
    const { topic, partition, message } = payload;

    try {
      // Parsear mensaje JSON
      const rawEvent: RawEvent = JSON.parse(message.value?.toString() || '{}');

      logger.debug(`Mensaje recibido de ${topic}`, {
        partition,
        offset: message.offset,
        sensor_id: rawEvent.sensor_id || rawEvent.tenant,
      });

      // Procesar y enriquecer el evento
      const enrichedEvent = this.dataProcessor.processEvent(rawEvent);

      if (!enrichedEvent) {
        logger.warn('No se pudo procesar el evento', { topic, partition, offset: message.offset });
        return;
      }

      // Enviar a Spark (con batching)
      await this.sparkClient.sendBatch(enrichedEvent);

      logger.info(`Evento procesado y enviado a Spark`, {
        topic,
        sensor_id: enrichedEvent.sensor_id,
        validated: enrichedEvent._validated,
      });
    } catch (error: any) {
      logger.error(`Error al procesar mensaje de ${topic}`, {
        error: error.message,
        partition,
        offset: message.offset,
      });
    }
  }

  isConsumerRunning(): boolean {
    return this.isRunning;
  }
}

