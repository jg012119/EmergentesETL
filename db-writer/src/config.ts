import dotenv from 'dotenv';

dotenv.config();

export const config = {
  server: {
    host: process.env.HOST || '0.0.0.0',
    port: parseInt(process.env.PORT || '3001', 10),
  },
  mysql: {
    uri: process.env.MYSQL_URI || undefined,
    host: process.env.MYSQL_HOST || 'localhost',
    port: parseInt(process.env.MYSQL_PORT || '3306', 10),
    database: process.env.MYSQL_DATABASE || 'emergent_etl',
    user: process.env.MYSQL_USER || 'etl_user',
    password: process.env.MYSQL_PASSWORD || 'etl_password',
  },
  mongodb: {
    uri: process.env.MONGO_ATLAS_URI || undefined,
    host: process.env.MONGO_HOST || 'localhost',
    port: parseInt(process.env.MONGO_PORT || '27017', 10),
    database: process.env.MONGO_DATABASE || 'emergent_etl',
    user: process.env.MONGO_USER || 'admin',
    password: process.env.MONGO_PASSWORD || 'adminpassword',
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
  },
};

