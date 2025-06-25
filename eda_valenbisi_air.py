import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Crear carpeta para guardar figuras
os.makedirs('figures', exist_ok=True)

# Cargar datasets principales
city = pd.read_csv('data/city_bike_air_2022.csv')
spatial = pd.read_csv('data/bike_air_spatial_hour_2022.csv')

# --- KPIs básicos ---
# Media y desviación de contaminantes y viajes
kpis = city[['NO2', 'PM10', 'PM2_5', 'O3', 'bike_trips']].agg(['mean', 'std', 'min', 'max'])
kpis.to_csv('figures/kpis_city.csv')
print('KPIs guardados en figures/kpis_city.csv')

# --- Series temporales ---
plt.figure(figsize=(12,5))
plt.plot(city['NO2'], label='NO2')
plt.plot(city['bike_trips'], label='Viajes Bici', alpha=0.7)
plt.title('Evolución NO2 y Viajes en Bici (Ciudad)')
plt.xlabel('Índice temporal')
plt.ylabel('Valor')
plt.legend()
plt.tight_layout()
plt.savefig('figures/serie_NO2_bici.png')
plt.close()

# --- Heatmap hora vs día de la semana (NO2) ---
heatmap_data = city.pivot_table(index='hour', columns='dow', values='NO2', aggfunc='mean')
plt.figure(figsize=(8,6))
sns.heatmap(heatmap_data, cmap='coolwarm')
plt.title('Heatmap NO2 por hora y día de la semana')
plt.ylabel('Hora')
plt.xlabel('Día de la semana (0=Lunes)')
plt.tight_layout()
plt.savefig('figures/heatmap_NO2.png')
plt.close()

# --- Heatmap hora vs día de la semana (Viajes Bici) ---
heatmap_data_bike = city.pivot_table(index='hour', columns='dow', values='bike_trips', aggfunc='mean')
plt.figure(figsize=(8,6))
sns.heatmap(heatmap_data_bike, cmap='YlGnBu')
plt.title('Heatmap Viajes Bici por hora y día de la semana')
plt.ylabel('Hora')
plt.xlabel('Día de la semana (0=Lunes)')
plt.tight_layout()
plt.savefig('figures/heatmap_bike.png')
plt.close()

# --- Scatterplot NO2 vs Viajes Bici ---
plt.figure(figsize=(7,5))
sns.scatterplot(data=city, x='bike_trips', y='NO2', alpha=0.6)
plt.title('Relación NO2 vs Viajes en Bici (Ciudad)')
plt.xlabel('Viajes en Bici')
plt.ylabel('NO2')
plt.tight_layout()
plt.savefig('figures/scatter_NO2_bici.png')
plt.close()

# --- KPIs avanzados ---
# Día y hora con mayor y menor contaminación y uso
max_no2 = city.loc[city['NO2'].idxmax()]
min_no2 = city.loc[city['NO2'].idxmin()]
max_bike = city.loc[city['bike_trips'].idxmax()]
min_bike = city.loc[city['bike_trips'].idxmin()]

with open('figures/kpis_avanzados.txt', 'w') as f:
    f.write(f"Mayor NO2: mes={max_no2['month']}, dow={max_no2['dow']}, hora={max_no2['hour']}, valor={max_no2['NO2']:.2f}\n")
    f.write(f"Menor NO2: mes={min_no2['month']}, dow={min_no2['dow']}, hora={min_no2['hour']}, valor={min_no2['NO2']:.2f}\n")
    f.write(f"Mayor viajes bici: mes={max_bike['month']}, dow={max_bike['dow']}, hora={max_bike['hour']}, valor={max_bike['bike_trips']:.0f}\n")
    f.write(f"Menor viajes bici: mes={min_bike['month']}, dow={min_bike['dow']}, hora={min_bike['hour']}, valor={min_bike['bike_trips']:.0f}\n")
print('KPIs avanzados guardados en figures/kpis_avanzados.txt')

# --- Boxplots por mes, día de la semana y hora ---
for var in ['NO2', 'bike_trips']:
    plt.figure(figsize=(8,5))
    sns.boxplot(x='month', y=var, data=city)
    plt.title(f'Distribución de {var} por mes')
    plt.tight_layout()
    plt.savefig(f'figures/boxplot_{var}_mes.png')
    plt.close()
    plt.figure(figsize=(8,5))
    sns.boxplot(x='dow', y=var, data=city)
    plt.title(f'Distribución de {var} por día de la semana')
    plt.tight_layout()
    plt.savefig(f'figures/boxplot_{var}_dow.png')
    plt.close()
    plt.figure(figsize=(8,5))
    sns.boxplot(x='hour', y=var, data=city)
    plt.title(f'Distribución de {var} por hora')
    plt.tight_layout()
    plt.savefig(f'figures/boxplot_{var}_hora.png')
    plt.close()

# --- Matriz de correlación ---
plt.figure(figsize=(10,8))
corr = city[['NO2','PM10','PM2_5','NOx','O3','Veloc','Temp','bike_trips']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Matriz de correlación de variables')
plt.tight_layout()
plt.savefig('figures/correlacion_variables.png')
plt.close()

# --- Regresión lineal NO2 ~ bike_trips + Veloc + Temp ---
from sklearn.linear_model import LinearRegression
X = city[['bike_trips','Veloc','Temp']]
y = city['NO2']
reg = LinearRegression().fit(X, y)
coefs = dict(zip(X.columns, reg.coef_))
r2 = reg.score(X, y)
with open('figures/regresion_NO2.txt', 'w') as f:
    f.write(f"Intercept: {reg.intercept_:.2f}\n")
    for var, coef in coefs.items():
        f.write(f"Coef {var}: {coef:.4f}\n")
    f.write(f"R2: {r2:.4f}\n")
print('Resultados de regresión guardados en figures/regresion_NO2.txt')

# --- Comparativa laborables vs. fines de semana ---
city['is_weekend'] = city['dow'].apply(lambda x: 1 if x in [5,6] else 0)
for var in ['NO2','bike_trips']:
    plt.figure(figsize=(6,4))
    sns.boxplot(x='is_weekend', y=var, data=city)
    plt.title(f'{var}: Laborables (0) vs. Finde (1)')
    plt.tight_layout()
    plt.savefig(f'figures/boxplot_{var}_weekend.png')
    plt.close()

# --- Evolución mensual de contaminación y uso bici ---
for var in ['NO2','bike_trips']:
    plt.figure(figsize=(8,5))
    city.groupby('month')[var].mean().plot(marker='o')
    plt.title(f'Evolución mensual de {var}')
    plt.xlabel('Mes')
    plt.ylabel(var)
    plt.tight_layout()
    plt.savefig(f'figures/evolucion_mensual_{var}.png')
    plt.close()

# --- Top 5 estaciones con más/menos NO2 y uso bici ---
spatial_mean = spatial.groupby('codigo_estacion').agg({'NO2':'mean','prestamos_mean':'mean'}).reset_index()
top5_no2 = spatial_mean.nlargest(5, 'NO2')
bot5_no2 = spatial_mean.nsmallest(5, 'NO2')
top5_bike = spatial_mean.nlargest(5, 'prestamos_mean')
bot5_bike = spatial_mean.nsmallest(5, 'prestamos_mean')
top5_no2.to_csv('figures/top5_no2.csv', index=False)
bot5_no2.to_csv('figures/bot5_no2.csv', index=False)
top5_bike.to_csv('figures/top5_bike.csv', index=False)
bot5_bike.to_csv('figures/bot5_bike.csv', index=False)
print('Top estaciones guardadas en figures/')

# --- Mapa de estaciones (NO2 y uso bici) ---
# (Solo como scatter, sin mapa interactivo aún)
if 'lat' in spatial.columns and 'lon' in spatial.columns:
    plt.figure(figsize=(8,6))
    plt.scatter(spatial['lon'], spatial['lat'], c=spatial['NO2'], cmap='Reds', s=spatial['prestamos_mean']*10+10, alpha=0.7)
    plt.colorbar(label='NO2')
    plt.title('Estaciones: color=NO2, tamaño=uso bici')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.tight_layout()
    plt.savefig('figures/mapa_estaciones_no2_bici.png')
    plt.close()
else:
    print('No hay columnas lat/lon en spatial para mapa de estaciones.')

print('EDA avanzada completada. Revisa la carpeta figures.')

print('Gráficos guardados en la carpeta figures/') 