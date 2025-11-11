import dotenv from 'dotenv';

dotenv.config();

export const config = {
  kafka: {
    bootstrapServers: process.env.KAFKA_BOOTSTRAP_SERVERS || 'localhost:29092',
    groupId: process.env.KAFKA_GROUP_ID || 'listener-router-group',
    clientId: process.env.KAFKA_CLIENT_ID || 'emergent-etl-listener-router',
  },
  spark: {
    host: process.env.SPARK_HOST || 'localhost',
    port: parseInt(process.env.SPARK_PORT || '8082', 10),  // Cambiado a 8082 para evitar conflicto con Docker/WSL
    endpoint: process.env.SPARK_ENDPOINT || '/api/data',
    protocol: (process.env.SPARK_PROTOCOL || 'http') as 'http' | 'https',
    timeout: parseInt(process.env.SPARK_TIMEOUT || '30000', 10),
  },
  processing: {
    batchSize: parseInt(process.env.BATCH_SIZE || '10', 10),
    batchTimeout: parseInt(process.env.BATCH_TIMEOUT || '5000', 10),
    maxRetries: parseInt(process.env.MAX_RETRIES || '3', 10),
    retryDelay: parseInt(process.env.RETRY_DELAY || '1000', 10),
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
  },
};

