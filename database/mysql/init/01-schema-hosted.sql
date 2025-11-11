-- Esquema de base de datos para EmergentesETL (Base de datos hosteada)
-- Este script debe ejecutarse manualmente en tu base de datos MySQL hosteada
-- 
-- IMPORTANTE: 
-- 1. Cambia 'defaultdb' por el nombre de tu base de datos si es diferente
-- 2. Ejecuta este script usando tu cliente MySQL preferido o la consola de Aiven

-- Crear base de datos si no existe (opcional, si tienes permisos)
-- CREATE DATABASE IF NOT EXISTS defaultdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE defaultdb;

-- ============================================
-- TABLAS DE MÉTRICAS DE SONIDO
-- ============================================

-- Métricas de sonido (ventana 1 min)
CREATE TABLE IF NOT EXISTS sound_metrics_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    laeq_avg DECIMAL(10,2),
    lai_avg DECIMAL(10,2),
    laimax_max DECIMAL(10,2),
    p95_laeq DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Métricas de sonido (ventana 5 min)
CREATE TABLE IF NOT EXISTS sound_metrics_5m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    laeq_avg DECIMAL(10,2),
    lai_avg DECIMAL(10,2),
    laimax_max DECIMAL(10,2),
    p95_laeq DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Métricas de sonido (ventana 1 hora)
CREATE TABLE IF NOT EXISTS sound_metrics_1h (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    laeq_avg DECIMAL(10,2),
    lai_avg DECIMAL(10,2),
    laimax_max DECIMAL(10,2),
    p95_laeq DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLAS DE MÉTRICAS DE DISTANCIA
-- ============================================

-- Métricas de distancia (ventana 1 min)
CREATE TABLE IF NOT EXISTS distance_metrics_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    distance_avg DECIMAL(10,2),
    distance_min DECIMAL(10,2),
    distance_max DECIMAL(10,2),
    anomaly_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Métricas de distancia (ventana 5 min)
CREATE TABLE IF NOT EXISTS distance_metrics_5m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    distance_avg DECIMAL(10,2),
    distance_min DECIMAL(10,2),
    distance_max DECIMAL(10,2),
    anomaly_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Métricas de distancia (ventana 1 hora)
CREATE TABLE IF NOT EXISTS distance_metrics_1h (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    distance_avg DECIMAL(10,2),
    distance_min DECIMAL(10,2),
    distance_max DECIMAL(10,2),
    anomaly_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLAS DE MÉTRICAS DE AIRE
-- ============================================

-- Métricas de aire (ventana 1 min)
CREATE TABLE IF NOT EXISTS air_metrics_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    co2_avg DECIMAL(10,2),
    temp_avg DECIMAL(10,2),
    rh_avg DECIMAL(10,2),
    press_avg DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Métricas de aire (ventana 5 min)
CREATE TABLE IF NOT EXISTS air_metrics_5m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    co2_avg DECIMAL(10,2),
    temp_avg DECIMAL(10,2),
    rh_avg DECIMAL(10,2),
    press_avg DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Métricas de aire (ventana 1 hora)
CREATE TABLE IF NOT EXISTS air_metrics_1h (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    co2_avg DECIMAL(10,2),
    temp_avg DECIMAL(10,2),
    rh_avg DECIMAL(10,2),
    press_avg DECIMAL(10,2),
    alert_prob DECIMAL(5,4),
    sample_n INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_window (sensor_id, window_start),
    INDEX idx_window_start (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

