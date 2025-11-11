import { parseISO, format } from 'date-fns';
import { utcToZonedTime } from 'date-fns-tz';
import { logger } from '../logger';

/**
 * Normaliza un timestamp a formato ISO 8601 UTC
 */
export function normalizeTimestamp(tsRaw: string | undefined, tsUtc: string | undefined): string {
  // Si ya tenemos ts_utc, usarlo directamente
  if (tsUtc) {
    try {
      const date = parseISO(tsUtc);
      if (!isNaN(date.getTime())) {
        return date.toISOString();
      }
    } catch {
      // Continuar con ts_raw
    }
  }

  // Intentar parsear ts_raw
  if (tsRaw) {
    try {
      let date: Date;

      // Formato ISO
      if (tsRaw.includes('T') || tsRaw.match(/^\d{4}-\d{2}-\d{2}/)) {
        date = parseISO(tsRaw);
      } else {
        // Formato personalizado
        date = new Date(tsRaw);
      }

      if (!isNaN(date.getTime())) {
        return date.toISOString();
      }
    } catch (error) {
      logger.warn(`No se pudo parsear timestamp: ${tsRaw}`, { error });
    }
  }

  // Si todo falla, usar fecha actual
  return new Date().toISOString();
}

