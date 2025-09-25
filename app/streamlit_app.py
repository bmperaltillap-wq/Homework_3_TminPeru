
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
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Análisis Geoespacial de Temperatura Mínima en Perú",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
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
    """Carga datos con manejo robusto de errores y validación"""
    try:
        stats = pd.read_csv('estadisticas_temperatura_distritos.csv')
        with open('metricas_resumen.json', 'r') as f:
            metricas = json.load(f)
        
        # Validación de datos
        if stats.empty:
            st.error("El archivo de estadísticas está vacío")
            return None, None
            
        required_columns = ['DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'mean', 'min', 'max', 'std']
        missing_cols = [col for col in required_columns if col not in stats.columns]
        if missing_cols:
            st.error(f"Faltan columnas requeridas: {missing_cols}")
            return None, None
            
        return stats, metricas
    except FileNotFoundError as e:
        st.error(f"Archivo no encontrado: {e}")
        return None, None
    except Exception as e:
        st.error(f"Error inesperado cargando datos: {e}")
        return None, None

def create_advanced_distribution_plot(datos):
    """Crea visualizaciones avanzadas de distribución"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distribución de Temperatura Media', 'Box Plot por Regiones', 
                       'Densidad por Departamentos Top', 'Correlación Temp vs Variabilidad'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Histograma con curva de densidad
    fig.add_trace(
        go.Histogram(x=datos['mean'], nbinsx=40, name='Distribución', 
                    marker_color='lightblue', opacity=0.7),
        row=1, col=1
    )
    
    # Box plot por regiones (aproximación por departamentos)
    top_depts = datos.groupby('DEPARTAMEN')['mean'].count().nlargest(8).index
    dept_data = datos[datos['DEPARTAMEN'].isin(top_depts)]
    
    for dept in top_depts:
        dept_temps = dept_data[dept_data['DEPARTAMEN'] == dept]['mean']
        fig.add_trace(
            go.Box(y=dept_temps, name=dept[:8], showlegend=False),
            row=1, col=2
        )
    
    # Curvas de densidad para departamentos principales
    colors = px.colors.qualitative.Set3
    for i, dept in enumerate(top_depts[:5]):
        dept_temps = datos[datos['DEPARTAMEN'] == dept]['mean']
        if len(dept_temps) > 5:  # Solo si hay suficientes datos
            fig.add_trace(
                go.Histogram(x=dept_temps, histnorm='probability density', 
                           name=dept, opacity=0.6, 
                           marker_color=colors[i % len(colors)]),
                row=2, col=1
            )
    
    # Scatter plot temperatura vs variabilidad
    fig.add_trace(
        go.Scatter(x=datos['mean'], y=datos['std'], mode='markers',
                  marker=dict(size=5, opacity=0.6, color=datos['mean'], 
                            colorscale='RdYlBu_r', showscale=True,
                            colorbar=dict(title="Temp (°C)", x=1.02)),
                  name='Distritos', showlegend=False),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, 
                     title_text="Análisis Estadístico Avanzado de Temperatura")
    
    return fig

def create_ranking_visualization(datos):
    """Crea visualización avanzada de rankings"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Top 15 Distritos Más Fríos', 'Top 15 Distritos Más Cálidos',
                       'Distribución por Departamento', 'Análisis de Riesgo por Región'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Top 15 más fríos
    frios = datos.nsmallest(15, 'mean')
    fig.add_trace(
        go.Bar(x=frios['mean'], y=[f"{row['DISTRITO'][:15]}..." for _, row in frios.iterrows()],
               orientation='h', name='Más Fríos', marker_color='lightblue',
               text=[f"{temp:.1f}°C" for temp in frios['mean']], textposition='outside'),
        row=1, col=1
    )
    
    # Top 15 más cálidos
    calidos = datos.nlargest(15, 'mean')
    fig.add_trace(
        go.Bar(x=calidos['mean'], y=[f"{row['DISTRITO'][:15]}..." for _, row in calidos.iterrows()],
               orientation='h', name='Más Cálidos', marker_color='lightcoral',
               text=[f"{temp:.1f}°C" for temp in calidos['mean']], textposition='outside'),
        row=1, col=2
    )
    
    # Distribución por departamento
    dept_stats = datos.groupby('DEPARTAMEN')['mean'].agg(['count', 'mean']).sort_values('mean')
    fig.add_trace(
        go.Bar(x=dept_stats.index, y=dept_stats['count'], name='Cantidad Distritos',
               marker_color='lightgreen'),
        row=2, col=1
    )
    
    # Análisis de riesgo
    umbral_riesgo = datos['mean'].quantile(0.1)
    riesgo_por_dept = datos[datos['mean'] <= umbral_riesgo].groupby('DEPARTAMEN').size().sort_values(ascending=False)
    
    fig.add_trace(
        go.Bar(x=riesgo_por_dept.index[:10], y=riesgo_por_dept.values[:10], 
               name='Distritos Alto Riesgo', marker_color='red'),
        row=2, col=2
    )
    
    fig.update_layout(height=900, showlegend=False,
                     title_text="Análisis de Rankings y Distribución Territorial")
    
    return fig

def show_executive_summary(metricas, datos):
    """Resumen ejecutivo mejorado con análisis detallado"""
    st.markdown('<div class="main-header">Resumen Ejecutivo - Análisis de Temperatura Mínima</div>', unsafe_allow_html=True)
    
    # Métricas principales con diseño mejorado
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
            help="Distritos con temperatura ≤ percentil 10 (mayor vulnerabilidad al friaje)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Temperatura Media Nacional", 
            value=f"{metricas['temp_media_nacional']:.1f}°C",
            delta=f"Rango: {metricas['temp_minima_extrema']:.1f}°C - {metricas['temp_maxima_extrema']:.1f}°C",
            help="Promedio ponderado de temperatura media distrital"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        variabilidad_promedio = datos['std'].mean()
        st.metric(
            label="Variabilidad Térmica", 
            value=f"{variabilidad_promedio:.1f}°C",
            help="Desviación estándar promedio - indica heterogeneidad climática"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análisis contextual detallado
    st.markdown('<div class="section-header">Contexto Geográfico y Climático</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h4>Interpretación de Resultados</h4>
        <p><strong>Distribución Espacial:</strong> El análisis revela una marcada heterogeneidad térmica 
        que refleja la compleja geografía peruana. Las temperaturas mínimas están fuertemente correlacionadas 
        con la altitud, evidenciando el gradiente térmico altitudinal característico de los Andes tropicales.</p>
        
        <p><strong>Patrón Latitudinal:</strong> Se observa una distribución que sigue patrones geográficos 
        esperados: temperaturas más bajas en zonas alto-andinas del sur (Puno, Cusco, Arequipa) y 
        temperaturas más elevadas en regiones amazónicas del norte y oriente.</p>
        
        <p><strong>Implicaciones Socioeconómicas:</strong> Los {distritos_riesgo:,} distritos identificados en alto riesgo 
        concentran poblaciones rurales vulnerables, principalmente comunidades campesinas y ganaderas 
        que dependen de actividades sensibles al clima.</p>
        </div>
        """.format(distritos_riesgo=metricas['distritos_alto_riesgo']), unsafe_allow_html=True)
    
    with col2:
        # Gráfico de distribución rápida
        fig_mini = px.histogram(datos, x='mean', nbins=30, 
                               title='Distribución de Temperatura Media')
        fig_mini.add_vline(x=metricas['umbral_alto_riesgo'], line_dash="dash", 
                          line_color="red", annotation_text="Umbral Alto Riesgo")
        fig_mini.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_mini, use_container_width=True)
    
    # Hallazgos clave
    st.markdown('<div class="section-header">Hallazgos Principales</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="warning-box">
        <h4>Zona Crítica Identificada</h4>
        <p><strong>Distrito más frío:</strong><br>{metricas['distrito_mas_frio']}</p>
        <p><strong>Temperatura media:</strong> {metricas['temp_minima_extrema']:.2f}°C</p>
        <p>Esta zona requiere intervención prioritaria para mitigar impactos del friaje.</p>
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
        <p>Concentra el mayor número de distritos que requieren atención específica.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="success-box">
        <h4>Cobertura del Análisis</h4>
        <p><strong>Metodología:</strong> Estadísticas zonales</p>
        <p><strong>Precisión:</strong> Resolución ~1km</p>
        <p><strong>Validez:</strong> Datos 2024 actualizados</p>
        <p>Análisis geoespacial robusto con cobertura nacional completa.</p>
        </div>
        """, unsafe_allow_html=True)

def show_zonal_statistics(datos):
    """Sección de estadísticas zonales con análisis técnico detallado"""
    st.markdown('<div class="main-header">Estadísticas Zonales - Análisis Técnico</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Metodología de Análisis Geoespacial
    
    El análisis de estadísticas zonales constituye la técnica fundamental para extraer información cuantitativa 
    de datos raster (temperatura) utilizando geometrías vectoriales (límites distritales). Esta metodología 
    permite transformar datos continuos espaciales en métricas discretas por unidad administrativa.
    """)
    
    # Explicación técnica detallada
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        #### Proceso Técnico Implementado
        
        **1. Preparación de Datos:**
        - Raster de temperatura mínima (GeoTIFF multibanda, EPSG:4326)
        - Shapefile de límites distritales (1,873 unidades administrativas)
        - Verificación de compatibilidad de sistemas de coordenadas
        
        **2. Cálculo de Estadísticas Zonales:**
        - Superposición espacial entre geometrías y píxeles del raster
        - Extracción de valores de temperatura para cada distrito
        - Cálculo de métricas estadísticas usando biblioteca `rasterstats`
        
        **3. Métricas Calculadas:**
        """)
        
        # Tabla de métricas con explicaciones
        metricas_df = pd.DataFrame({
            'Métrica': ['count', 'mean', 'min', 'max', 'std', 'percentile_10', 'percentile_90', 'range'],
            'Descripción': [
                'Número de píxeles válidos dentro de cada distrito',
                'Temperatura media ponderada por área distrital',
                'Valor mínimo de temperatura registrado en el distrito',
                'Valor máximo de temperatura registrado en el distrito',
                'Desviación estándar - medida de variabilidad térmica interna',
                'Percentil 10 - umbral de temperaturas extremas bajas',
                'Percentil 90 - umbral de temperaturas extremas altas',
                'Amplitud térmica (max - min) - métrica personalizada'
            ],
            'Unidad': ['píxeles', '°C', '°C', '°C', '°C', '°C', '°C', '°C'],
            'Aplicación': [
                'Validación de cobertura espacial',
                'Caracterización climática principal',
                'Identificación de microclimas fríos',
                'Detección de heterogeneidad térmica',
                'Análisis de variabilidad espacial',
                'Definición de zonas de alto riesgo',
                'Identificación de valores atípicos',
                'Evaluación de gradientes térmicos'
            ]
        })
        
        st.dataframe(metricas_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Estadísticas de calidad de datos
        st.markdown("#### Validación de Calidad")
        
        total_distritos = len(datos)
        distritos_datos_validos = len(datos.dropna(subset=['mean']))
        cobertura = (distritos_datos_validos / total_distritos) * 100
        
        st.metric("Cobertura Espacial", f"{cobertura:.1f}%", 
                 help="Porcentaje de distritos con datos válidos")
        
        pixeles_promedio = datos['count'].mean()
        st.metric("Píxeles/Distrito", f"{pixeles_promedio:.0f}", 
                 help="Resolución espacial promedio por unidad administrativa")
        
        # Distribución de píxeles
        fig_pixeles = px.histogram(datos, x='count', nbins=30, 
                                  title='Distribución de Cobertura de Píxeles')
        fig_pixeles.update_layout(height=250)
        st.plotly_chart(fig_pixeles, use_container_width=True)

def show_advanced_visualizations(datos):
    """Visualizaciones avanzadas con análisis profundo"""
    st.markdown('<div class="main-header">Análisis Visual Avanzado</div>', unsafe_allow_html=True)
    
    # Gráfico avanzado de distribución
    fig_dist = create_advanced_distribution_plot(datos)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Visualización avanzada de rankings
    fig_rank = create_ranking_visualization(datos)
    st.plotly_chart(fig_rank, use_container_width=True)

def show_static_map():
    """Sección del mapa estático con contexto profesional"""
    st.markdown('<div class="main-header">Cartografía Temática - Temperatura Mínima</div>', unsafe_allow_html=True)
    
    try:
        st.image("mapa_temperatura_distritos.png", 
                caption="Distribución espacial de temperatura mínima por distrito - Análisis geoespacial 2024",
                use_column_width=True)
    except:
        st.error("Mapa estático no disponible. Verificar archivo 'mapa_temperatura_distritos.png'")

def show_data_download(datos):
    """Sección de descarga de datos con opciones avanzadas"""
    st.markdown('<div class="main-header">Centro de Descarga de Datos</div>', unsafe_allow_html=True)
    
    # Dataset completo
    csv_completo = datos.to_csv(index=False)
    st.download_button(
        label="Descargar Dataset Completo - Estadísticas Zonales",
        data=csv_completo,
        file_name="temperatura_minima_peru_completo.csv",
        mime="text/csv",
        help="Incluye todas las métricas calculadas para 1,873 distritos"
    )

def show_public_policies():
    """Sección de políticas públicas con análisis técnico-económico detallado"""
    st.markdown('<div class="main-header">Marco de Políticas Públicas Basadas en Evidencia</div>', unsafe_allow_html=True)
    
    # Crear pestañas para cada propuesta
    tab1, tab2, tab3 = st.tabs([
        "Propuesta 1: Viviendas Térmicas", 
        "Propuesta 2: Protección Agrícola",
        "Propuesta 3: Protección Ganadera"
    ])
    
    with tab1:
        st.markdown("#### Programa Nacional de Mejoramiento Térmico de Viviendas Rurales")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("""
            **Objetivo Específico:**
            Reducir la incidencia de infecciones respiratorias agudas (IRA) en niños menores de 5 años en un 30% 
            mediante el mejoramiento integral de las condiciones térmicas habitacionales.
            
            **Población Objetivo:**
            - Familias residentes en los 188 distritos con Tmin ≤ 1.5°C
            - Hogares en condición de pobreza y pobreza extrema
            - Presencia de niños menores de 5 años y adultos mayores
            - Estimación poblacional: 80,000 familias (360,000 beneficiarios)
            
            **Componentes de Intervención:**
            1. **Aislamiento Térmico Integral:** Paneles aislantes, mejoramiento de cobertura
            2. **Sistema de Calefacción Eficiente:** Cocinas mejoradas, sistemas de ventilación
            3. **Capacitación:** Educación en uso eficiente de combustibles
            """)
        
        with col2:
            st.markdown("""
            **Análisis Costo-Beneficio:**
            - Materiales: S/ 8,500
            - Mano de obra: S/ 4,200
            - Capacitación: S/ 800
            - Supervisión: S/ 1,500
            - **Total por vivienda: S/ 15,000**
            
            **Inversión Total:** S/ 1,200,000,000
            
            **Indicadores (KPI):**
            - Reducción 30% casos IRA en menores de 5 años
            - Mejora temperatura interna promedio: +7°C
            - 95% satisfacción beneficiarios
            """)
    
    with tab2:
        st.markdown("#### Programa Nacional de Protección Agrícola Anti-Helada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo Específico:**
            Reducir las pérdidas económicas por heladas agrícolas en 25% mediante tecnologías 
            de protección pasiva y activa.
            
            **Población Objetivo:**
            - 40,000 productores agrícolas en distritos prioritarios
            - Predios de 0.5 a 10 hectáreas
            - Cultivos de papa, quinua, habas, maíz amiláceo
            
            **Tecnologías:**
            - Mantas térmicas agrícolas
            - Sistemas de riego anti-helada
            - Calendarios climatológicos
            """)
        
        with col2:
            st.markdown("""
            **Inversión:**
            - Costo por kit (10 ha): S/ 500
            - Inversión total: S/ 10,000,000
            - Beneficio-Costo: 4.5:1
            
            **Impactos:**
            - Incremento rendimiento: 25%
            - Reducción pérdidas: 25%
            - Mejora calidad: 15%
            """)
    
    with tab3:
        st.markdown("#### Programa Nacional de Protección de Camélidos Sudamericanos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo Específico:**
            Reducir la mortalidad de camélidos por eventos de friaje en 40% mediante 
            refugios térmicos y manejo ganadero adaptativo.
            
            **Población Objetivo:**
            - 25,000 familias ganaderas en altitudes > 3,800 msnm
            - Hatos de 20-200 camélidos
            - 1,250,000 animales protegidos
            
            **Componentes:**
            - Cobertizos térmicos (50 animales)
            - Suplementación nutricional
            - Capacitación en manejo sanitario
            """)
        
        with col2:
            st.markdown("""
            **Inversión:**
            - Costo por refugio: S/ 8,000
            - Inversión total: S/ 200,000,000
            - Periodo recuperación: 2.5 años
            
            **Impactos:**
            - Reducción mortalidad: 40%
            - Incremento producción fibra: 20%
            - Estabilización ingresos: 85%
            """)

def main():
    """Función principal de la aplicación"""
    
    st.markdown('<div class="main-header">Sistema de Análisis Geoespacial - Temperatura Mínima Perú</div>', unsafe_allow_html=True)
    
    # Cargar datos con validación
    datos, metricas = load_data()
    
    if datos is None:
        st.error("Error crítico: No se pudieron cargar los datasets requeridos")
        return
    
    # Sidebar con navegación avanzada
    st.sidebar.markdown('<div style="text-align: center; padding: 1rem;"><h2>Centro de Control</h2></div>', unsafe_allow_html=True)
    
    opciones_menu = [
        "Resumen Ejecutivo",
        "Estadísticas Zonales", 
        "Análisis Visual Avanzado",
        "Cartografía Temática",
        "Centro de Descarga",
        "Marco de Políticas Públicas"
    ]
    
    seleccion = st.sidebar.selectbox("Seleccionar módulo de análisis:", opciones_menu)
    
    # Filtros globales
    departamentos = ['Todos'] + sorted(datos['DEPARTAMEN'].unique().tolist())
    dept_filtro = st.sidebar.selectbox("Filtro Departamental:", departamentos)
    
    # Aplicar filtros
    if dept_filtro != "Todos":
        datos_filtrados = datos[datos['DEPARTAMEN'] == dept_filtro]
    else:
        datos_filtrados = datos
    
    # Enrutamiento a módulos
    if seleccion == "Resumen Ejecutivo":
        show_executive_summary(metricas, datos_filtrados)
    elif seleccion == "Estadísticas Zonales":
        show_zonal_statistics(datos_filtrados)
    elif seleccion == "Análisis Visual Avanzado":
        show_advanced_visualizations(datos_filtrados)
    elif seleccion == "Cartografía Temática":
        show_static_map()
    elif seleccion == "Centro de Descarga":
        show_data_download(datos_filtrados)
    elif seleccion == "Marco de Políticas Públicas":
        show_public_policies()

if __name__ == "__main__":
    main()
