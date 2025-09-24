
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Análisis Temperatura Mínima Perú",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Cargar datos procesados"""
    try:
        stats = pd.read_csv('estadisticas_temperatura_distritos.csv')
        with open('metricas_resumen.json', 'r') as f:
            metricas = json.load(f)
        return stats, metricas
    except Exception as e:
        st.error(f"Error cargando archivos: {e}")
        return None, None

def main():
    """Función principal de la aplicación"""
    
    st.title("🧊 Análisis de Temperatura Mínima en Perú")
    st.markdown("### Análisis de riesgos climáticos y propuestas de políticas públicas")
    
    # Cargar datos
    datos, metricas = load_data()
    
    if datos is None:
        st.error("No se pudieron cargar los datos.")
        return
    
    # Sidebar con navegación
    st.sidebar.title("🧭 Navegación")
    
    opciones_menu = [
        "📊 Resumen Ejecutivo",
        "📈 Estadísticas Zonales", 
        "📉 Visualizaciones",
        "🗺️ Mapa Estático",
        "💾 Descarga de Datos",
        "🏛️ Políticas Públicas"
    ]
    
    seleccion = st.sidebar.selectbox("Selecciona una sección:", opciones_menu)
    
    # Ejecutar sección seleccionada
    if seleccion == "📊 Resumen Ejecutivo":
        show_resumen(metricas)
    elif seleccion == "📈 Estadísticas Zonales":
        show_estadisticas(datos)
    elif seleccion == "📉 Visualizaciones":
        show_visualizaciones(datos)
    elif seleccion == "🗺️ Mapa Estático":
        show_mapa()
    elif seleccion == "💾 Descarga de Datos":
        show_descarga(datos)
    elif seleccion == "🏛️ Políticas Públicas":
        show_politicas()

def show_resumen(metricas):
    st.header("📊 Resumen Ejecutivo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Distritos", f"{metricas['total_distritos']:,}")
    with col2:
        st.metric("Alto Riesgo", f"{metricas['distritos_alto_riesgo']:,}")
    with col3:
        st.metric("Temp. Media", f"{metricas['temp_media_nacional']:.1f}°C")
    with col4:
        st.metric("Distrito Más Frío", metricas['distrito_mas_frio'])

def show_estadisticas(datos):
    st.header("📈 Estadísticas Zonales")
    
    st.subheader("Explorador de Datos")
    columnas = ['DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'mean', 'min', 'max', 'std']
    st.dataframe(datos[columnas].head(20), use_container_width=True)

def show_visualizaciones(datos):
    st.header("📉 Visualizaciones")
    
    # Distribución
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(datos['mean'].dropna(), bins=40, alpha=0.7, color='skyblue')
    ax.set_title('Distribución de Temperatura Media por Distrito')
    ax.set_xlabel('Temperatura (°C)')
    ax.set_ylabel('Frecuencia')
    st.pyplot(fig)
    
    # Rankings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥶 Top 10 Más Fríos")
        frios = datos.nsmallest(10, 'mean')[['DISTRITO', 'DEPARTAMEN', 'mean']]
        st.dataframe(frios)
    
    with col2:
        st.subheader("🔥 Top 10 Más Cálidos") 
        calidos = datos.nlargest(10, 'mean')[['DISTRITO', 'DEPARTAMEN', 'mean']]
        st.dataframe(calidos)

def show_mapa():
    st.header("🗺️ Mapa de Temperatura")
    try:
        st.image("mapa_temperatura_distritos.png")
    except:
        st.warning("Mapa no disponible")

def show_descarga(datos):
    st.header("💾 Descarga de Datos")
    
    csv = datos.to_csv(index=False)
    st.download_button(
        label="📊 Descargar Datos Completos (CSV)",
        data=csv,
        file_name="estadisticas_temperatura.csv",
        mime="text/csv"
    )

def show_politicas():
    st.header("🏛️ Propuestas de Políticas Públicas")
    
    st.subheader("🏠 Propuesta 1: Viviendas Térmicas")
    st.markdown("""
    - **Objetivo**: Reducir IRA en 30%
    - **Población**: Distritos con Tmin ≤ percentil 10
    - **Costo**: S/ 15,000 por vivienda
    - **KPI**: -30% casos IRA registrados
    """)
    
    st.subheader("🌾 Propuesta 2: Kits Anti-helada")
    st.markdown("""
    - **Objetivo**: Reducir pérdidas agrícolas en 25%
    - **Población**: Productores en zonas de riesgo
    - **Costo**: S/ 500 por kit
    - **KPI**: -25% pérdidas en cultivos
    """)
    
    st.subheader("🦙 Propuesta 3: Refugios para Camélidos")
    st.markdown("""
    - **Objetivo**: Reducir mortalidad en 40%
    - **Población**: Comunidades ganaderas alto-andinas
    - **Costo**: S/ 8,000 por refugio
    - **KPI**: -40% mortalidad durante friaje
    """)

if __name__ == "__main__":
    main()
