import fs from 'fs';
import path from 'path';
import csv from 'csv-parser';
import { EventEmitter } from 'events';
import { logger } from './logger';

export interface CSVRow {
  [key: string]: string | undefined;
}

export class CSVReader extends EventEmitter {
  private filePath: string;
  private rows: CSVRow[] = [];
  private currentIndex: number = 0;

  constructor(filePath: string) {
    super();
    this.filePath = filePath;
  }

  async load(): Promise<void> {
    return new Promise((resolve, reject) => {
      logger.info(`Cargando archivo CSV: ${this.filePath}`);

      if (!fs.existsSync(this.filePath)) {
        reject(new Error(`Archivo no encontrado: ${this.filePath}`));
        return;
      }

      const rows: CSVRow[] = [];

      fs.createReadStream(this.filePath)
        .pipe(csv())
        .on('data', (row: CSVRow) => {
          rows.push(row);
        })
        .on('end', () => {
          this.rows = rows;
          this.currentIndex = 0;
          logger.info(`CSV cargado: ${rows.length} filas`);
          this.emit('loaded', rows.length);
          resolve();
        })
        .on('error', (error) => {
          logger.error(`Error al leer CSV: ${error.message}`, { error });
          reject(error);
        });
    });
  }

  getNextRow(): CSVRow | null {
    if (this.currentIndex >= this.rows.length) {
      return null; // Fin del archivo
    }

    const row = this.rows[this.currentIndex];
    this.currentIndex++;
    return row;
  }

  reset(): void {
    this.currentIndex = 0;
    logger.info('CSV reiniciado al inicio');
  }

  getTotalRows(): number {
    return this.rows.length;
  }

  getCurrentIndex(): number {
    return this.currentIndex;
  }

  isFinished(): boolean {
    return this.currentIndex >= this.rows.length;
  }
}

