import axios, { AxiosInstance } from 'axios';
import { config } from './config';
import { logger } from './logger';
import { EnrichedEvent } from './data-processor';

export class SparkClient {
  private client: AxiosInstance;
  private batch: EnrichedEvent[] = [];
  private batchTimeout?: NodeJS.Timeout;

  constructor() {
    const baseURL = `${config.spark.protocol}://${config.spark.host}:${config.spark.port}`;
    
    this.client = axios.create({
      baseURL,
      timeout: config.spark.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Envía un evento individual a Spark
   */
  async sendEvent(event: EnrichedEvent): Promise<boolean> {
    try {
      const response = await this.client.post(config.spark.endpoint, event);
      logger.debug(`Evento enviado a Spark`, {
        sensor_id: event.sensor_id,
        status: response.status,
      });
      return true;
    } catch (error: any) {
      logger.error(`Error al enviar evento a Spark`, {
        error: error.message,
        sensor_id: event.sensor_id,
        status: error.response?.status,
      });
      return false;
    }
  }

  /**
   * Agrega un evento al batch y lo envía cuando se alcanza el tamaño o timeout
   */
  async sendBatch(event: EnrichedEvent): Promise<void> {
    this.batch.push(event);

    // Si el batch está lleno, enviarlo inmediatamente
    if (this.batch.length >= config.processing.batchSize) {
      await this.flushBatch();
      return;
    }

    // Configurar timeout para enviar el batch
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }

    this.batchTimeout = setTimeout(async () => {
      await this.flushBatch();
    }, config.processing.batchTimeout);
  }

  /**
   * Envía el batch actual a Spark
   */
  private async flushBatch(): Promise<void> {
    if (this.batch.length === 0) {
      return;
    }

    const batchToSend = [...this.batch];
    this.batch = [];

    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = undefined;
    }

    let retries = 0;
    while (retries < config.processing.maxRetries) {
      try {
        const response = await this.client.post(`${config.spark.endpoint}/batch`, {
          events: batchToSend,
          count: batchToSend.length,
        });

        logger.info(`Batch enviado a Spark`, {
          count: batchToSend.length,
          status: response.status,
        });
        return;
      } catch (error: any) {
        retries++;
        logger.warn(`Error al enviar batch a Spark (intento ${retries}/${config.processing.maxRetries})`, {
          error: error.message,
          count: batchToSend.length,
        });

        if (retries < config.processing.maxRetries) {
          await new Promise(resolve => setTimeout(resolve, config.processing.retryDelay * retries));
        } else {
          logger.error(`No se pudo enviar batch después de ${config.processing.maxRetries} intentos`);
          // Aquí podrías implementar un dead letter queue
        }
      }
    }
  }

  /**
   * Fuerza el envío del batch pendiente
   */
  async flush(): Promise<void> {
    await this.flushBatch();
  }
}

