import { Kafka, Producer, ProducerRecord } from 'kafkajs';
import { logger } from './logger';
import { config } from './config';

export class KafkaProducer {
  private kafka: Kafka;
  private producer: Producer;
  private isConnected: boolean = false;

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

    this.producer = this.kafka.producer({
      maxInFlightRequests: 1,
      idempotent: true,
      transactionTimeout: 30000,
    });
  }

  async connect(): Promise<void> {
    if (this.isConnected) {
      return;
    }

    try {
      await this.producer.connect();
      this.isConnected = true;
      logger.info('Conectado a Kafka');
    } catch (error) {
      logger.error('Error al conectar a Kafka', { error });
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (!this.isConnected) {
      return;
    }

    try {
      await this.producer.disconnect();
      this.isConnected = false;
      logger.info('Desconectado de Kafka');
    } catch (error) {
      logger.error('Error al desconectar de Kafka', { error });
      throw error;
    }
  }

  async send(topic: string, message: any): Promise<void> {
    if (!this.isConnected) {
      throw new Error('Productor no conectado a Kafka');
    }

    const record: ProducerRecord = {
      topic,
      messages: [
        {
          key: message.sensor_id || message.tenant || 'unknown',
          value: JSON.stringify(message),
          timestamp: Date.now().toString(),
        },
      ],
    };

    try {
      const result = await this.producer.send(record);
      logger.debug(`Mensaje enviado a ${topic}`, {
        partition: result[0].partition,
        offset: result[0].offset,
        sensor_id: message.sensor_id,
      });
    } catch (error: any) {
      logger.error(`Error al enviar mensaje a ${topic}`, {
        error: error.message,
        topic,
        sensor_id: message.sensor_id,
      });
      throw error;
    }
  }
}

