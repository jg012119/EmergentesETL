import { CSVReader } from './csv-reader';
import { KafkaProducer } from './kafka-producer';
import { getTransformerForFile } from './transformers';
import { config } from './config';
import { logger } from './logger';
import fs from 'fs';
import path from 'path';

interface SimulationTask {
  fileName: string;
  reader: CSVReader;
  transformer: any;
  topic: string;
}

async function main() {
  logger.info('=== Iniciando Simulador CSV → Kafka ===');
  logger.info(`Velocidad: ${config.simulation.speedMultiplier}x`);
  logger.info(`Intervalo: ${config.simulation.intervalMs}ms`);

  // Conectar a Kafka
  const producer = new KafkaProducer();
  try {
    await producer.connect();
  } catch (error) {
    logger.error('No se pudo conectar a Kafka. Asegúrate de que Kafka esté corriendo.');
    process.exit(1);
  }

  // Encontrar archivos CSV
  const csvDirectory = config.csv.directory;
  logger.info(`Buscando CSVs en: ${csvDirectory}`);

  if (!fs.existsSync(csvDirectory)) {
    logger.error(`Directorio no encontrado: ${csvDirectory}`);
    process.exit(1);
  }

  const csvFiles = fs.readdirSync(csvDirectory)
    .filter(file => file.endsWith('.csv'))
    .map(file => path.join(csvDirectory, file));

  if (csvFiles.length === 0) {
    logger.error('No se encontraron archivos CSV');
    process.exit(1);
  }

  logger.info(`Archivos CSV encontrados: ${csvFiles.length}`);

  // Crear tareas de simulación para cada archivo
  const tasks: SimulationTask[] = [];

  for (const filePath of csvFiles) {
    const fileName = path.basename(filePath);
    const transformer = getTransformerForFile(fileName);

    if (!transformer) {
      logger.warn(`No se encontró transformador para: ${fileName}`);
      continue;
    }

    const reader = new CSVReader(filePath);
    await reader.load();

    tasks.push({
      fileName,
      reader,
      transformer,
      topic: transformer.getTopic(),
    });

    logger.info(`✓ Configurado: ${fileName} → ${transformer.getTopic()}`);
  }

  if (tasks.length === 0) {
    logger.error('No se pudo configurar ningún archivo CSV');
    await producer.disconnect();
    process.exit(1);
  }

  // Función para procesar una fila de cada tarea
  const processNextRows = async () => {
    for (const task of tasks) {
      if (task.reader.isFinished()) {
        logger.info(`Archivo ${task.fileName} completado. Reiniciando...`);
        task.reader.reset();
      }

      const row = task.reader.getNextRow();
      if (!row) continue;

      const event = task.transformer.transform(row);
      if (!event) {
        logger.warn(`No se pudo transformar fila de ${task.fileName}`);
        continue;
      }

      try {
        await producer.send(task.topic, event);
        logger.info(`[${task.fileName}] Enviado a ${task.topic}`, {
          sensor_id: event.sensor_id,
          index: task.reader.getCurrentIndex(),
        });
      } catch (error: any) {
        logger.error(`Error al enviar evento de ${task.fileName}`, {
          error: error.message,
          topic: task.topic,
        });
      }
    }
  };

  // Procesar primera fila inmediatamente
  await processNextRows();

  // Configurar intervalo
  const intervalMs = config.simulation.intervalMs / config.simulation.speedMultiplier;
  logger.info(`Iniciando simulación con intervalo de ${intervalMs}ms`);

  const interval = setInterval(async () => {
    await processNextRows();
  }, intervalMs);

  // Manejo de señales para cierre limpio
  const shutdown = async () => {
    logger.info('Cerrando simulador...');
    clearInterval(interval);
    await producer.disconnect();
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  logger.info('Simulador corriendo. Presiona Ctrl+C para detener.');
}

main().catch((error) => {
  logger.error('Error fatal:', { error });
  process.exit(1);
});

