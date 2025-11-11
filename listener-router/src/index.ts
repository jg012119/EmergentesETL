import { KafkaConsumer } from './kafka-consumer';
import { logger } from './logger';
import { config } from './config';

async function main() {
  logger.info('=== Iniciando Listener/Router ===');
  logger.info(`Kafka: ${config.kafka.bootstrapServers}`);
  logger.info(`Spark: ${config.spark.protocol}://${config.spark.host}:${config.spark.port}`);
  logger.info(`Batch size: ${config.processing.batchSize}`);
  logger.info(`Batch timeout: ${config.processing.batchTimeout}ms`);

  const consumer = new KafkaConsumer();

  // Manejo de señales para cierre limpio
  const shutdown = async () => {
    logger.info('Cerrando Listener/Router...');
    try {
      await consumer.disconnect();
      process.exit(0);
    } catch (error) {
      logger.error('Error durante el cierre', { error });
      process.exit(1);
    }
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  // Manejo de errores no capturados
  process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled Rejection', { reason, promise });
  });

  process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception', { error });
    shutdown();
  });

  try {
    await consumer.start();
    logger.info('Listener/Router corriendo. Presiona Ctrl+C para detener.');
  } catch (error) {
    logger.error('Error fatal al iniciar', { error });
    process.exit(1);
  }
}

main();

