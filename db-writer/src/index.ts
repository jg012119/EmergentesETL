import { config } from './config';
import { logger } from './logger';
import { MySQLClient } from './mysql-client';
import { MongoDBClient } from './mongodb-client';
import { KafkaConsumer } from './kafka-consumer';

// Clientes de bases de datos
const mysqlClient = new MySQLClient();
const mongoClient = new MongoDBClient();

// Consumidor Kafka (consume datos procesados por Spark)
const kafkaConsumer = new KafkaConsumer(mysqlClient, mongoClient);

/**
 * Iniciar servicio db-writer
 * Consume de Kafka y escribe a MySQL y MongoDB
 */
async function start() {
  try {
    logger.info('=== Iniciando Servicio DB Writer ===');
    logger.info('Modo: Consumidor Kafka');
    logger.info(`Tópicos: processed.metrics.v1, processed.readings.v1`);
    
    // Inicializar clientes de bases de datos
    await mysqlClient.initialize();
    await mongoClient.initialize();
    
    // Conectar y empezar a consumir de Kafka
    await kafkaConsumer.connect();
    
    logger.info('✓ Servicio DB Writer iniciado correctamente');
    logger.info('Consumiendo mensajes de Kafka y escribiendo a MySQL y MongoDB...');
  } catch (error: any) {
    logger.error(`Error al iniciar servicio: ${error.message}`);
    process.exit(1);
  }
}

/**
 * Manejo de cierre graceful
 */
process.on('SIGTERM', async () => {
  logger.info('SIGTERM recibido, cerrando servicio...');
  await kafkaConsumer.disconnect();
  await mysqlClient.close();
  await mongoClient.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT recibido, cerrando servicio...');
  await kafkaConsumer.disconnect();
  await mysqlClient.close();
  await mongoClient.close();
  process.exit(0);
});

// Iniciar servicio
start();

