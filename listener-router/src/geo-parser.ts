import { logger } from './logger';

export interface GeoCoordinates {
  lat: number;
  lng: number;
}

/**
 * Parsea una cadena de ubicación a coordenadas geográficas.
 * Soporta varios formatos:
 * - "lat,lng" (ej: "-12.0464,-77.0428")
 * - "lat, lng" (con espacio)
 * - Objeto JSON stringificado
 */
export function parseLocation(location: string | undefined): GeoCoordinates | undefined {
  if (!location || typeof location !== 'string') {
    return undefined;
  }

  try {
    // Intentar parsear como JSON primero
    try {
      const parsed = JSON.parse(location);
      if (parsed.lat && parsed.lng) {
        return {
          lat: parseFloat(parsed.lat),
          lng: parseFloat(parsed.lng),
        };
      }
    } catch {
      // No es JSON, continuar con otros formatos
    }

    // Formato "lat,lng" o "lat, lng"
    const parts = location.split(',').map(p => p.trim());
    if (parts.length === 2) {
      const lat = parseFloat(parts[0]);
      const lng = parseFloat(parts[1]);

      if (!isNaN(lat) && !isNaN(lng)) {
        // Validar rangos válidos de latitud y longitud
        if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
          return { lat, lng };
        }
      }
    }

    logger.warn(`No se pudo parsear la ubicación: ${location}`);
    return undefined;
  } catch (error) {
    logger.error(`Error al parsear ubicación: ${location}`, { error });
    return undefined;
  }
}

