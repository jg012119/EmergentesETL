// Script de inicialización de MongoDB para EmergentesETL
// Este script se ejecuta automáticamente al iniciar el contenedor MongoDB

db = db.getSiblingDB('emergent_etl');

// Crear colecciones con índices

// ============================================
// COLECCIONES DE LECTURAS LIMPIAS
// ============================================

// Lecturas limpias de sonido
db.createCollection('sound_readings_clean');
db.sound_readings_clean.createIndex({ sensor_id: 1, ts: 1 });
db.sound_readings_clean.createIndex({ ts: 1 });
db.sound_readings_clean.createIndex({ sensor_id: 1 });

// Lecturas limpias de distancia
db.createCollection('distance_readings_clean');
db.distance_readings_clean.createIndex({ sensor_id: 1, ts: 1 });
db.distance_readings_clean.createIndex({ ts: 1 });
db.distance_readings_clean.createIndex({ sensor_id: 1 });

// Lecturas limpias de aire
db.createCollection('air_readings_clean');
db.air_readings_clean.createIndex({ sensor_id: 1, ts: 1 });
db.air_readings_clean.createIndex({ ts: 1 });
db.air_readings_clean.createIndex({ sensor_id: 1 });

// ============================================
// COLECCIONES DE PREDICCIONES
// ============================================

// Predicciones de sonido
db.createCollection('sound_predictions');
db.sound_predictions.createIndex({ sensor_id: 1, ts_ref: 1 });
db.sound_predictions.createIndex({ ts_ref: 1 });
db.sound_predictions.createIndex({ sensor_id: 1, metric: 1 });

// Predicciones de distancia
db.createCollection('distance_predictions');
db.distance_predictions.createIndex({ sensor_id: 1, ts_ref: 1 });
db.distance_predictions.createIndex({ ts_ref: 1 });
db.distance_predictions.createIndex({ sensor_id: 1, metric: 1 });

// Predicciones de aire
db.createCollection('air_predictions');
db.air_predictions.createIndex({ sensor_id: 1, ts_ref: 1 });
db.air_predictions.createIndex({ ts_ref: 1 });
db.air_predictions.createIndex({ sensor_id: 1, metric: 1 });

print('✓ Colecciones e índices de MongoDB creados exitosamente');

