import { normalizeTimestamp } from './enrichers';
import { parseLocation } from './geo-parser';
import { RangeValidator } from './validators';
import { logger } from './logger';

export interface RawEvent {
  source: string;
  model: string;
  ts_raw?: string;
  ts_utc?: string;
  [key: string]: any;
}

export interface EnrichedEvent extends RawEvent {
  ts_utc: string;
  sensor_id: string;
  geo?: { lat: number; lng: number };
  _validated: boolean;
  _validation_errors?: string[];
}

export class DataProcessor {
  /**
   * Procesa y enriquece un evento raw
   */
  processEvent(rawEvent: RawEvent): EnrichedEvent | null {
    try {
      const enriched: EnrichedEvent = {
        ...rawEvent,
        ts_utc: normalizeTimestamp(rawEvent.ts_raw, rawEvent.ts_utc),
        sensor_id: rawEvent.sensor_id || rawEvent.tenant || 'unknown',
        _validated: false,
      };

      // Parsear ubicación geográfica
      const geo = parseLocation(rawEvent.geo);
      if (geo) {
        enriched.geo = geo;
      } else if (rawEvent.geo) {
        // Mantener el string original si no se pudo parsear
        enriched.geo = rawEvent.geo as any;
      }

      // Validar según el tipo de sensor
      const validationErrors: string[] = [];
      const model = enriched.model.toLowerCase();

      if (model.includes('ws302') || model.includes('sound')) {
        const result = RangeValidator.validateSound(
          enriched.LAeq,
          enriched.LAI,
          enriched.LAImax
        );
        if (!result.valid) {
          validationErrors.push(result.reason || 'Validación de sonido falló');
        }
      } else if (model.includes('em310') || model.includes('distance')) {
        const result = RangeValidator.validateDistance(enriched.distance);
        if (!result.valid) {
          validationErrors.push(result.reason || 'Validación de distancia falló');
        }
      } else if (model.includes('em500') || model.includes('co2') || model.includes('air')) {
        const result = RangeValidator.validateAir(
          enriched.co2,
          enriched.temperature,
          enriched.humidity,
          enriched.pressure
        );
        if (!result.valid) {
          validationErrors.push(result.reason || 'Validación de aire falló');
        }
      }

      enriched._validated = validationErrors.length === 0;
      if (validationErrors.length > 0) {
        enriched._validation_errors = validationErrors;
        logger.warn(`Evento con errores de validación: ${enriched.sensor_id}`, {
          errors: validationErrors,
        });
      }

      return enriched;
    } catch (error: any) {
      logger.error('Error al procesar evento', { error: error.message, event: rawEvent });
      return null;
    }
  }
}

