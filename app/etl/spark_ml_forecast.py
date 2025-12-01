from pyspark.sql import SparkSession
from pyspark.sql.functions import col, unix_timestamp, lit, avg, stddev
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression, RandomForestRegressor, GBTRegressor
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
import mysql.connector
import logging
from datetime import datetime, timedelta
import time
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("🤖 SPARK ML - BIG DATA FORECASTING")
logger.info("=" * 80)

DB_CONFIG = {
    "host": "mysql",
    "port": 3306,
    "user": "root",
    "password": "Os51t=Ag/3=B",
    "database": "emergentETL"
}

def get_spark_session():
    return SparkSession.builder \
        .appName("SparkML_BigData_Forecast") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def read_data_from_mysql(spark, table_name):
    """Lee datos desde MySQL usando pandas y los convierte a Spark DataFrame"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        query = f"SELECT * FROM {table_name}"
        pdf = pd.read_sql(query, conn)
        conn.close()
        
        if pdf.empty:
            logger.warning(f"No hay datos en la tabla {table_name}")
            return None
            
        df = spark.createDataFrame(pdf)
        logger.info(f"✅ Leídos {df.count()} registros de {table_name}")
        return df
    except Exception as e:
        logger.error(f"❌ Error leyendo de MySQL tabla {table_name}: {e}")
        return None

def detect_anomalies(df, column_name):
    """Detecta anomalías usando Z-score"""
    try:
        stats = df.select(
            avg(col(column_name)).alias('mean'),
            stddev(col(column_name)).alias('stddev')
        ).collect()[0]
        
        mean_val = stats['mean']
        stddev_val = stats['stddev']
        
        if mean_val is None or stddev_val is None or stddev_val == 0:
            return df
        
        # Filtrar outliers (valores fuera de 3 desviaciones estándar)
        df_clean = df.filter(
            (col(column_name) >= mean_val - 3 * stddev_val) &
            (col(column_name) <= mean_val + 3 * stddev_val)
        )
        
        removed = df.count() - df_clean.count()
        if removed > 0:
            logger.info(f"🔍 Removidas {removed} anomalías de {column_name}")
        
        return df_clean
    except Exception as e:
        logger.error(f"Error en detección de anomalías: {e}")
        return df

def train_and_predict_em310(spark):
    """Entrena y predice para sensores EM310 (distancia)"""
    logger.info("🚀 Entrenando modelo para EM310 (Distancia)...")
    
    df = read_data_from_mysql(spark, "em310_soterrados")
    
    if df is None or df.count() < 10:
        logger.warning("⚠️ Datos insuficientes para entrenar EM310")
        return
    
    # Preprocesamiento
    df_clean = df.filter(col("distance").isNotNull()) \
                 .withColumn("timestamp_num", unix_timestamp("time")) \
                 .withColumn("label", col("distance").cast("double")) \
                 .select("timestamp_num", "label")
    
    # Detectar anomalías
    df_clean = detect_anomalies(df_clean, "label")
    
    if df_clean.count() < 5:
        logger.warning("⚠️ Muy pocos datos después de limpiar anomalías")
        return
    
    # Feature Engineering
    assembler = VectorAssembler(inputCols=["timestamp_num"], outputCol="features")
    
    # Modelos
    lr = LinearRegression(featuresCol="features", labelCol="label", maxIter=10)
    rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=20, maxDepth=5)
    gbt = GBTRegressor(featuresCol="features", labelCol="label", maxIter=10)
    
    # Split datos
    train_data, test_data = df_clean.randomSplit([0.8, 0.2], seed=42)
    
    # Entrenar modelos y seleccionar el mejor
    best_model = None
    best_r2 = -float('inf')
    best_model_name = ""
    
    evaluator = RegressionEvaluator(labelCol="label", metricName="r2")
    
    for model, name in [(lr, "LinearRegression"), (rf, "RandomForest"), (gbt, "GradientBoosting")]:
        try:
            pipeline = Pipeline(stages=[assembler, model])
            trained_model = pipeline.fit(train_data)
            predictions = trained_model.transform(test_data)
            r2 = evaluator.evaluate(predictions)
            
            logger.info(f"📊 {name} - R²: {r2:.4f}")
            
            if r2 > best_r2:
                best_r2 = r2
                best_model = trained_model
                best_model_name = name
        except Exception as e:
            logger.error(f"Error entrenando {name}: {e}")
            continue
    
    if best_model is None:
        logger.error("❌ No se pudo entrenar ningún modelo para EM310")
        return
    
    logger.info(f"✅ Mejor modelo para EM310: {best_model_name} (R²={best_r2:.4f})")
    
    # Generar predicciones futuras (próximas 24 horas)
    last_timestamp = df_clean.agg({"timestamp_num": "max"}).collect()[0][0]
    
    if last_timestamp is None:
        last_timestamp = time.time()
    
    future_times = [(last_timestamp + i * 3600,) for i in range(1, 25)]
    future_df = spark.createDataFrame(future_times, ["timestamp_num"])
    future_preds = best_model.transform(future_df)
    
    save_predictions(future_preds, "EM310", best_model_name)

def train_and_predict_em500(spark):
    """Entrena y predice para sensores EM500 (CO2, temperatura, humedad, presión)"""
    logger.info("🚀 Entrenando modelos para EM500 (CO2, Temperatura, Humedad, Presión)...")
    
    df = read_data_from_mysql(spark, "em500_co2")
    
    if df is None or df.count() < 10:
        logger.warning("⚠️ Datos insuficientes para entrenar EM500")
        return
    
    # Entrenar modelo para cada métrica
    metrics = [
        ("co2", "EM500_CO2"),
        ("temperature", "EM500_TEMP"),
        ("humidity", "EM500_HUM"),
        ("pressure", "EM500_PRES")
    ]
    
    for metric, sensor_type in metrics:
        try:
            logger.info(f"📈 Entrenando para {metric}...")
            
            df_clean = df.filter(col(metric).isNotNull()) \
                         .withColumn("timestamp_num", unix_timestamp("time")) \
                         .withColumn("label", col(metric).cast("double")) \
                         .select("timestamp_num", "label")
            
            df_clean = detect_anomalies(df_clean, "label")
            
            if df_clean.count() < 5:
                logger.warning(f"⚠️ Muy pocos datos para {metric}")
                continue
            
            assembler = VectorAssembler(inputCols=["timestamp_num"], outputCol="features")
            
            # Modelos
            lr = LinearRegression(featuresCol="features", labelCol="label", maxIter=10)
            rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=20, maxDepth=5)
            gbt = GBTRegressor(featuresCol="features", labelCol="label", maxIter=10)
            
            train_data, test_data = df_clean.randomSplit([0.8, 0.2], seed=42)
            
            # Seleccionar mejor modelo
            best_model = None
            best_r2 = -float('inf')
            best_model_name = ""
            
            evaluator = RegressionEvaluator(labelCol="label", metricName="r2")
            
            for model, name in [(lr, "LinearRegression"), (rf, "RandomForest"), (gbt, "GradientBoosting")]:
                try:
                    pipeline = Pipeline(stages=[assembler, model])
                    trained_model = pipeline.fit(train_data)
                    predictions = trained_model.transform(test_data)
                    r2 = evaluator.evaluate(predictions)
                    
                    logger.info(f"  📊 {name} - R²: {r2:.4f}")
                    
                    if r2 > best_r2:
                        best_r2 = r2
                        best_model = trained_model
                        best_model_name = name
                except Exception as e:
                    logger.error(f"  Error con {name}: {e}")
                    continue
            
            if best_model is None:
                logger.warning(f"❌ No se pudo entrenar modelo para {metric}")
                continue
            
            logger.info(f"✅ {metric} - Mejor: {best_model_name} (R²={best_r2:.4f})")
            
            # Predicciones futuras
            last_timestamp = df_clean.agg({"timestamp_num": "max"}).collect()[0][0]
            if last_timestamp is None:
                last_timestamp = time.time()
            
            future_times = [(last_timestamp + i * 3600,) for i in range(1, 25)]
            future_df = spark.createDataFrame(future_times, ["timestamp_num"])
            future_preds = best_model.transform(future_df)
            
            save_predictions(future_preds, sensor_type, best_model_name)
            
        except Exception as e:
            logger.error(f"❌ Error procesando {metric}: {e}")
            continue

def train_and_predict_ws302(spark):
    """Entrena y predice para sensores WS302 (LAeq, LAI, LAImax)"""
    logger.info("🚀 Entrenando modelos para WS302 (Niveles de Sonido)...")
    
    df = read_data_from_mysql(spark, "ws302_sonido")
    
    if df is None or df.count() < 10:
        logger.warning("⚠️ Datos insuficientes para entrenar WS302")
        return
    
    # Entrenar modelo para cada métrica de sonido
    metrics = [
        ("LAeq", "WS302_LAeq"),
        ("LAI", "WS302_LAI"),
        ("LAImax", "WS302_LAImax")
    ]
    
    for metric, sensor_type in metrics:
        try:
            logger.info(f"📈 Entrenando para {metric}...")
            
            df_clean = df.filter(col(metric).isNotNull()) \
                         .withColumn("timestamp_num", unix_timestamp("time")) \
                         .withColumn("label", col(metric).cast("double")) \
                         .select("timestamp_num", "label")
            
            df_clean = detect_anomalies(df_clean, "label")
            
            if df_clean.count() < 5:
                logger.warning(f"⚠️ Muy pocos datos para {metric}")
                continue
            
            assembler = VectorAssembler(inputCols=["timestamp_num"], outputCol="features")
            
            # Modelos
            lr = LinearRegression(featuresCol="features", labelCol="label", maxIter=10)
            rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=20, maxDepth=5)
            gbt = GBTRegressor(featuresCol="features", labelCol="label", maxIter=10)
            
            train_data, test_data = df_clean.randomSplit([0.8, 0.2], seed=42)
            
            # Seleccionar mejor modelo
            best_model = None
            best_r2 = -float('inf')
            best_model_name = ""
            
            evaluator = RegressionEvaluator(labelCol="label", metricName="r2")
            
            for model, name in [(lr, "LinearRegression"), (rf, "RandomForest"), (gbt, "GradientBoosting")]:
                try:
                    pipeline = Pipeline(stages=[assembler, model])
                    trained_model = pipeline.fit(train_data)
                    predictions = trained_model.transform(test_data)
                    r2 = evaluator.evaluate(predictions)
                    
                    logger.info(f"  📊 {name} - R²: {r2:.4f}")
                    
                    if r2 > best_r2:
                        best_r2 = r2
                        best_model = trained_model
                        best_model_name = name
                except Exception as e:
                    logger.error(f"  Error con {name}: {e}")
                    continue
            
            if best_model is None:
                logger.warning(f"❌ No se pudo entrenar modelo para {metric}")
                continue
            
            logger.info(f"✅ {metric} - Mejor: {best_model_name} (R²={best_r2:.4f})")
            
            # Predicciones futuras
            last_timestamp = df_clean.agg({"timestamp_num": "max"}).collect()[0][0]
            if last_timestamp is None:
                last_timestamp = time.time()
            
            future_times = [(last_timestamp + i * 3600,) for i in range(1, 25)]
            future_df = spark.createDataFrame(future_times, ["timestamp_num"])
            future_preds = best_model.transform(future_df)
            
            save_predictions(future_preds, sensor_type, best_model_name)
            
        except Exception as e:
            logger.error(f"❌ Error procesando {metric}: {e}")
            continue

def save_predictions(predictions_df, sensor_type, model_name):
    """Guarda predicciones en MySQL"""
    try:
        rows = predictions_df.select("timestamp_num", "prediction").collect()
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO predicciones (fecha_prediccion, tipo_sensor, valor_predicho, modelo_usado)
        VALUES (%s, %s, %s, %s)
        """
        
        count = 0
        for row in rows:
            ts = row.timestamp_num
            val = row.prediction
            dt = datetime.fromtimestamp(ts)
            
            cursor.execute(insert_query, (dt, sensor_type, val, model_name))
            count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"💾 Guardadas {count} predicciones para {sensor_type}")
    except Exception as e:
        logger.error(f"❌ Error guardando predicciones para {sensor_type}: {e}")

if __name__ == "__main__":
    spark = get_spark_session()
    
    logger.info("🎯 Iniciando proceso de Machine Learning para todos los sensores...")
    
    try:
        # Entrenar y predecir para los 3 tipos de sensores
        train_and_predict_em310(spark)
        train_and_predict_em500(spark)
        train_and_predict_ws302(spark)
        
        logger.info("✅ Proceso de ML completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en job ML: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        spark.stop()
