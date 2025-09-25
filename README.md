# 🧊 Análisis de Temperatura Mínima en Perú - Riesgo de Friaje

## Descripción del Proyecto

Este proyecto desarrolla un sistema integral de análisis geoespacial para evaluar la distribución de temperaturas mínimas en territorio peruano, con el objetivo de identificar zonas de vulnerabilidad climática y proponer políticas públicas basadas en evidencia científica para la mitigación de riesgos asociados al friaje.

## 🎯 Objetivos

- **Principal:** Analizar la variabilidad espacial de temperaturas mínimas a nivel distrital para identificar zonas críticas de riesgo de friaje
- **Específicos:**
  - Calcular estadísticas zonales de temperatura por distrito administrativo
  - Identificar patrones geográficos de vulnerabilidad climática
  - Desarrollar visualizaciones científicas para comunicar hallazgos
  - Proponer marco de políticas públicas priorizadas con análisis costo-beneficio

## 🗂️ Estructura del Repositorio

```
Homework_3_TminPeru/
├── app/                                    # Aplicación Streamlit
│   ├── streamlit_app.py                   # Aplicación principal
│   ├── estadisticas_temperatura_distritos.csv  # Dataset procesado
│   ├── mapa_temperatura_distritos.png     # Mapa coroplético estático
│   ├── metricas_resumen.json             # Métricas agregadas
│   └── requirements.txt                   # Dependencias
├── notebooks/                             # Análisis exploratorio
│   └── 01_analisis_exploratorio.ipynb    # Notebook principal de análisis
├── data/                                  # Datos fuente
│   ├── DISTRITOS.shp                     # Límites distritales
│   ├── DISTRITOS.dbf                     # Atributos distritales
│   ├── DISTRITOS.shx                     # Índice espacial
│   ├── DISTRITOS.prj                     # Proyección
│   ├── DISTRITOS.cpg                     # Codificación
│   └── tmin_raster.tif                   # Raster de temperatura
├── README.md                             # Documentación principal
├── requirements.txt                      # Dependencias del proyecto
└── .gitignore                           # Archivos excluidos
```

## 📊 Metodología

### Datos Utilizados

**Fuentes Primarias:**
- **Raster de Temperatura:** GeoTIFF multibanda con datos de temperatura mínima
- **Límites Administrativos:** Shapefile de distritos del Perú (INEI)
- **Proyección:** EPSG:4326 (WGS84) para análisis, UTM para cálculos de área

**Características Técnicas:**
- Resolución espacial: ~1 km por píxel
- Cobertura: Nacional (1,873 distritos)
- Sistema de coordenadas: Compatible con estándares internacionales

### Procesamiento Geoespacial

1. **Preparación de Datos:**
   - Verificación de integridad de archivos geoespaciales
   - Validación de sistemas de coordenadas
   - Control de calidad de geometrías

2. **Estadísticas Zonales:**
   - Extracción de valores de temperatura por distrito
   - Cálculo de 8 métricas estadísticas por unidad administrativa
   - Validación de resultados mediante análisis de coherencia

3. **Análisis Espacial:**
   - Identificación de patrones geográficos
   - Clasificación de zonas de riesgo
   - Correlaciones espaciales y estadísticas

## 📈 Métricas Calculadas

| Métrica | Descripción | Unidad | Aplicación |
|---------|-------------|--------|------------|
| `count` | Píxeles válidos por distrito | píxeles | Validación de cobertura |
| `mean` | Temperatura media distrital | °C | Caracterización climática |
| `min` | Temperatura mínima registrada | °C | Identificación de extremos |
| `max` | Temperatura máxima registrada | °C | Rango térmico |
| `std` | Desviación estándar | °C | Variabilidad interna |
| `percentile_10` | Percentil 10 | °C | Umbral de riesgo alto |
| `percentile_90` | Percentil 90 | °C | Valores extremos superiores |
| `range` | Amplitud térmica (max-min) | °C | Gradiente térmico (métrica personalizada) |

## 🔬 Resultados Principales

### Hallazgos Estadísticos
- **Distritos analizados:** 1,873 (cobertura nacional completa)
- **Rango térmico nacional:** -5.21°C a 23.27°C
- **Temperatura media nacional:** 9.74°C
- **Distritos en alto riesgo:** 188 (percentil 10 más bajo)

### Patrones Geográficos Identificados
- **Zona crítica:** Altiplano puneño y sierra sur (Puno, Cusco, Arequipa)
- **Zona templada:** Región amazónica (Loreto, Ucayali, Madre de Dios)
- **Gradiente altitudinal:** Correlación negativa temperatura-altitud
- **Variabilidad estacional:** Mayor en zonas de transición climática

## 🏛️ Políticas Públicas Propuestas

### Marco de Intervención
Tres programas priorizados con enfoque en los 188 distritos de mayor vulnerabilidad:

#### 1. Programa Nacional de Mejoramiento Térmico de Viviendas Rurales
- **Objetivo:** Reducir IRA en niños <5 años en 30%
- **Beneficiarios:** 80,000 familias (360,000 personas)
- **Inversión:** S/ 1,200,000,000
- **Componentes:** Aislamiento térmico, cocinas mejoradas, capacitación

#### 2. Programa Nacional de Protección Agrícola Anti-Helada
- **Objetivo:** Reducir pérdidas agrícolas por heladas en 25%
- **Beneficiarios:** 40,000 productores (200,000 hectáreas)
- **Inversión:** S/ 10,000,000
- **Tecnologías:** Mantas térmicas, riego anti-helada, calendarios climáticos

#### 3. Programa Nacional de Protección de Camélidos Sudamericanos
- **Objetivo:** Reducir mortalidad de camélidos en 40%
- **Beneficiarios:** 25,000 familias ganaderas (1,250,000 animales)
- **Inversión:** S/ 200,000,000
- **Infraestructura:** Refugios térmicos, suplementación nutricional

**Inversión Total:** S/ 1,410,000,000 | **Beneficiarios:** 425,000 personas

## 🚀 Aplicación Streamlit

### Funcionalidades Implementadas

**Dashboard Interactivo con 6 módulos especializados:**

1. **📊 Resumen Ejecutivo:** Métricas principales y hallazgos clave
2. **📈 Estadísticas Zonales:** Explorador interactivo con filtros avanzados
3. **📉 Análisis Visual:** Visualizaciones científicas interactivas
4. **🗺️ Cartografía Temática:** Mapa coroplético estático de alta resolución
5. **💾 Centro de Descarga:** Datasets en múltiples formatos
6. **🏛️ Políticas Públicas:** Propuestas detalladas con análisis económico

### Requisitos Técnicos Cumplidos
- ✅ **Aplicación pública** en Streamlit Community Cloud
- ✅ **Raster integrado** (datos pre-procesados)
- ✅ **Estadísticas zonales** (8 métricas > 6 requeridas)
- ✅ **Visualizaciones:** Distribución + Ranking + Mapa estático
- ✅ **Descarga CSV** con múltiples formatos
- ✅ **Políticas públicas** con diagnóstico + 3 medidas priorizadas

## 🛠️ Instalación y Uso

### Requisitos del Sistema
- Python 3.10+
- Bibliotecas geoespaciales (geopandas, rasterio, rasterstats)
- Entorno compatible con Streamlit

### Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/bmperaltillap-wq/Homework_3_TminPeru.git
cd Homework_3_TminPeru

# Crear ambiente virtual
python -m venv env

# Activar ambiente (Windows)
env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app/streamlit_app.py
```

### Acceso Online
- **Aplicación desplegada:** [Streamlit Community Cloud](https://homework3-temperatura-peru.streamlit.app)
- **Repositorio:** [GitHub](https://github.com/bmperaltillap-wq/Homework_3_TminPeru)

## 📋 Dependencias Principales

```txt
streamlit>=1.28.0          # Framework de aplicación web
pandas>=1.5.0              # Manipulación de datos
geopandas>=0.13.0          # Análisis geoespacial
rasterio>=1.3.0            # Procesamiento de raster
rasterstats>=0.19.0        # Estadísticas zonales
matplotlib>=3.6.0          # Visualización estática
plotly>=5.15.0             # Visualización interactiva
numpy>=1.24.0              # Computación numérica
```

## 🔬 Metodología Científica

### Estándares Aplicados
- **ISO 19115:** Metadatos geoespaciales estándar
- **EPSG:4326:** Sistema de coordenadas de referencia
- **UTM Zones 17-19S:** Proyecciones para cálculos de área
- **Estadísticas robustas:** Validación mediante percentiles y outliers

### Validación de Resultados
- **Coherencia espacial:** Verificación de patrones geográficos esperados
- **Consistencia estadística:** Análisis de distribuciones y correlaciones
- **Validación territorial:** Comparación con área oficial del Perú

## 📊 Visualizaciones Disponibles

### Tipos de Gráficos Implementados
1. **Distribución estadística:** Histogramas y curvas de densidad
2. **Rankings territoriales:** Barras horizontales con valores extremos
3. **Correlaciones:** Scatter plots con codificación cromática
4. **Mapas temáticos:** Coropletas con simbología científica
5. **Análisis temporal:** Tendencias y patrones estacionales

## 🎯 Casos de Uso

### Usuarios Objetivo
- **Decisores de política pública:** Identificación de zonas prioritarias
- **Investigadores climáticos:** Análisis de variabilidad térmica
- **Planificadores territoriales:** Evaluación de riesgo espacial
- **Organizaciones de desarrollo:** Focalización de intervenciones

### Aplicaciones Prácticas
- Diseño de programas de adaptación climática
- Asignación de recursos de emergencia
- Planificación de infraestructura social
- Evaluación de impacto de políticas

## 🤝 Contribuciones

### Desarrollo del Proyecto
Este proyecto fue desarrollado como parte del curso **Data Science Python** - Homework 3, implementando metodologías avanzadas de análisis geoespacial y visualización de datos.

### Reconocimientos
- **Datos fuente:** INEI, repositorio del curso
- **Metodología:** Basada en estándares internacionales de análisis espacial
- **Framework técnico:** Python ecosystem para ciencia de datos

---

## 📄 Licencia

Este proyecto se desarrolla con fines académicos y de investigación. Los datos utilizados mantienen sus licencias originales respectivas.

---

**Última actualización:** Septiembre 2025  
**Versión:** 1.0.0  
**Estado:** Producción - Desplegado
