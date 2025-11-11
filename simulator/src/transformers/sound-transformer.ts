import { BaseTransformer, TransformedEvent } from './base-transformer';
import { CSVRow } from '../csv-reader';

export class SoundTransformer extends BaseTransformer {
  protected model = 'WS302-915M';
  protected topic = 'ws302.sound.raw.v1';

  transform(row: CSVRow): TransformedEvent | null {
    try {
      const timeValue = this.getValue(row, 'time');
      const { ts_raw, ts_utc } = this.parseTimestamp(timeValue);

      const event: TransformedEvent = {
        source: 'csv-replay',
        model: this.model,
        ts_utc,
        tenant: this.getValue(row, 'deviceInfo.tenantName') || undefined,
        sensor_id: this.getValue(row, 'deviceInfo.deviceName') || 'unknown',
        addr: this.getValue(row, 'deviceInfo.tags.Address') || undefined,
        geo: this.getValue(row, 'deviceInfo.tags.Location') || undefined,
        LAeq: this.getNumericValue(row, 'object.LAeq'),
        LAI: this.getNumericValue(row, 'object.LAI'),
        LAImax: this.getNumericValue(row, 'object.LAImax'),
        status: this.getValue(row, 'object.status') || undefined,
      };

      if (ts_raw) {
        event.ts_raw = ts_raw;
      }

      return event;
    } catch (error) {
      console.error('Error transformando fila de sonido:', error);
      return null;
    }
  }
}

