import { SoundTransformer } from './sound-transformer';
import { DistanceTransformer } from './distance-transformer';
import { AirTransformer } from './air-transformer';
import { BaseTransformer } from './base-transformer';
import path from 'path';

export { SoundTransformer } from './sound-transformer';
export { DistanceTransformer } from './distance-transformer';
export { AirTransformer } from './air-transformer';
export { BaseTransformer } from './base-transformer';

export function getTransformerForFile(fileName: string): BaseTransformer | null {
  const lowerFileName = fileName.toLowerCase();

  if (lowerFileName.includes('ws302') || lowerFileName.includes('sonido')) {
    return new SoundTransformer();
  }

  if (lowerFileName.includes('em310') || lowerFileName.includes('soterrados') || lowerFileName.includes('distance')) {
    return new DistanceTransformer();
  }

  if (lowerFileName.includes('em500') || lowerFileName.includes('co2') || lowerFileName.includes('aire')) {
    return new AirTransformer();
  }

  return null;
}

