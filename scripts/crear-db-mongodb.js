// Script para crear la base de datos y colecciones en MongoDB Atlas
// Ejecuta este script usando mongosh o MongoDB Compass

// Conectar a MongoDB Atlas (usa tu MONGO_ATLAS_URI)
// mongosh "<TU_MONGO_ATLAS_URI>"

// Cambiar a la base de datos (se crea automáticamente al usarla)
db = db.getSiblingDB('emergent_etl');

print('=== Creando base de datos: emergent_etl ===');

// ============================================
// COLECCIONES DE LECTURAS LIMPIAS
// ============================================

// Lecturas limpias de sonido
print('\nCreando colección: sound_readings_clean');
db.createCollection('sound_readings_clean');
db.sound_readings_clean.createIndex({ sensor_id: 1, ts_utc: 1 });
db.sound_readings_clean.createIndex({ ts_utc: 1 });
db.sound_readings_clean.createIndex({ sensor_id: 1 });
print('✓ sound_readings_clean creada con índices');

// Lecturas limpias de distancia
print('\nCreando colección: distance_readings_clean');
db.createCollection('distance_readings_clean');
db.distance_readings_clean.createIndex({ sensor_id: 1, ts_utc: 1 });
db.distance_readings_clean.createIndex({ ts_utc: 1 });
db.distance_readings_clean.createIndex({ sensor_id: 1 });
print('✓ distance_readings_clean creada con índices');

// Lecturas limpias de aire
print('\nCreando colección: air_readings_clean');
db.createCollection('air_readings_clean');
db.air_readings_clean.createIndex({ sensor_id: 1, ts_utc: 1 });
db.air_readings_clean.createIndex({ ts_utc: 1 });
db.air_readings_clean.createIndex({ sensor_id: 1 });
print('✓ air_readings_clean creada con índices');

// ============================================
// COLECCIONES DE PREDICCIONES
// ============================================

// Predicciones de sonido
print('\nCreando colección: sound_predictions');
db.createCollection('sound_predictions');
db.sound_predictions.createIndex({ sensor_id: 1, ts_ref: 1 });
db.sound_predictions.createIndex({ ts_ref: 1 });
db.sound_predictions.createIndex({ sensor_id: 1, metric: 1 });
print('✓ sound_predictions creada con índices');

// Predicciones de distancia
print('\nCreando colección: distance_predictions');
db.createCollection('distance_predictions');
db.distance_predictions.createIndex({ sensor_id: 1, ts_ref: 1 });
db.distance_predictions.createIndex({ ts_ref: 1 });
db.distance_predictions.createIndex({ sensor_id: 1, metric: 1 });
print('✓ distance_predictions creada con índices');

// Predicciones de aire
print('\nCreando colección: air_predictions');
db.createCollection('air_predictions');
db.air_predictions.createIndex({ sensor_id: 1, ts_ref: 1 });
db.air_predictions.createIndex({ ts_ref: 1 });
db.air_predictions.createIndex({ sensor_id: 1, metric: 1 });
print('✓ air_predictions creada con índices');

// ============================================
// RESUMEN
// ============================================

print('\n=== RESUMEN ===');
print('Base de datos: emergent_etl');
print('Colecciones creadas:');
db.getCollectionNames().forEach(function(collection) {
  var count = db[collection].countDocuments();
  var indexes = db[collection].getIndexes().length;
  print(`  - ${collection}: ${count} documentos, ${indexes} índices`);
});

print('\n✓ Base de datos y colecciones creadas exitosamente');
print('La base de datos aparecerá en MongoDB Atlas después de unos segundos');

