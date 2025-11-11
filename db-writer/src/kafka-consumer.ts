import { Kafka, Consumer, EachMessagePayload } from 'kafkajs';
import { config } from './config';
import { logger } from './logger';
import { MySQLClient } from './mysql-client';
import { MongoDBClient } from './mongodb-client';

interface ProcessedMetric {
  _table_name: string;
  [key: string]: any;
}

interface ProcessedReading {
  _collection_name: string;
  [key: string]: any;
}

export class KafkaConsumer {
  private kafka: Kafka;
  private consumer: Consumer;
  private mysqlClient: MySQLClient;
  private mongoClient: MongoDBClient;
  private isRunning: boolean = false;

  // Tópicos a consumir (datos procesados por Spark)
  private readonly topics = [
    'processed.metrics.v1',    // Métricas agregadas para MySQL
    'processed.readings.v1',   // Lecturas limpias para MongoDB
  ];

  constructor(mysqlClient: MySQLClient, mongoClient: MongoDBClient) {
    const kafkaBootstrapServers = process.env.KAFKA_BOOTSTRAP_SERVERS || 'localhost:29092';
    
    this.kafka = new Kafka({
      clientId: 'db-writer',
      brokers: kafkaBootstrapServers.split(','),
      retry: {
        initialRetryTime: 100,
        retries: 8,
        maxRetryTime: 30000,
        multiplier: 2,
      },
    });

    this.consumer = this.kafka.consumer({
      groupId: 'db-writer-group',
      sessionTimeout: 30000,
      heartbeatInterval: 3000,
    });

    this.mysqlClient = mysqlClient;
    this.mongoClient = mongoClient;
  }

  async connect(): Promise<void> {
    try {
      await this.consumer.connect();
      logger.info('Conectado a Kafka como consumidor');

      // Suscribirse a los tópicos
      await this.consumer.subscribe({
        topics: this.topics,
        fromBeginning: false, // Solo leer mensajes nuevos
      });

      logger.info(`Suscrito a tópicos: ${this.topics.join(', ')}`);

      // Iniciar consumo
      await this.consumer.run({
        eachMessage: async (payload: EachMessagePayload) => {
          await this.processMessage(payload);
        },
      });

      this.isRunning = true;
      logger.info('Consumidor Kafka iniciado');
    } catch (error: any) {
      logger.error(`Error al conectar consumidor Kafka: ${error.message}`);
      throw error;
    }
  }

  private async processMessage(payload: EachMessagePayload): Promise<void> {
    const { topic, partition, message } = payload;

    try {
      // Parsear mensaje JSON
      const messageValue = message.value?.toString() || '{}';
      const data = JSON.parse(messageValue);

      logger.debug(`Mensaje recibido de ${topic}`, {
        partition,
        offset: message.offset,
      });

      if (topic === 'processed.metrics.v1') {
        // Procesar métricas para MySQL
        await this.processMetrics(data);
      } else if (topic === 'processed.readings.v1') {
        // Procesar lecturas para MongoDB
        await this.processReadings(data);
      } else {
        logger.warn(`Tópico desconocido: ${topic}`);
      }
    } catch (error: any) {
      logger.error(`Error al procesar mensaje de ${topic}`, {
        error: error.message,
        partition,
        offset: message.offset,
      });
      // No hacer throw - continuar procesando otros mensajes
    }
  }

  private async processMetrics(data: ProcessedMetric): Promise<void> {
    try {
      // Extraer nombre de tabla
      const tableName = data._table_name;
      if (!tableName) {
        logger.warn('Mensaje de métricas sin _table_name, ignorando');
        return;
      }

      // Remover metadata antes de escribir
      const { _table_name, ...metricData } = data;

      // Escribir a MySQL
      await this.mysqlClient.writeMetrics(tableName, [metricData]);

      logger.info(`Métrica escrita a MySQL: ${tableName}`, {
        sensor_id: metricData.sensor_id,
      });
    } catch (error: any) {
      logger.error(`Error al procesar métrica: ${error.message}`);
      throw error;
    }
  }

  private async processReadings(data: ProcessedReading): Promise<void> {
    try {
      // Extraer nombre de colección
      const collectionName = data._collection_name;
      if (!collectionName) {
        logger.warn('Mensaje de lectura sin _collection_name, ignorando');
        return;
      }

      // Remover metadata antes de escribir
      const { _collection_name, ...readingData } = data;

      // Escribir a MongoDB
      await this.mongoClient.writeReadings(collectionName, [readingData]);

      logger.info(`Lectura escrita a MongoDB: ${collectionName}`, {
        sensor_id: readingData.sensor_id,
      });
    } catch (error: any) {
      logger.error(`Error al procesar lectura: ${error.message}`);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.isRunning) {
      await this.consumer.disconnect();
      this.isRunning = false;
      logger.info('Desconectado de Kafka');
    }
  }

  isConsumerRunning(): boolean {
    return this.isRunning;
  }
}

