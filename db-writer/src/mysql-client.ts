import mysql from 'mysql2/promise';
import { config } from './config';
import { logger } from './logger';

export class MySQLClient {
  private pool: mysql.Pool | null = null;

  constructor() {
    // initialize() se llama explícitamente desde index.ts
  }

  async initialize(): Promise<void> {
    try {
      if (config.mysql.uri) {
        // Usar URI completa si está disponible
        this.pool = mysql.createPool({
          uri: config.mysql.uri,
          waitForConnections: true,
          connectionLimit: 10,
          queueLimit: 0,
        });
        logger.info('Conexión MySQL configurada usando URI');
      } else {
        // Usar parámetros individuales
        this.pool = mysql.createPool({
          host: config.mysql.host,
          port: config.mysql.port,
          database: config.mysql.database,
          user: config.mysql.user,
          password: config.mysql.password,
          waitForConnections: true,
          connectionLimit: 10,
          queueLimit: 0,
        });
        logger.info(`Conexión MySQL configurada: ${config.mysql.host}:${config.mysql.port}/${config.mysql.database}`);
      }

      // Probar conexión
      const connection = await this.pool.getConnection();
      await connection.ping();
      connection.release();
      logger.info('Conexión MySQL establecida correctamente');
    } catch (error: any) {
      logger.error(`Error al inicializar MySQL: ${error.message}`);
      this.pool = null;
    }
  }

  /**
   * Escribe métricas agregadas a MySQL
   */
  async writeMetrics(tableName: string, metrics: any[]): Promise<boolean> {
    if (!this.pool) {
      logger.warn('MySQL no está disponible, saltando escritura');
      return false;
    }

    if (!metrics || metrics.length === 0) {
      logger.debug(`No hay métricas para escribir en ${tableName}`);
      return true;
    }

    try {
      const connection = await this.pool.getConnection();
      
      try {
        // Preparar datos para inserción
        const values = metrics.map(metric => {
          // Extraer window_info si existe
          const windowStart = metric.window_info?.start || metric.window_start;
          const windowEnd = metric.window_info?.end || metric.window_end;
          
          return [
            metric.sensor_id,
            windowStart,
            windowEnd,
            metric.laeq_avg || null,
            metric.p95_laeq || null,
            metric.alert_prob || null,
            metric.distance_avg || null,
            metric.distance_min || null,
            metric.distance_max || null,
            metric.anomaly_prob || null,
            metric.co2_avg || null,
            metric.temperature_avg || null,
            metric.humidity_avg || null,
            metric.alert_prob || null,
          ];
        });

        // Construir query según el tipo de tabla
        let query = '';
        let columns: string[] = [];

        if (tableName.includes('sound')) {
          query = `INSERT INTO ${tableName} (sensor_id, window_start, window_end, laeq_avg, p95_laeq, alert_prob) VALUES ?`;
          columns = ['sensor_id', 'window_start', 'window_end', 'laeq_avg', 'p95_laeq', 'alert_prob'];
        } else if (tableName.includes('distance')) {
          query = `INSERT INTO ${tableName} (sensor_id, window_start, window_end, distance_avg, distance_min, distance_max, anomaly_prob) VALUES ?`;
          columns = ['sensor_id', 'window_start', 'window_end', 'distance_avg', 'distance_min', 'distance_max', 'anomaly_prob'];
        } else if (tableName.includes('air')) {
          query = `INSERT INTO ${tableName} (sensor_id, window_start, window_end, co2_avg, temperature_avg, humidity_avg, alert_prob) VALUES ?`;
          columns = ['sensor_id', 'window_start', 'window_end', 'co2_avg', 'temperature_avg', 'humidity_avg', 'alert_prob'];
        } else {
          logger.warn(`Tabla desconocida: ${tableName}`);
          return false;
        }

        // Filtrar valores según las columnas necesarias
        const filteredValues = values.map(v => {
          if (tableName.includes('sound')) {
            return [v[0], v[1], v[2], v[3], v[4], v[5]]; // sensor_id, window_start, window_end, laeq_avg, p95_laeq, alert_prob
          } else if (tableName.includes('distance')) {
            return [v[0], v[1], v[2], v[6], v[7], v[8], v[9]]; // sensor_id, window_start, window_end, distance_avg, distance_min, distance_max, anomaly_prob
          } else if (tableName.includes('air')) {
            return [v[0], v[1], v[2], v[10], v[11], v[12], v[13]]; // sensor_id, window_start, window_end, co2_avg, temperature_avg, humidity_avg, alert_prob
          }
          return v;
        });

        await connection.query(query, [filteredValues]);
        logger.info(`Métricas escritas a MySQL: ${tableName} (${metrics.length} registros)`);
        return true;
      } finally {
        connection.release();
      }
    } catch (error: any) {
      logger.error(`Error al escribir métricas a MySQL ${tableName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Cierra las conexiones
   */
  async close(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      logger.info('Conexiones MySQL cerradas');
    }
  }
}

