import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import warnings
import os
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Análisis Geoespacial de Temperatura Mínima en Perú",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #4472C4;
        padding-bottom: 1rem;
    }
    .section-header {
        color: #2E75B6;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4472C4;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d6eaf8;
        border: 1px solid #aed6f1;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Carga datos con manejo robusto de rutas para local y cloud"""
    try:
        # Posibles ubicaciones de archivos
        csv_paths = [
            'estadisticas_temperatura_distritos.csv',  # Ejecución local desde app/
            'app/estadisticas_temperatura_distritos.csv',  # Ejecución cloud desde raíz
            './estadisticas_temperatura_distritos.csv',
            './app/estadisticas_temperatura_distritos.csv'
        ]
        
        json_paths = [
            'metricas_resumen.json',
            'app/metricas_resumen.json',
            './metricas_resumen.json', 
            './app/metricas_resumen.json'
        ]
        
        # Buscar y cargar CSV
        stats = None
        csv_found = None
        for path in csv_paths:
            if os.path.exists(path):
                try:
                    stats = pd.read_csv(path)
                    csv_found = path
                    break
                except Exception as e:
                    continue
        
        if stats is None:
            # Debug: mostrar archivos disponibles
            st.error("CSV no encontrado. Archivos disponibles:")
            st.write("Directorio actual:", os.listdir('.'))
            if os.path.exists('app'):
                st.write("Carpeta app:", os.listdir('app'))
            raise FileNotFoundError("Archivo CSV no encontrado en ninguna ubicación")
        
        # Buscar y cargar JSON
        metricas = None
        json_found = None
        for path in json_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        metricas = json.load(f)
                    json_found = path
                    break
                except Exception as e:
                    continue
        
        if metricas is None:
            raise FileNotFoundError("Archivo JSON no encontrado")
        
        # Validaciones
        if stats.empty:
            st.error("El archivo de estadísticas está vacío")
            return None, None
            
        required_columns = ['DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'mean', 'min', 'max', 'std']
        missing_cols = [col for col in required_columns if col not in stats.columns]
        if missing_cols:
            st.error(f"Faltan columnas requeridas: {missing_cols}")
            return None, None
            
        return stats, metricas
        
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None

def create_advanced_distribution_plot(datos):
    """Crea visualizaciones avanzadas de distribución"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distribución de Temperatura Media', 'Box Plot por Departamentos', 
                       'Densidad por Regiones', 'Correlación Temp vs Variabilidad'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Histograma
    fig.add_trace(
        go.Histogram(x=datos['mean'], nbinsx=40, name='Distribución', 
                    marker_color='lightblue', opacity=0.7),
        row=1, col=1
    )
    
    # Box plot por departamentos top
    top_depts = datos.groupby('DEPARTAMEN')['mean'].count().nlargest(8).index
    dept_data = datos[datos['DEPARTAMEN'].isin(top_depts)]
    
    for dept in top_depts:
        dept_temps = dept_data[dept_data['DEPARTAMEN'] == dept]['mean']
        fig.add_trace(
            go.Box(y=dept_temps, name=dept[:8], showlegend=False),
            row=1, col=2
        )
    
    # Scatter plot temperatura vs variabilidad
    fig.add_trace(
        go.Scatter(x=datos['mean'], y=datos['std'], mode='markers',
                  marker=dict(size=5, opacity=0.6, color=datos['mean'], 
                            colorscale='RdYlBu_r', showscale=True),
                  name='Distritos', showlegend=False),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, 
                     title_text="Análisis Estadístico Avanzado de Temperatura")
    
    return fig

def show_executive_summary(metricas, datos):
    """Resumen ejecutivo mejorado"""
    st.markdown('<div class="main-header">Resumen Ejecutivo - Análisis de Temperatura Mínima</div>', unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Total Distritos Analizados", 
            value=f"{metricas['total_distritos']:,}",
            help="Cobertura completa del territorio nacional peruano"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Distritos en Alto Riesgo", 
            value=f"{metricas['distritos_alto_riesgo']:,}",
            delta=f"{(metricas['distritos_alto_riesgo']/metricas['total_distritos']*100):.1f}%",
            help="Distritos con temperatura ≤ percentil 10"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Temperatura Media Nacional", 
            value=f"{metricas['temp_media_nacional']:.1f}°C",
            help="Promedio de temperatura media distrital"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        variabilidad_promedio = datos['std'].mean()
        st.metric(
            label="Variabilidad Térmica", 
            value=f"{variabilidad_promedio:.1f}°C",
            help="Desviación estándar promedio"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Hallazgos clave
    st.markdown('<div class="section-header">Hallazgos Principales</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="warning-box">
        <h4>Zona Crítica Identificada</h4>
        <p><strong>Distrito más frío:</strong><br>{metricas['distrito_mas_frio']}</p>
        <p><strong>Temperatura:</strong> {metricas['temp_minima_extrema']:.2f}°C</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dept_mas_afectado = datos[datos['mean'] <= metricas['umbral_alto_riesgo']].groupby('DEPARTAMEN').size().idxmax()
        distritos_afectados = datos[datos['mean'] <= metricas['umbral_alto_riesgo']].groupby('DEPARTAMEN').size().max()
        
        st.markdown(f"""
        <div class="warning-box">
        <h4>Departamento Más Vulnerable</h4>
        <p><strong>Departamento:</strong> {dept_mas_afectado}</p>
        <p><strong>Distritos en riesgo:</strong> {distritos_afectados}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="success-box">
        <h4>Cobertura del Análisis</h4>
        <p><strong>Metodología:</strong> Estadísticas zonales</p>
        <p><strong>Precisión:</strong> ~1km</p>
        <p><strong>Estándar:</strong> EPSG:4326 + UTM</p>
        </div>
        """, unsafe_allow_html=True)

def show_zonal_statistics(datos):
    """Estadísticas zonales con análisis técnico"""
    st.markdown('<div class="main-header">Estadísticas Zonales - Análisis Técnico</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Metodología de Análisis Geoespacial
    
    El análisis utiliza técnicas de estadísticas zonales para extraer información cuantitativa 
    del raster de temperatura usando límites administrativos distritales.
    """)
    
    # Filtros interactivos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        departamentos = ['Todos'] + sorted(datos['DEPARTAMEN'].unique().tolist())
        dept_seleccionado = st.selectbox("Departamento:", departamentos)
    
    with col2:
        temp_min, temp_max = st.slider("Rango Temperatura (°C):", 
                                      float(datos['mean'].min()), float(datos['mean'].max()), 
                                      (float(datos['mean'].min()), float(datos['mean'].max())))
    
    with col3:
        orden_columnas = ['mean', 'min', 'max', 'std']
        columna_orden = st.selectbox("Ordenar por:", orden_columnas)
    
    # Aplicar filtros
    datos_filtrados = datos.copy()
    
    if dept_seleccionado != 'Todos':
        datos_filtrados = datos_filtrados[datos_filtrados['DEPARTAMEN'] == dept_seleccionado]
    
    datos_filtrados = datos_filtrados[
        (datos_filtrados['mean'] >= temp_min) & 
        (datos_filtrados['mean'] <= temp_max)
    ]
    
    datos_filtrados = datos_filtrados.sort_values(columna_orden, ascending=False)
    
    # Mostrar resultados
    st.markdown(f"**Resultados:** {len(datos_filtrados):,} distritos encontrados")
    
    columnas_mostrar = ['DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'mean', 'min', 'max', 'std']
    datos_display = datos_filtrados[columnas_mostrar].round(2)
    
    st.dataframe(datos_display, use_container_width=True, height=400)

def show_advanced_visualizations(datos):
    """Visualizaciones avanzadas"""
    st.markdown('<div class="main-header">Análisis Visual Avanzado</div>', unsafe_allow_html=True)
    
    # Gráfico de distribución avanzado
    fig_dist = create_advanced_distribution_plot(datos)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Rankings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distritos Más Fríos")
        frios = datos.nsmallest(15, 'mean')[['DISTRITO', 'DEPARTAMEN', 'mean']].round(2)
        st.dataframe(frios, hide_index=True)
    
    with col2:
        st.subheader("Distritos Más Cálidos") 
        calidos = datos.nlargest(15, 'mean')[['DISTRITO', 'DEPARTAMEN', 'mean']].round(2)
        st.dataframe(calidos, hide_index=True)

def show_static_map():
    """Mapa estático con rutas flexibles"""
    st.markdown('<div class="main-header">Cartografía Temática</div>', unsafe_allow_html=True)
    
    # Buscar imagen del mapa
    map_paths = [
        'mapa_temperatura_distritos.png',
        'app/mapa_temperatura_distritos.png',
        './mapa_temperatura_distritos.png',
        './app/mapa_temperatura_distritos.png'
    ]
    
    map_found = None
    for path in map_paths:
        if os.path.exists(path):
            map_found = path
            break
    
    if map_found:
        st.image(map_found, 
                caption="Mapa de temperatura mínima por distrito - Perú",
                use_column_width=True)
    else:
        st.error("Mapa estático no disponible")
        st.info("El mapa se genera durante el procesamiento en el notebook")

def show_data_download(datos):
    """Descarga de datos"""
    st.markdown('<div class="main-header">Centro de Descarga</div>', unsafe_allow_html=True)
    
    st.markdown("### Datasets Disponibles")
    
    # Dataset completo
    csv_completo = datos.to_csv(index=False)
    st.download_button(
        label="📊 Descargar Dataset Completo (CSV)",
        data=csv_completo,
        file_name="temperatura_minima_peru_completo.csv",
        mime="text/csv",
        help="Todas las métricas calculadas para 1,873 distritos"
    )
    
    # Dataset de alto riesgo
    umbral_riesgo = datos['mean'].quantile(0.1)
    alto_riesgo = datos[datos['mean'] <= umbral_riesgo]
    csv_riesgo = alto_riesgo.to_csv(index=False)
    
    st.download_button(
        label="🚨 Distritos Alto Riesgo (CSV)",
        data=csv_riesgo,
        file_name="distritos_alto_riesgo_friaje.csv",
        mime="text/csv",
        help=f"Distritos con temperatura ≤ {umbral_riesgo:.1f}°C"
    )

def show_public_policies():
    """Políticas públicas detalladas"""
    st.markdown('<div class="main-header">Marco de Políticas Públicas</div>', unsafe_allow_html=True)
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs([
        "🏠 Viviendas Térmicas", 
        "🌾 Protección Agrícola",
        "🦙 Protección Ganadera"
    ])
    
    with tab1:
        st.markdown("#### Programa de Mejoramiento Térmico de Viviendas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo:**
            Reducir infecciones respiratorias agudas (IRA) en niños menores de 5 años en 30%
            
            **Población Objetivo:**
            - 80,000 familias en distritos con Tmin ≤ 1.5°C
            - 360,000 beneficiarios directos
            
            **Componentes:**
            - Aislamiento térmico integral (ISUR)
            - Cocinas mejoradas con distribución de calor
            - Capacitación en uso eficiente de combustibles
            """)
        
        with col2:
            st.markdown("""
            **Inversión:**
            - Costo por vivienda: S/ 15,000
            - Inversión total: S/ 1,200,000,000
            
            **Indicadores (KPI):**
            - Reducción 30% casos IRA registrados
            - Mejora temperatura interna +7°C
            - 95% satisfacción beneficiarios
            - ROI: 2.8:1 en 10 años
            """)
    
    with tab2:
        st.markdown("#### Programa de Protección Agrícola Anti-Helada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo:**
            Reducir pérdidas agrícolas por heladas en 25%
            
            **Beneficiarios:**
            - 40,000 productores en zonas de riesgo
            - 200,000 hectáreas protegidas
            
            **Tecnologías:**
            - Mantas térmicas agrícolas
            - Sistemas de riego anti-helada
            - Calendarios climatológicos
            """)
        
        with col2:
            st.markdown("""
            **Inversión:**
            - Costo por kit: S/ 500
            - Inversión total: S/ 10,000,000
            
            **Impactos:**
            - Incremento rendimiento: 25%
            - Reducción pérdidas: 25%
            - Beneficio-Costo: 4.5:1
            """)
    
    with tab3:
        st.markdown("#### Programa de Protección de Camélidos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo:**
            Reducir mortalidad de camélidos por friaje en 40%
            
            **Beneficiarios:**
            - 25,000 familias ganaderas
            - 1,250,000 animales protegidos
            
            **Infraestructura:**
            - Refugios térmicos (50 animales)
            - Suplementación nutricional
            - Capacitación en manejo
            """)
        
        with col2:
            st.markdown("""
            **Inversión:**
            - Costo por refugio: S/ 8,000
            - Inversión total: S/ 200,000,000
            
            **Impactos:**
            - Reducción mortalidad: 40%
            - Incremento producción fibra: 20%
            - Estabilización ingresos: 85%
            """)

def main():
    """Función principal"""
    
    st.markdown('<div class="main-header">Sistema de Análisis Geoespacial - Temperatura Mínima Perú</div>', unsafe_allow_html=True)
    
    # Cargar datos
    datos, metricas = load_data()
    
    if datos is None:
        st.error("Error crítico: No se pudieron cargar los datasets requeridos")
        return
    
    # Sidebar
    st.sidebar.markdown('<div style="text-align: center;"><h2>🧭 Centro de Control</h2></div>', unsafe_allow_html=True)
    
    opciones_menu = [
        "📊 Resumen Ejecutivo",
        "📈 Estadísticas Zonales", 
        "📉 Análisis Visual Avanzado",
        "🗺️ Cartografía Temática",
        "💾 Centro de Descarga",
        "🏛️ Marco de Políticas Públicas"
    ]
    
    seleccion = st.sidebar.selectbox("Seleccionar módulo:", opciones_menu)
    
    # Información del sistema
    st.sidebar.markdown("### 📊 Métricas del Sistema")
    st.sidebar.metric("Distritos Analizados", f"{len(datos):,}")
    st.sidebar.metric("Cobertura Nacional", "100%")
    st.sidebar.metric("Resolución Espacial", "~1 km")
    
    # Enrutamiento
    if seleccion == "📊 Resumen Ejecutivo":
        show_executive_summary(metricas, datos)
    elif seleccion == "📈 Estadísticas Zonales":
        show_zonal_statistics(datos)
    elif seleccion == "📉 Análisis Visual Avanzado":
        show_advanced_visualizations(datos)
    elif seleccion == "🗺️ Cartografía Temática":
        show_static_map()
    elif seleccion == "💾 Centro de Descarga":
        show_data_download(datos)
    elif seleccion == "🏛️ Marco de Políticas Públicas":
        show_public_policies()

if __name__ == "__main__":
    main()