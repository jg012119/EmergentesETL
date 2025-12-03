import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import numpy as np

st.set_page_config(page_title="Dashboard IoT - Big Data ML", page_icon="📊", layout="wide")

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": "mysql",
    "port": 3306,
    "user": "root",
    "password": "Os51t=Ag/3=B",
    "database": "emergentETL"
}

@st.cache_resource
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def load_data(query):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return pd.DataFrame()

def get_stats():
    """Obtiene estadísticas generales de todos los sensores"""
    query = """
    SELECT 
        (SELECT COUNT(*) FROM em310_soterrados) as em310_count,
        (SELECT COUNT(*) FROM em500_co2) as em500_count,
        (SELECT COUNT(*) FROM ws302_sonido) as ws302_count,
        (SELECT COUNT(*) FROM predicciones) as predicciones_count
    """
    df = load_data(query)
    return df.iloc[0] if not df.empty else None

# Título
st.title("📊 Dashboard IoT - Big Data & Machine Learning")
st.markdown("---")

# Mostrar estadísticas generales
st.header("📈 Estadísticas Generales")
stats = get_stats()

if stats is not None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔵 EM310 Soterrados", f"{int(stats['em310_count']):,}")
    with col2:
        st.metric("🟢 EM500 CO2", f"{int(stats['em500_count']):,}")
    with col3:
        st.metric("🟡 WS302 Sonido", f"{int(stats['ws302_count']):,}")
    with col4:
        st.metric("🤖 Predicciones ML", f"{int(stats['predicciones_count']):,}")

st.divider()

# Sidebar
st.sidebar.header("⚙️ Configuración")
sensor_type = st.sidebar.selectbox(
    "Seleccionar Tipo de Sensor",
    ["EM310 Soterrados", "EM500 CO2", "WS302 Sonido"]
)

limit = st.sidebar.slider("Registros a mostrar", 10, 500, 100, 10)

# ========================================
# EM310 SOTERRADOS
# ========================================
if sensor_type == "EM310 Soterrados":
    st.header("🔵 Sensores de Distancia (Soterrados)")
    
    # Datos Históricos en Tiempo Real
    st.subheader("📡 Datos Históricos en Tiempo Real")
    df_real = load_data(f"SELECT time, device_name, distance, status FROM em310_soterrados ORDER BY time DESC LIMIT {limit}")
    
    if not df_real.empty:
        # Convertir distance a numérico
        df_real['distance'] = pd.to_numeric(df_real['distance'], errors='coerce')
        df_real = df_real.dropna(subset=['distance'])
        
        # Mostrar tabla (últimos 20 registros)
        st.dataframe(df_real.head(20), use_container_width=True)
        
        # Gráfico histórico
        fig = px.line(df_real.sort_values('time'), x='time', y='distance', 
                      title='Evolución de Distancia (Datos Históricos)',
                      labels={'distance': 'Distancia (cm)', 'time': 'Tiempo'},
                      markers=True)
        fig.update_layout(hovermode='x unified', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 Distancia Promedio", f"{df_real['distance'].mean():.2f} cm")
        with col2:
            st.metric("⬆️ Distancia Máxima", f"{df_real['distance'].max():.2f} cm")
        with col3:
            st.metric("⬇️ Distancia Mínima", f"{df_real['distance'].min():.2f} cm")
    else:
        st.info("⚠️ No hay datos disponibles aún.")
    
    # Predicciones ML (Sección separada)
    st.divider()
    st.subheader("🤖 Predicciones de Machine Learning (Próximas 24 horas)")
    
    df_pred = load_data("SELECT fecha_prediccion, valor_predicho, modelo_usado FROM predicciones WHERE tipo_sensor='EM310' ORDER BY fecha_prediccion ASC")
    
    if not df_pred.empty:
        fig = px.line(df_pred, x='fecha_prediccion', y='valor_predicho',
                      title=f'Predicciones EM310 - Modelo: {df_pred["modelo_usado"].iloc[0]}',
                      labels={'valor_predicho': 'Distancia Predicha (cm)', 'fecha_prediccion': 'Fecha/Hora'},
                      markers=True,
                      color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(hovermode='x unified', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Información del modelo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Predicciones", len(df_pred))
        with col2:
            st.metric("🤖 Modelo Usado", df_pred['modelo_usado'].iloc[0])
        with col3:
            st.metric("🔮 Rango Temporal", "24 horas")
    else:
        st.info("⚠️ No hay predicciones generadas aún. Ejecute el job de ML.")

# ========================================
# EM500 CO2
# ========================================
elif sensor_type == "EM500 CO2":
    st.header("🟢 Sensores de Calidad de Aire (CO2)")
    
    # Datos Históricos en Tiempo Real
    st.subheader("📡 Datos Históricos en Tiempo Real")
    df_real = load_data(f"SELECT time, device_name, co2, temperature, humidity, pressure FROM em500_co2 ORDER BY time DESC LIMIT {limit}")
    
    if not df_real.empty:
        # Convertir a numérico
        for col in ['co2', 'temperature', 'humidity', 'pressure']:
            df_real[col] = pd.to_numeric(df_real[col], errors='coerce')
        
        df_real = df_real.dropna(subset=['co2', 'temperature', 'humidity'])
        
        # Mostrar tabla (solo 20 registros)
        st.dataframe(df_real.head(20), use_container_width=True)
        
        # Gráficos históricos en columnas
        col1, col2 = st.columns(2)
        
        with col1:
            fig_co2 = px.line(df_real.sort_values('time'), x='time', y='co2',
                              title='CO2 - Datos Históricos',
                              labels={'co2': 'CO2 (ppm)', 'time': 'Tiempo'},
                              markers=True)
            fig_co2.update_layout(hovermode='x unified', height=350)
            st.plotly_chart(fig_co2, use_container_width=True)
            
            fig_temp = px.line(df_real.sort_values('time'), x='time', y='temperature',
                               title='Temperatura - Datos Históricos',
                               labels={'temperature': 'Temperatura (°C)', 'time': 'Tiempo'},
                               markers=True)
            fig_temp.update_layout(hovermode='x unified', height=350)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            fig_hum = px.line(df_real.sort_values('time'), x='time', y='humidity',
                              title='Humedad - Datos Históricos',
                              labels={'humidity': 'Humedad (%)', 'time': 'Tiempo'},
                              markers=True)
            fig_hum.update_layout(hovermode='x unified', height=350)
            st.plotly_chart(fig_hum, use_container_width=True)
            
            if 'pressure' in df_real.columns:
                fig_pres = px.line(df_real.sort_values('time'), x='time', y='pressure',
                                   title='Presión - Datos Históricos',
                                   labels={'pressure': 'Presión (hPa)', 'time': 'Tiempo'},
                                   markers=True)
                fig_pres.update_layout(hovermode='x unified', height=350)
                st.plotly_chart(fig_pres, use_container_width=True)
    else:
        st.info("⚠️ No hay datos disponibles aún.")
    
    # Predicciones ML (Sección separada)
    st.divider()
    st.subheader("🤖 Predicciones de Machine Learning (Próximas 24 horas)")
    
    pred_types = [
        ("EM500_CO2", "CO2 (ppm)"),
        ("EM500_TEMP", "Temperatura (°C)"),
        ("EM500_HUM", "Humedad (%)"),
        ("EM500_PRES", "Presión (hPa)")
    ]
    
    tabs = st.tabs(["CO2", "Temperatura", "Humedad", "Presión"])
    
    for idx, (sensor_pred, label) in enumerate(pred_types):
        with tabs[idx]:
            df_pred = load_data(f"SELECT fecha_prediccion, valor_predicho, modelo_usado FROM predicciones WHERE tipo_sensor='{sensor_pred}' ORDER BY fecha_prediccion ASC")
            
            if not df_pred.empty:
                fig = px.line(df_pred, x='fecha_prediccion', y='valor_predicho',
                              title=f'Predicciones {label} - Modelo: {df_pred["modelo_usado"].iloc[0]}',
                              labels={'valor_predicho': label, 'fecha_prediccion': 'Fecha/Hora'},
                              markers=True,
                              color_discrete_sequence=['#ff7f0e'])
                fig.update_layout(hovermode='x unified', height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Información del modelo
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Predicciones", len(df_pred))
                with col2:
                    st.metric("🤖 Modelo", df_pred['modelo_usado'].iloc[0])
                with col3:
                    st.metric("🔮 Rango", "24 horas")
            else:
                st.info("⚠️ No hay predicciones generadas aún.")

# ========================================
# WS302 SONIDO
# ========================================
elif sensor_type == "WS302 Sonido":
    st.header("🟡 Sensores de Calidad de Sonido")
    
    # Datos Históricos en Tiempo Real
    st.subheader("📡 Datos Históricos en Tiempo Real")
    df_real = load_data(f"SELECT time, tenant_name, LAeq, LAI, LAImax, status FROM ws302_sonido ORDER BY time DESC LIMIT {limit}")
    
    if not df_real.empty:
        # Convertir a numérico
        for col in ['LAeq', 'LAI', 'LAImax']:
            df_real[col] = pd.to_numeric(df_real[col], errors='coerce')
        
        df_real = df_real.dropna(subset=['LAeq'])
        
        # Mostrar tabla (solo 20 registros)
        st.dataframe(df_real.head(20), use_container_width=True)
        
        # Gráficos históricos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_laeq = px.line(df_real.sort_values('time'), x='time', y='LAeq',
                               title='LAeq - Datos Históricos',
                               labels={'LAeq': 'LAeq (dB)', 'time': 'Tiempo'},
                               markers=True, color_discrete_sequence=['#FFA500'])
            fig_laeq.update_layout(hovermode='x unified', height=350)
            st.plotly_chart(fig_laeq, use_container_width=True)
        
        with col2:
            fig_lai = px.line(df_real.sort_values('time'), x='time', y='LAI',
                              title='LAI - Datos Históricos',
                              labels={'LAI': 'LAI (dB)', 'time': 'Tiempo'},
                              markers=True, color_discrete_sequence=['#FF6347'])
            fig_lai.update_layout(hovermode='x unified', height=350)
            st.plotly_chart(fig_lai, use_container_width=True)
        
        with col3:
            fig_laimax = px.line(df_real.sort_values('time'), x='time', y='LAImax',
                                 title='LAImax - Datos Históricos',
                                 labels={'LAImax': 'LAImax (dB)', 'time': 'Tiempo'},
                                 markers=True, color_discrete_sequence=['#DC143C'])
            fig_laimax.update_layout(hovermode='x unified', height=350)
            st.plotly_chart(fig_laimax, use_container_width=True)
        
        # Estadísticas
        st.subheader("📊 Estadísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔊 LAeq Promedio", f"{df_real['LAeq'].mean():.2f} dB")
        with col2:
            st.metric("🔊 LAI Promedio", f"{df_real['LAI'].mean():.2f} dB")
        with col3:
            st.metric("🔊 LAImax Promedio", f"{df_real['LAImax'].mean():.2f} dB")
    else:
        st.info("⚠️ No hay datos disponibles aún.")
    
    # Predicciones ML (Sección separada)
    st.divider()
    st.subheader("🤖 Predicciones de Machine Learning (Próximas 24 horas)")
    
    pred_types = [
        ("WS302_LAeq", "LAeq (dB)"),
        ("WS302_LAI", "LAI (dB)"),
        ("WS302_LAImax", "LAImax (dB)")
    ]
    
    tabs = st.tabs(["LAeq", "LAI", "LAImax"])
    
    for idx, (sensor_pred, label) in enumerate(pred_types):
        with tabs[idx]:
            df_pred = load_data(f"SELECT fecha_prediccion, valor_predicho, modelo_usado FROM predicciones WHERE tipo_sensor='{sensor_pred}' ORDER BY fecha_prediccion ASC")
            
            if not df_pred.empty:
                fig = px.line(df_pred, x='fecha_prediccion', y='valor_predicho',
                              title=f'Predicciones {label} - Modelo: {df_pred["modelo_usado"].iloc[0]}',
                              labels={'valor_predicho': label, 'fecha_prediccion': 'Fecha/Hora'},
                              markers=True,
                              color_discrete_sequence=['#ff7f0e'])
                fig.update_layout(hovermode='x unified', height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Información del modelo
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Predicciones", len(df_pred))
                with col2:
                    st.metric("🤖 Modelo", df_pred['modelo_usado'].iloc[0])
                with col3:
                    st.metric("🔮 Rango", "24 horas")
            else:
                st.info("⚠️ No hay predicciones generadas aún.")

# ========================================
# MÉTRICAS DE MACHINE LEARNING
# ========================================
if st.sidebar.checkbox("📊 Mostrar Métricas de ML"):
    st.divider()
    st.header("🤖 Métricas de Machine Learning")
    
    # Selector de tipo de sensor
    all_sensors = ["Todos", "EM310", "EM500_CO2", "EM500_TEMP", "EM500_HUM", "EM500_PRES", 
                   "WS302_LAeq", "WS302_LAI", "WS302_LAImax"]
    sensor_filter = st.selectbox("🔍 Filtrar por tipo de sensor", all_sensors)
    
    # Cargar métricas
    if sensor_filter == "Todos":
        metrics_query = "SELECT * FROM ml_metricas ORDER BY fecha_generacion DESC"
    else:
        metrics_query = f"SELECT * FROM ml_metricas WHERE tipo_sensor='{sensor_filter}' ORDER BY fecha_generacion DESC"
    
    df_metrics = load_data(metrics_query)
    
    if not df_metrics.empty:
        # Mostrar tabla de métricas
        st.subheader("📈 Tabla de Métricas de Evaluación")
        st.dataframe(
            df_metrics[['fecha_generacion', 'tipo_sensor', 'modelo', 'r2_score', 'rmse', 'mae']].head(20),
            use_container_width=True
        )
        
        # Gráfico comparativo de modelos
        st.subheader("📊 Comparación de Modelos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de R² por modelo
            fig_r2 = px.bar(
                df_metrics.groupby(['tipo_sensor', 'modelo'])['r2_score'].mean().reset_index(),
                x='modelo', y='r2_score', color='tipo_sensor',
                title='R² Score Promedio por Modelo y Sensor',
                labels={'r2_score': 'R² Score', 'modelo': 'Modelo'},
                barmode='group'
            )
            fig_r2.update_layout(height=400)
            st.plotly_chart(fig_r2, use_container_width=True)
        
        with col2:
            # Gráfico de RMSE por modelo
            fig_rmse = px.bar(
                df_metrics.groupby(['tipo_sensor', 'modelo'])['rmse'].mean().reset_index(),
                x='modelo', y='rmse', color='tipo_sensor',
                title='RMSE Promedio por Modelo y Sensor',
                labels={'rmse': 'RMSE', 'modelo': 'Modelo'},
                barmode='group'
            )
            fig_rmse.update_layout(height=400)
            st.plotly_chart(fig_rmse, use_container_width=True)
        
        # MAE
        fig_mae = px.bar(
            df_metrics.groupby(['tipo_sensor', 'modelo'])['mae'].mean().reset_index(),
            x='modelo', y='mae', color='tipo_sensor',
            title='MAE Promedio por Modelo y Sensor',
            labels={'mae': 'MAE', 'modelo': 'Modelo'},
            barmode='group'
        )
        fig_mae.update_layout(height=400)
        st.plotly_chart(fig_mae, use_container_width=True)
        
        # Matriz de Confusión
        st.divider()
        st.subheader("🎯 Matriz de Confusión")
        
        # Obtener sensores únicos con matrices de confusión
        if sensor_filter == "Todos":
            cm_query = "SELECT DISTINCT tipo_sensor FROM confusion_matrix ORDER BY tipo_sensor"
        else:
            cm_query = f"SELECT DISTINCT tipo_sensor FROM confusion_matrix WHERE tipo_sensor='{sensor_filter}'"
        
        df_sensors = load_data(cm_query)
        
        if not df_sensors.empty and len(df_sensors) > 0:
            sensor_tabs = st.tabs(df_sensors['tipo_sensor'].tolist())
            
            for idx, sensor in enumerate(df_sensors['tipo_sensor'].tolist()):
                with sensor_tabs[idx]:
                    # Obtener datos de matriz de confusión para este sensor
                    cm_query = f"""
                    SELECT modelo, true_label, predicted_label, count 
                    FROM confusion_matrix 
                    WHERE tipo_sensor='{sensor}' 
                    ORDER BY fecha_generacion DESC
                    LIMIT 9
                    """
                    df_cm = load_data(cm_query)
                    
                    if not df_cm.empty and len(df_cm) > 0:
                        modelo = df_cm['modelo'].iloc[0]
                        
                        # Crear matriz 3x3
                        labels = ['bajo', 'medio', 'alto']
                        matrix = np.zeros((3, 3))
                        
                        for _, row in df_cm.iterrows():
                            true_idx = labels.index(row['true_label'])
                            pred_idx = labels.index(row['predicted_label'])
                            matrix[true_idx][pred_idx] = row['count']
                        
                        # Crear heatmap
                        fig_cm = go.Figure(data=go.Heatmap(
                            z=matrix,
                            x=['Bajo (pred)', 'Medio (pred)', 'Alto (pred)'],
                            y=['Bajo (real)', 'Medio (real)', 'Alto (real)'],
                            colorscale='Blues',
                            text=matrix.astype(int),
                            texttemplate='%{text}',
                            textfont={"size": 16},
                            hoverongaps=False
                        ))
                        
                        fig_cm.update_layout(
                            title=f'Matriz de Confusión - {sensor} ({modelo})',
                            xaxis_title='Valores Predichos',
                            yaxis_title='Valores Reales',
                            height=400
                        )
                        
                        st.plotly_chart(fig_cm, use_container_width=True)
                        
                        # Calcular accuracy
                        total = matrix.sum()
                        correct = matrix.diagonal().sum()
                        accuracy = (correct / total * 100) if total > 0 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎯 Accuracy", f"{accuracy:.2f}%")
                        with col2:
                            st.metric("📊 Total Muestras", f"{int(total)}")
                        with col3:
                            st.metric("✅ Correctos", f"{int(correct)}")
                    else:
                        st.info("⚠️ No hay datos de matriz de confusión para este sensor.")
        else:
            st.info("⚠️ No hay matrices de confusión generadas aún.")
    else:
        st.info("⚠️ No hay métricas disponibles. Ejecute el job de ML primero.")

# Footer
st.divider()
st.caption("🔄 Dashboard actualizado cada 10 segundos | 🤖 Big Data ML con Apache Spark")

# Auto-refresh cada 10 segundos
import time
time.sleep(10)
st.rerun()

