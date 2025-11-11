import { CSVRow } from '../csv-reader';
import { parseISO, format } from 'date-fns';
import { utcToZonedTime, format as tzFormat } from 'date-fns-tz';

export interface TransformedEvent {
  source: string;
  model: string;
  ts_raw?: string;
  ts_utc: string;
  [key: string]: any;
}

export abstract class BaseTransformer {
  protected abstract model: string;
  protected abstract topic: string;

  abstract transform(row: CSVRow): TransformedEvent | null;

  protected parseTimestamp(timeValue: string | undefined): { ts_raw?: string; ts_utc: string } {
    if (!timeValue) {
      const now = new Date();
      return {
        ts_utc: now.toISOString(),
      };
    }

    try {
      // Intentar parsear diferentes formatos de fecha
      let date: Date;
      
      // Formato ISO o similar
      if (timeValue.includes('T') || timeValue.includes('-')) {
        date = parseISO(timeValue);
      } else {
        // Formato personalizado (ej: "2024-11-03 10:15:20-04:00")
        date = new Date(timeValue);
      }

      if (isNaN(date.getTime())) {
        throw new Error('Fecha inválida');
      }

      return {
        ts_raw: timeValue,
        ts_utc: date.toISOString(),
      };
    } catch (error) {
      // Si falla, usar fecha actual
      const now = new Date();
      return {
        ts_raw: timeValue,
        ts_utc: now.toISOString(),
      };
    }
  }

  protected getValue(row: CSVRow, key: string): string | undefined {
    return row[key];
  }

  protected getNumericValue(row: CSVRow, key: string): number | null {
    const value = this.getValue(row, key);
    if (!value) return null;
    
    const num = parseFloat(value);
    return isNaN(num) ? null : num;
  }

  getTopic(): string {
    return this.topic;
  }

  getModel(): string {
    return this.model;
  }
}

