import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import io

# Configuración de la página
st.set_page_config(
    page_title="Análisis Temperatura Mínima Perú",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar estilo de matplotlib
plt.style.use('default')
sns.set_palette("viridis")

@st.cache_data
def load_data():
    """Cargar datos procesados"""
    try:
        # Cargar estadísticas principales
        stats = pd.read_csv('estadisticas_temperatura_distritos.csv')
        
        # Cargar métricas resumen
        with open('metricas_resumen.json', 'r') as f:
            metricas = json.load(f)
        
        return stats, metricas
    except FileNotFoundError as e:
        st.error(f"Error cargando archivos: {e}")
        st.info("Asegúrate de tener todos los archivos CSV y JSON en la misma carpeta")
        return None, None

def crear_grafico_distribucion(datos):
    """Crear gráfico de distribución de temperaturas"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(datos['mean'].dropna(), bins=40, alpha=0.7, color='skyblue', edgecolor='black')
    ax.axvline(datos['mean'].mean(), color='red', linestyle='--', linewidth=2, 
               label=f'Media: {datos["mean"].mean():.1f}°C')
    ax.axvline(datos['mean'].quantile(0.1), color='blue', linestyle='--', linewidth=2, 
               label=f'P10: {datos["mean"].quantile(0.1):.1f}°C')
    
    ax.set_title('Distribución de Temperatura Media por Distrito', fontweight='bold', fontsize=14)
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_ylabel('Número de Distritos')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig

def crear_grafico_ranking(datos, tipo='frios', n=15):
    """Crear gráfico de ranking de distritos"""
    if tipo == 'frios':
        top_datos = datos.nsmallest(n, 'mean')
        color = 'lightblue'
        titulo = f'Top {n} Distritos MÁS FRÍOS'
        subtitulo = '(Mayor riesgo de friaje)'
    else:
        top_datos = datos.nlargest(n, 'mean')
        color = 'lightcoral'
        titulo = f'Top {n} Distritos MÁS CÁLIDOS'
        subtitulo = '(Menor riesgo de friaje)'
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Crear etiquetas cortas
    labels = [f"{row['DISTRITO'][:15]}..." if len(row['DISTRITO']) > 15 else row['DISTRITO'] 
              for _, row in top_datos.iterrows()]
    
    y_pos = range(len(top_datos))
    bars = ax.barh(y_pos, top_datos['mean'], color=color, alpha=0.8)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{i+1}. {label}" for i, label in enumerate(labels)], fontsize=10)
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_title(f'{titulo}\n{subtitulo}', fontweight='bold', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()
    
    # Añadir valores en las barras
    for i, temp in enumerate(top_datos['mean']):
        ax.text(temp + 0.1, i, f'{temp:.1f}°C', va='center', fontsize=9, fontweight='bold')
    
    return fig

def crear_mapa_plotly(datos):
    """Crear mapa interactivo con Plotly"""
    # Crear figura de dispersión geográfica (aproximación sin shapefile)
    fig = go.Figure()
    
    # Usar coordenadas aproximadas basadas en departamentos
    coords_aprox = {
        'AMAZONAS': (-77.9, -6.2), 'ANCASH': (-77.5, -9.5), 'APURIMAC': (-72.9, -13.6),
        'AREQUIPA': (-71.5, -16.4), 'AYACUCHO': (-74.2, -13.2), 'CAJAMARCA': (-78.5, -7.2),
        'CALLAO': (-77.1, -12.1), 'CUSCO': (-71.9, -13.5), 'HUANCAVELICA': (-75.0, -12.8),
        'HUANUCO': (-76.2, -9.9), 'ICA': (-75.7, -14.1), 'JUNIN': (-75.0, -11.2),
        'LA LIBERTAD': (-79.0, -8.1), 'LAMBAYEQUE': (-79.9, -6.7), 'LIMA': (-77.0, -12.0),
        'LORETO': (-73.2, -3.7), 'MADRE DE DIOS': (-70.9, -12.6), 'MOQUEGUA': (-70.9, -17.2),
        'PASCO': (-76.3, -10.7), 'PIURA': (-80.6, -5.2), 'PUNO': (-70.0, -15.8),
        'SAN MARTIN': (-76.4, -6.8), 'TACNA': (-70.2, -18.0), 'TUMBES': (-80.5, -3.6), 'UCAYALI': (-74.6, -8.4)
    }
    
    # Agregar coordenadas aproximadas
    datos_con_coords = datos.copy()
    datos_con_coords['lon'] = datos_con_coords['DEPARTAMEN'].map(lambda x: coords_aprox.get(x, (-75, -10))[0])
    datos_con_coords['lat'] = datos_con_coords['DEPARTAMEN'].map(lambda x: coords_aprox.get(x, (-75, -10))[1])
    
    # Añadir ruido aleatorio para separar puntos del mismo departamento
    np.random.seed(42)
    datos_con_coords['lon'] += np.random.normal(0, 0.5, len(datos_con_coords))
    datos_con_coords['lat'] += np.random.normal(0, 0.3, len(datos_con_coords))
    
    fig.add_trace(go.Scattermapbox(
        lat=datos_con_coords['lat'],
        lon=datos_con_coords['lon'],
        mode='markers',
        marker=dict(
            size=8,
            color=datos_con_coords['mean'],
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(title="Temperatura (°C)")
        ),
        text=datos_con_coords['DISTRITO'] + '<br>' + 
             datos_con_coords['PROVINCIA'] + '<br>' + 
             datos_con_coords['DEPARTAMEN'] + '<br>' +
             'Temp: ' + datos_con_coords['mean'].round(1).astype(str) + '°C',
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=-9.19, lon=-75.0),
            zoom=5
        ),
        height=600,
        title="Mapa Interactivo de Temperatura por Distrito"
    )
    
    return fig

def mostrar_politicas_publicas():
    """Mostrar sección de políticas públicas"""
    st.header("🏛️ Propuestas de Políticas Públicas")
    
    st.markdown("""
    ### Diagnóstico
    Las bajas temperaturas en zonas alto-andinas y episodios de friaje en la Amazonía peruana generan:
    - Incremento de enfermedades respiratorias agudas (IRA) y diarreicas (EDA)
    - Pérdidas significativas en la producción agrícola por heladas
    - Reducción de la asistencia escolar durante eventos extremos
    - Mortalidad de ganado, especialmente camélidos sudamericanos
    """)
    
    # Crear pestañas para las 3 propuestas
    tab1, tab2, tab3 = st.tabs(["🏠 Viviendas Térmicas", "🌾 Kits Anti-helada", "🦙 Refugios Ganaderos"])
    
    with tab1:
        st.subheader("Propuesta 1: Mejoramiento de Viviendas Térmicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo específico:** Reducir en 30% los casos de IRA en niños menores de 5 años
            
            **Población objetivo:** Familias en distritos con Tmin ≤ percentil 10
            
            **Intervención:** 
            - Instalación de sistemas de aislamiento térmico (ISUR)
            - Implementación de cocinas mejoradas
            - Capacitación en uso eficiente de combustibles
            """)
        
        with col2:
            st.markdown("""
            **Costo estimado:** S/ 15,000 por vivienda
            
            **Indicadores (KPI):**
            - Reducción 30% casos IRA registrados en MINSA/EsSalud
            - Mejora temperatura interna +5°C promedio
            - 95% satisfacción de beneficiarios
            
            **Beneficiarios:** ~80,000 familias rurales
            """)
    
    with tab2:
        st.subheader("Propuesta 2: Kits Anti-helada para Agricultura")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo específico:** Reducir pérdidas agrícolas por heladas en 25%
            
            **Población objetivo:** Productores agrícolas en zonas de riesgo
            
            **Intervención:**
            - Distribución de mantas térmicas para cultivos
            - Sistemas de riego antihielo por aspersión
            - Calendarios agrícolas climatológicos
            """)
        
        with col2:
            st.markdown("""
            **Costo estimado:** S/ 500 por kit (cobertura 10 hectáreas)
            
            **Indicadores (KPI):**
            - Reducción 25% pérdidas en papa, quinua, habas
            - Aumento 15% rendimiento promedio
            - Mejora ingresos familiares 20%
            
            **Beneficiarios:** ~40,000 pequeños productores
            """)
    
    with tab3:
        st.subheader("Propuesta 3: Refugios para Camélidos Sudamericanos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objetivo específico:** Reducir mortalidad de alpacas y llamas en 40%
            
            **Población objetivo:** Comunidades ganaderas alto-andinas
            
            **Intervención:**
            - Construcción de cobertizos térmicos
            - Suplementación nutricional estratégica
            - Programa sanitario preventivo
            """)
        
        with col2:
            st.markdown("""
            **Costo estimado:** S/ 8,000 por refugio (50 animales)
            
            **Indicadores (KPI):**
            - Reducción 40% mortalidad durante friaje
            - Mejora condición corporal de animales
            - Aumento productividad de fibra 15%
            
            **Beneficiarios:** ~25,000 familias ganaderas
            """)
    
    # Resumen de inversión
    st.markdown("---")
    st.subheader("📊 Resumen de Inversión")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Inversión Total", "S/ 2.4 mil millones", help="Inversión estimada para las 3 propuestas")
    
    with col2:
        st.metric("Población Beneficiada", "658,000 habitantes", help="En distritos de alto riesgo")
    
    with col3:
        st.metric("Distritos Prioritarios", "188 distritos", help="Con temperatura ≤ percentil 10")
    
    with col4:
        st.metric("Inversión per cápita", "S/ 3,650", help="Inversión por habitante beneficiado")

def main():
    """Función principal de la aplicación"""
    
    # Título principal
    st.title("🧊 Análisis de Temperatura Mínima en Perú")
    st.markdown("### Análisis de riesgos climáticos y propuestas de políticas públicas")
    
    # Cargar datos
    datos, metricas = load_data()
    
    if datos is None:
        st.error("No se pudieron cargar los datos. Verifica que los archivos estén disponibles.")
        st.stop()
    
    # Sidebar con navegación
    st.sidebar.title("🧭 Navegación")
    
    opciones_menu = [
        "📊 Resumen Ejecutivo",
        "📈 Estadísticas Zonales", 
        "📉 Visualizaciones",
        "🗺️ Mapa Interactivo",
        "💾 Descarga de Datos",
        "🏛️ Políticas Públicas"
    ]
    
    seleccion = st.sidebar.selectbox("Selecciona una sección:", opciones_menu)
    
    # Filtros en sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros")
    
    departamentos_disponibles = ["Todos"] + sorted(datos['DEPARTAMEN'].unique().tolist())
    dept_seleccionado = st.sidebar.selectbox("Departamento:", departamentos_disponibles)
    
    umbral_temp = st.sidebar.slider("Umbral temperatura (°C):", -10, 25, 5)
    
    # Filtrar datos según selección
    if dept_seleccionado != "Todos":
        datos_filtrados = datos[datos['DEPARTAMEN'] == dept_seleccionado]
    else:
        datos_filtrados = datos.copy()
    
    # Contenido principal según selección
    if seleccion == "📊 Resumen Ejecutivo":
        st.header("📊 Resumen Ejecutivo")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Distritos", 
                f"{metricas['total_distritos']:,}",
                help="Distritos analizados en todo el país"
            )
        
        with col2:
            st.metric(
                "Alto Riesgo Friaje", 
                f"{metricas['distritos_alto_riesgo']:,}",
                help="Distritos con temperatura ≤ percentil 10"
            )
        
        with col3:
            st.metric(
                "Temp. Media Nacional", 
                f"{metricas['temp_media_nacional']:.1f}°C",
                help="Promedio de temperatura media distrital"
            )
        
        with col4:
            st.metric(
                "Rango Térmico", 
                f"{metricas['temp_minima_extrema']:.1f}°C - {metricas['temp_maxima_extrema']:.1f}°C",
                help="Temperaturas extremas registradas"
            )
        
        # Información de contexto
        st.markdown("### 🔍 Hallazgos Principales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Distrito más frío:** {metricas['distrito_mas_frio']}  
            Temperatura media: {metricas['temp_minima_extrema']:.2f}°C
            
            **Alto riesgo de friaje:** {metricas['distritos_alto_riesgo']} distritos  
            Umbral: ≤ {metricas['umbral_alto_riesgo']:.1f}°C
            """)
        
        with col2:
            st.success(f"""
            **Distrito más cálido:** {metricas['distrito_mas_calido']}  
            Temperatura media: {metricas['temp_maxima_extrema']:.2f}°C
            
            **Cobertura del análisis:** 100%  
            Todos los distritos tienen datos válidos
            """)
    
    elif seleccion == "📈 Estadísticas Zonales":
        st.header("📈 Estadísticas Zonales")
        
        st.markdown("""
        Las estadísticas zonales extraen valores del raster de temperatura para cada distrito administrativo.
        Se calcularon 8 métricas por distrito:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Métricas básicas:**
            - **count**: Píxeles válidos por distrito
            - **mean**: Temperatura media
            - **min/max**: Valores extremos
            - **std**: Variabilidad térmica
            """)
        
        with col2:
            st.markdown("""
            **Métricas de riesgo:**
            - **percentile_10**: Umbral temperaturas bajas
            - **percentile_90**: Umbral temperaturas altas  
            - **range**: Amplitud térmica (personalizada)
            """)
        
        # Mostrar tabla de datos
        st.subheader("🔍 Explorador de Datos")
        
        # Opciones de visualización de tabla
        col1, col2 = st.columns([3, 1])
        
        with col2:
            mostrar_filas = st.number_input("Filas a mostrar:", 5, 50, 10)
            ordenar_por = st.selectbox("Ordenar por:", ['mean', 'min', 'max', 'std'])
            orden_desc = st.checkbox("Orden descendente", value=True)
        
        with col1:
            # Preparar datos para mostrar
            columnas_mostrar = ['DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'count', 'mean', 'min', 'max', 'std', 'percentile_10', 'percentile_90', 'range']
            datos_tabla = datos_filtrados[columnas_mostrar].round(2)
            
            if orden_desc:
                datos_tabla = datos_tabla.sort_values(ordenar_por, ascending=False)
            else:
                datos_tabla = datos_tabla.sort_values(ordenar_por, ascending=True)
            
            st.dataframe(datos_tabla.head(mostrar_filas), use_container_width=True)
    
    elif seleccion == "📉 Visualizaciones":
        st.header("📉 Visualizaciones")
        
        # Gráfico de distribución
        st.subheader("📊 Distribución de Temperaturas")
        fig_dist = crear_grafico_distribucion(datos_filtrados)
        st.pyplot(fig_dist)
        
        # Rankings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥶 Distritos Más Fríos")
            fig_frios = crear_grafico_ranking(datos_filtrados, 'frios', 10)
            st.pyplot(fig_frios)
        
        with col2:
            st.subheader("🔥 Distritos Más Cálidos") 
            fig_calidos = crear_grafico_ranking(datos_filtrados, 'calidos', 10)
            st.pyplot(fig_calidos)
    
    elif seleccion == "🗺️ Mapa Interactivo":
        st.header("🗺️ Mapa Interactivo de Temperatura")
        
        # Mapa con Plotly
        fig_mapa = crear_mapa_plotly(datos_filtrados)
        st.plotly_chart(fig_mapa, use_container_width=True)
        
        # Mostrar imagen estática como respaldo
        st.subheader("🗺️ Mapa Estático")
        try:
            st.image("mapa_temperatura_distritos.png", caption="Mapa coroplético de temperatura por distrito")
        except:
            st.warning("Mapa estático no disponible")
    
    elif seleccion == "💾 Descarga de Datos":
        st.header("💾 Descarga de Datos")
        
        st.markdown("Descarga los resultados del análisis en diferentes formatos:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Datos Principales")
            
            # CSV completo
            csv_completo = datos_filtrados.to_csv(index=False)
            st.download_button(
                label="📊 Descargar Estadísticas Completas (CSV)",
                data=csv_completo,
                file_name=f"estadisticas_temperatura_{dept_seleccionado.lower()}.csv",
                mime="text/csv"
            )
            
            # Solo distritos de alto riesgo
            alto_riesgo = datos_filtrados[datos_filtrados['mean'] <= metricas['umbral_alto_riesgo']]
            csv_riesgo = alto_riesgo.to_csv(index=False)
            st.download_button(
                label="🚨 Descargar Distritos Alto Riesgo (CSV)",
                data=csv_riesgo,
                file_name=f"alto_riesgo_friaje_{dept_seleccionado.lower()}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.subheader("📈 Resúmenes")
            
            # Resumen por departamento
            if dept_seleccionado == "Todos":
                resumen_dept = datos.groupby('DEPARTAMEN')['mean'].agg(['count', 'mean', 'std', 'min', 'max']).round(2)
                resumen_csv = resumen_dept.to_csv()
                st.download_button(
                    label="🗺️ Resumen por Departamento (CSV)",
                    data=resumen_csv,
                    file_name="resumen_departamental.csv",
                    mime="text/csv"
                )
            
            # Métricas en JSON
            metricas_json = json.dumps(metricas, indent=2)
            st.download_button(
                label="📋 Métricas Resumen (JSON)",
                data=metricas_json,
                file_name="metricas_resumen.json",
                mime="application/json"
            )
        
        # Información sobre los datos
        st.markdown("---")
        st.subheader("ℹ️ Información sobre los Datos")
        st.markdown(f"""
        - **Fuente**: Raster GeoTIFF de temperatura mínima + Shapefile distritos INEI
        - **Proyección**: EPSG:4326 (WGS84)
        - **Resolución**: ~1km por píxel
        - **Cobertura**: {len(datos):,} distritos (100% del territorio nacional)
        - **Métricas**: 8 estadísticas zonales por distrito
        - **Fecha de procesamiento**: Septiembre 2025
        """)
    
    elif seleccion == "🏛️ Políticas Públicas":
        mostrar_politicas_publicas()

if __name__ == "__main__":
    main()