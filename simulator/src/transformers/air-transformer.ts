import { BaseTransformer, TransformedEvent } from './base-transformer';
import { CSVRow } from '../csv-reader';

export class AirTransformer extends BaseTransformer {
  protected model = 'EM500-CO2-915M';
  protected topic = 'em500.air.raw.v1';

  transform(row: CSVRow): TransformedEvent | null {
    try {
      const timeValue = this.getValue(row, 'time');
      const { ts_raw, ts_utc } = this.parseTimestamp(timeValue);

      const event: TransformedEvent = {
        source: 'csv-replay',
        model: this.model,
        ts_utc,
        sensor_id: this.getValue(row, 'deviceInfo.deviceName') || 'unknown',
        addr: this.getValue(row, 'deviceInfo.tags.Address') || undefined,
        geo: this.getValue(row, 'deviceInfo.tags.Location') || undefined,
        co2: this.getNumericValue(row, 'object.co2'),
        co2_status: this.getValue(row, 'object.co2_status') || undefined,
        temperature: this.getNumericValue(row, 'object.temperature'),
        temperature_status: this.getValue(row, 'object.temperature_status') || undefined,
        humidity: this.getNumericValue(row, 'object.humidity'),
        humidity_status: this.getValue(row, 'object.humidity_status') || undefined,
        pressure: this.getNumericValue(row, 'object.pressure'),
        pressure_status: this.getValue(row, 'object.pressure_status') || undefined,
      };

      if (ts_raw) {
        event.ts_raw = ts_raw;
      }

      return event;
    } catch (error) {
      console.error('Error transformando fila de aire:', error);
      return null;
    }
  }
}

