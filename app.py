import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import seaborn as sns



st.set_page_config(
    page_title="Valenbisi × Calidad del Aire 2022",
    page_icon="logo.png",  # Icono cuadrado para la pestaña
    layout="wide"
)

# Cabecera con logo y título alineados
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image("favicon.png", width=600)  # Ajusta el tamaño según prefieras
# with col2:
#     st.markdown(
#         "<h1 style='margin-top: 30px; margin-bottom: 0;'>🚲 Valenbisi × Calidad del Aire 2022</h1>",
#         unsafe_allow_html=True
    #)

# Sidebar
st.sidebar.title('Navegación')
seccion = st.sidebar.radio('Ir a:', [
    'Resumen KPIs',
    'Análisis temporal',
    'Análisis espacial',
    'Correlaciones y modelos',
    'Comparativas'
])

# Cargar datos principales
city = pd.read_csv('data/city_bike_air_2022.csv')
city['is_weekend'] = city['dow'].apply(lambda x: 1 if x in [5, 6] else 0)

# --- Sección: Resumen KPIs ---
if seccion == 'Resumen KPIs':
    st.header('KPIs principales')
    st.info('Resumen de los principales indicadores de uso de Valenbisi y calidad del aire en València durante 2022. Observa la evolución temporal y los valores extremos.')
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('NO₂ medio', f"{city['NO2'].mean():.2f}", f"max: {city['NO2'].max():.1f}")
    col2.metric('PM10 medio', f"{city['PM10'].mean():.2f}", f"max: {city['PM10'].max():.1f}")
    col3.metric('PM2.5 medio', f"{city['PM2_5'].mean():.2f}", f"max: {city['PM2_5'].max():.1f}")
    col4.metric('O₃ medio', f"{city['O3'].mean():.2f}", f"max: {city['O3'].max():.1f}")
    col5.metric('Viajes bici/día', f"{city['bike_trips'].mean():.0f}", f"max: {city['bike_trips'].max():.0f}")
    st.subheader('Evolución temporal de NO₂ y viajes en bici')
    st.info('Serie temporal conjunta de la contaminación (NO₂) y el uso de la bici pública por hora, día y mes.')
    fig = px.line(city, y=['NO2', 'bike_trips'], labels={'value':'Valor','index':'Índice temporal','variable':'Variable'})
    st.plotly_chart(fig, use_container_width=True)

# --- Sección: Análisis temporal ---
elif seccion == 'Análisis temporal':
    st.header('Análisis temporal')
    st.info('Explora cómo varían la contaminación y el uso de la bici a lo largo del tiempo: por horas, días y meses.')
    st.subheader('Heatmap NO₂ por hora y día de la semana')
    heatmap_no2 = city.pivot_table(index='hour', columns='dow', values='NO2', aggfunc='mean')
    fig1 = px.imshow(heatmap_no2, labels=dict(x='Día de la semana (0=Lunes)', y='Hora', color='NO₂'))
    st.plotly_chart(fig1, use_container_width=True)
    st.subheader('Heatmap viajes bici por hora y día de la semana')
    heatmap_bike = city.pivot_table(index='hour', columns='dow', values='bike_trips', aggfunc='mean')
    fig2 = px.imshow(heatmap_bike, labels=dict(x='Día de la semana (0=Lunes)', y='Hora', color='Viajes bici'))
    st.plotly_chart(fig2, use_container_width=True)
    st.subheader('Boxplots NO₂ y viajes bici por mes')
    st.info('Distribución de los valores mensuales para identificar patrones y outliers.')
    fig3 = px.box(city, x='month', y='NO2', points='all', labels={'NO2':'NO₂','month':'Mes'})
    st.plotly_chart(fig3, use_container_width=True)
    fig4 = px.box(city, x='month', y='bike_trips', points='all', labels={'bike_trips':'Viajes bici','month':'Mes'})
    st.plotly_chart(fig4, use_container_width=True)

# --- Sección: Análisis espacial ---
elif seccion == 'Análisis espacial':
    st.header('Análisis espacial')
    st.info('Visualiza la distribución espacial de la contaminación y el uso de la bici en las estaciones de Valenbisi.')
    # Cargar datos de estaciones con lat/lon
    crosswalk = pd.read_csv('data/stations_crosswalk.csv')
    spatial = pd.read_csv('data/bike_air_spatial_hour_2022.csv')
    # Media por estación
    spatial_mean = spatial.groupby('codigo_estacion').agg({'NO2':'mean','prestamos_mean':'mean'}).reset_index()
    estaciones = pd.merge(crosswalk, spatial_mean, on='codigo_estacion', how='left')
    st.subheader('Mapa interactivo de estaciones')
    fig_map = px.scatter_mapbox(
        estaciones,
        lat='lat', lon='lon',
        color='NO2', size='prestamos_mean',
        hover_name='codigo_estacion',
        color_continuous_scale='Reds', size_max=20, zoom=12,
        mapbox_style='carto-positron',
        title='Estaciones: color=NO2, tamaño=uso bici'
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.subheader('Top 5 estaciones NO2')
    st.info('Estaciones con mayor concentración media de NO₂.')
    top5_no2 = estaciones.nlargest(5, 'NO2')
    fig_bar_no2 = px.bar(top5_no2, x='codigo_estacion', y='NO2', color='NO2', title='Top 5 NO2')
    st.plotly_chart(fig_bar_no2, use_container_width=True)
    st.subheader('Top 5 estaciones uso bici')
    st.info('Estaciones con mayor uso medio de Valenbisi.')
    top5_bike = estaciones.nlargest(5, 'prestamos_mean')
    fig_bar_bike = px.bar(top5_bike, x='codigo_estacion', y='prestamos_mean', color='prestamos_mean', title='Top 5 uso bici')
    st.plotly_chart(fig_bar_bike, use_container_width=True)
    st.subheader('Selecciona una estación para ver detalles')
    st.info('Consulta la evolución horaria de la contaminación y el uso de la bici en una estación concreta.')
    est_sel = st.selectbox('Estación', sorted(estaciones['codigo_estacion'].unique()))
    df_est = spatial[spatial['codigo_estacion'] == est_sel]
    fig_est = px.line(df_est, x='hour', y=['NO2','prestamos_mean'], labels={'value':'Valor','hour':'Hora','variable':'Variable'}, title=f'Evolución horaria estación {est_sel}')
    st.plotly_chart(fig_est, use_container_width=True)

# --- Sección: Correlaciones y modelos ---
elif seccion == 'Correlaciones y modelos':
    st.header('Correlaciones y modelos')
    st.info('Analiza la relación entre las variables y elabora modelos predictivos simples.')
    st.subheader('Matriz de correlación')
    columnas = ['NO2','PM10','PM2_5','NOx','O3','Veloc','Temp','bike_trips']
    columnas_existentes = [col for col in columnas if col in city.columns]
    corr = city[columnas_existentes].corr()
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu', zmin=-1, zmax=1)
    st.plotly_chart(fig_corr, use_container_width=True)
    st.subheader('Relación NO₂ vs Viajes en Bici')
    st.info('Visualiza la relación directa entre el uso de la bici y la contaminación por NO₂.')
    fig_scatter = px.scatter(city, x='bike_trips', y='NO2', trendline='ols', opacity=0.6,
                            labels={'bike_trips':'Viajes en Bici','NO2':'NO₂'})
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.subheader('Regresión lineal: NO₂ ~ bike_trips + Veloc + Temp')
    st.info('Modelo predictivo sencillo para estimar NO₂ a partir del uso de la bici, la velocidad del viento y la temperatura.')
    X = city[['bike_trips','Veloc','Temp']]
    y = city['NO2']
    reg = LinearRegression().fit(X, y)
    col1, col2 = st.columns(2)
    col1.metric('Intercept', f"{reg.intercept_:.2f}")
    col2.metric('R²', f"{reg.score(X, y):.4f}")
    col3, col4, col5 = st.columns(3)
    col3.metric('Coef bike_trips', f"{reg.coef_[0]:.4f}")
    col4.metric('Coef Veloc', f"{reg.coef_[1]:.4f}")
    col5.metric('Coef Temp', f"{reg.coef_[2]:.4f}")

# --- Sección: Comparativas ---
elif seccion == 'Comparativas':
    st.header('Comparativas')
    st.info('Compara la contaminación y el uso de la bici entre días laborables y fines de semana, y filtra por mes.')
    # Filtro por mes
    meses = sorted(city['month'].unique())
    mes_sel = st.selectbox('Selecciona mes', options=['Todos'] + [str(m) for m in meses], index=0)
    if mes_sel != 'Todos':
        df_comp = city[city['month'] == int(mes_sel)]
    else:
        df_comp = city.copy()
    # Boxplot NO2 laborables vs finde
    st.subheader('NO₂: Laborables vs. Finde')
    fig_box_no2 = px.box(df_comp, x='is_weekend', y='NO2', points='all',
                        labels={'is_weekend':'¿Finde? (0=Laborable, 1=Finde)','NO2':'NO₂'})
    st.plotly_chart(fig_box_no2, use_container_width=True)
    # Boxplot bike_trips laborables vs finde
    st.subheader('Viajes bici: Laborables vs. Finde')
    fig_box_bike = px.box(df_comp, x='is_weekend', y='bike_trips', points='all',
                        labels={'is_weekend':'¿Finde? (0=Laborable, 1=Finde)','bike_trips':'Viajes bici'})
    st.plotly_chart(fig_box_bike, use_container_width=True)

# Footer con nombres
st.markdown(
    '''
    <div style="position: fixed; bottom: 10px; right: 20px; color: #888; font-size: 0.9em; z-index: 100;">
        <span>Josep Ferrer García &nbsp;|&nbsp; 
        <a href="https://germanmallo.com" target="_blank" style="color: #4F8BF9; text-decoration: none;">
            Germán Mallo Faure
        </a>
        </span>
    </div>
    ''',
    unsafe_allow_html=True
) 