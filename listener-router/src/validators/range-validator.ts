import { logger } from '../logger';

export interface ValidationResult {
  valid: boolean;
  reason?: string;
}

/**
 * Valida rangos razonables para valores de sensores
 */
export class RangeValidator {
  // Rangos para sonido (dB)
  static readonly SOUND_LAEQ_MIN = 0;
  static readonly SOUND_LAEQ_MAX = 200;
  static readonly SOUND_LAI_MIN = 0;
  static readonly SOUND_LAI_MAX = 200;
  static readonly SOUND_LAIMAX_MIN = 0;
  static readonly SOUND_LAIMAX_MAX = 200;

  // Rangos para distancia (metros)
  static readonly DISTANCE_MIN = 0;
  static readonly DISTANCE_MAX = 100;

  // Rangos para aire
  static readonly CO2_MIN = 0;
  static readonly CO2_MAX = 10000; // ppm
  static readonly TEMP_MIN = -50;
  static readonly TEMP_MAX = 100; // Celsius
  static readonly HUMIDITY_MIN = 0;
  static readonly HUMIDITY_MAX = 100; // Porcentaje
  static readonly PRESSURE_MIN = 0;
  static readonly PRESSURE_MAX = 2000; // hPa

  static validateSound(laeq?: number | null, lai?: number | null, laimax?: number | null): ValidationResult {
    if (laeq !== undefined && laeq !== null) {
      if (laeq < this.SOUND_LAEQ_MIN || laeq > this.SOUND_LAEQ_MAX) {
        return { valid: false, reason: `LAeq fuera de rango: ${laeq}` };
      }
    }

    if (lai !== undefined && lai !== null) {
      if (lai < this.SOUND_LAI_MIN || lai > this.SOUND_LAI_MAX) {
        return { valid: false, reason: `LAI fuera de rango: ${lai}` };
      }
    }

    if (laimax !== undefined && laimax !== null) {
      if (laimax < this.SOUND_LAIMAX_MIN || laimax > this.SOUND_LAIMAX_MAX) {
        return { valid: false, reason: `LAImax fuera de rango: ${laimax}` };
      }
    }

    return { valid: true };
  }

  static validateDistance(distance?: number | null): ValidationResult {
    if (distance !== undefined && distance !== null) {
      if (distance < this.DISTANCE_MIN || distance > this.DISTANCE_MAX) {
        return { valid: false, reason: `Distancia fuera de rango: ${distance}` };
      }
    }

    return { valid: true };
  }

  static validateAir(
    co2?: number | null,
    temp?: number | null,
    humidity?: number | null,
    pressure?: number | null
  ): ValidationResult {
    if (co2 !== undefined && co2 !== null) {
      if (co2 < this.CO2_MIN || co2 > this.CO2_MAX) {
        return { valid: false, reason: `CO2 fuera de rango: ${co2}` };
      }
    }

    if (temp !== undefined && temp !== null) {
      if (temp < this.TEMP_MIN || temp > this.TEMP_MAX) {
        return { valid: false, reason: `Temperatura fuera de rango: ${temp}` };
      }
    }

    if (humidity !== undefined && humidity !== null) {
      if (humidity < this.HUMIDITY_MIN || humidity > this.HUMIDITY_MAX) {
        return { valid: false, reason: `Humedad fuera de rango: ${humidity}` };
      }
    }

    if (pressure !== undefined && pressure !== null) {
      if (pressure < this.PRESSURE_MIN || pressure > this.PRESSURE_MAX) {
        return { valid: false, reason: `Presión fuera de rango: ${pressure}` };
      }
    }

    return { valid: true };
  }
}

