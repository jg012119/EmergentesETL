import { MongoClient, Db, Collection } from 'mongodb';
import { config } from './config';
import { logger } from './logger';

export class MongoDBClient {
  private client: MongoClient | null = null;
  private db: Db | null = null;

  constructor() {
    // initialize() se llama explícitamente desde index.ts
  }

  async initialize(): Promise<void> {
    try {
      const uri = config.mongodb.uri || 
        `mongodb://${config.mongodb.user}:${config.mongodb.password}@${config.mongodb.host}:${config.mongodb.port}/${config.mongodb.database}?authSource=admin`;

      this.client = new MongoClient(uri);
      await this.client.connect();
      this.db = this.client.db(config.mongodb.database);
      
      logger.info(`Conexión MongoDB establecida: ${config.mongodb.database}`);
    } catch (error: any) {
      logger.error(`Error al inicializar MongoDB: ${error.message}`);
      this.client = null;
      this.db = null;
    }
  }

  /**
   * Escribe lecturas limpias a MongoDB
   */
  async writeReadings(collectionName: string, readings: any[]): Promise<boolean> {
    if (!this.db) {
      logger.warn('MongoDB no está disponible, saltando escritura');
      return false;
    }

    if (!readings || readings.length === 0) {
      logger.debug(`No hay lecturas para escribir en ${collectionName}`);
      return true;
    }

    try {
      const collection: Collection = this.db.collection(collectionName);
      
      // Preparar documentos para inserción
      const documents = readings.map(reading => {
        // Limpiar y normalizar el documento
        const doc: any = {
          sensor_id: reading.sensor_id,
          ts_utc: reading.ts_utc,
          model: reading.model,
        };

        // Agregar campos específicos según el tipo de sensor
        if (reading.laeq !== undefined) {
          doc.laeq = reading.laeq;
        }
        if (reading.distance !== undefined) {
          doc.distance = reading.distance;
        }
        if (reading.co2 !== undefined) {
          doc.co2 = reading.co2;
        }
        if (reading.temperature !== undefined) {
          doc.temperature = reading.temperature;
        }
        if (reading.humidity !== undefined) {
          doc.humidity = reading.humidity;
        }

        // Agregar ubicación si existe
        if (reading.location) {
          doc.location = reading.location;
        }
        if (reading.lat !== undefined) {
          doc.lat = reading.lat;
        }
        if (reading.lng !== undefined) {
          doc.lng = reading.lng;
        }

        return doc;
      });

      await collection.insertMany(documents, { ordered: false });
      logger.info(`Lecturas escritas a MongoDB: ${collectionName} (${readings.length} documentos)`);
      return true;
    } catch (error: any) {
      // Si hay errores de duplicados, ignorarlos (ordered: false)
      if (error.code === 11000 || error.writeErrors) {
        const inserted = readings.length - (error.writeErrors?.length || 0);
        logger.warn(`Algunas lecturas no se insertaron en ${collectionName} (duplicados): ${inserted}/${readings.length} insertadas`);
        return inserted > 0;
      }
      logger.error(`Error al escribir lecturas a MongoDB ${collectionName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Cierra la conexión
   */
  async close(): Promise<void> {
    if (this.client) {
      await this.client.close();
      logger.info('Conexión MongoDB cerrada');
    }
  }
}

