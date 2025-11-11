import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

export const config = {
  kafka: {
    bootstrapServers: process.env.KAFKA_BOOTSTRAP_SERVERS || 'localhost:29092',
    clientId: process.env.KAFKA_CLIENT_ID || 'emergent-etl-simulator',
  },
  csv: {
    directory: process.env.CSV_DIRECTORY || path.join(__dirname, '../../data/csv'),
  },
  simulation: {
    speedMultiplier: parseInt(process.env.SPEED_MULTIPLIER || '1', 10),
    intervalMs: parseInt(process.env.INTERVAL_MS || '10000', 10),
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
  },
};

