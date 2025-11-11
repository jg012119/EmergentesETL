import { BaseTransformer, TransformedEvent } from './base-transformer';
import { CSVRow } from '../csv-reader';

export class DistanceTransformer extends BaseTransformer {
  protected model = 'EM310-UDL-915M';
  protected topic = 'em310.distance.raw.v1';

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
        distance: this.getNumericValue(row, 'object.distance'),
        status: this.getValue(row, 'object.status') || undefined,
      };

      if (ts_raw) {
        event.ts_raw = ts_raw;
      }

      return event;
    } catch (error) {
      console.error('Error transformando fila de distancia:', error);
      return null;
    }
  }
}

