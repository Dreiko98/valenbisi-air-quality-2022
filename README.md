# Proyecto "Valenbisi × Calidad del Aire 2022"

> **Estado**: *Pipeline de descarga, limpieza y agregación completado* (👷‍♀️ listo para análisis y app Streamlit)

---

## 1 · Resumen rápido

Este proyecto investiga la relación entre **uso de bicicleta compartida (Valenbisi)** y **contaminación atmosférica** en la ciudad de Valencia durante 2022.

🔹 *Granularidad "ciudad"*: mes × día‑de‑la‑semana × hora (2 016 filas)

🔹 *Granularidad "estación"*: estación Valenbisi × hora (≈ 6 600 filas) enlazada a la estación de calidad del aire más cercana.

El ETL completa la descarga de datos abiertos, la normalización y la fusión en CSV listos para ciencia de datos y visualización.

---

## 2 · Cómo ejecutar el pipeline

```bash
# 0 · Clonar repo y entrar
pip install -r requirements.txt   # pandas, requests, tqdm, python-dateutil, scipy

# 1 · Colocar los .txt horarios de aire 2022 en:
mkdir air_txt
# (copiar aquí los ficheros descargados manualmente de la web de la Generalitat)

# 2 · Lanzar el script principal
python build_valencia_bike_air_2022.py
```

El script descargará automáticamente los datasets de Valenbisi y procesará todos los `.txt` de `air_txt/`.

---

## 3 · Estructura de carpetas

```
📂 data/
   ├─ bike_city_agg_2022.csv           # Bici ciudad  (2 016 filas)
   ├─ air_city_agg_2022.csv            # Aire ciudad  (2 016 filas)
   ├─ city_bike_air_2022.csv           # Merge ciudad
   ├─ bike_station_hour_2022.csv       # Bici por estación‑hora
   ├─ air_station_hour_2022.csv        # Aire por estación‑hora (full serie)
   ├─ stations_crosswalk.csv           # Emparejamiento bici ↔ aire + distancia
   └─ bike_air_spatial_hour_2022.csv   # Merge espacial
📂 air_txt/            # (input) ficheros .txt horarios 2022 por estación de aire
build_valencia_bike_air_2022.py        # Script ETL principal
README.md                               # Este documento
```

---

## 4 · Descripción de los outputs clave

| Archivo                                | Granularidad             | Columnas principales                                                                 |
| -------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------ |
| **city\_bike\_air\_2022.csv**          | mes, dow, hora           | `bike_trips`, `bike_dur_tot`, `NO2`, `PM10`, `PM2.5`, `NOx`, `O3`, `Veloc.`, `Temp.` |
| **bike\_air\_spatial\_hour\_2022.csv** | estación Valenbisi, hora | `prestamos_mean`, `NO2`, `PM10`, `PM2.5`, `dist_km`, `lat`, `lon`                    |

Nota: los contaminantes son medias de todas las estaciones de aire en la ciudad (nivel ciudad) o de la estación más cercana (nivel estación).

---

## 5 · Siguientes pasos propuestos

1. **Exploración básica (EDA)**

   * Serie temporal `bike_trips` vs `NO2`.
   * Heatmap hora × día de la semana.
2. **Correlaciones ciudad‑nivel**

   * Pearson/Spearman entre viajes y contaminantes.
3. **Modelo lineal multivariante**

   * `NO2 ~ bike_trips + Veloc. + Temp.`
4. **Mapa interactivo (fase espacial)**

   * Burbujas tamaño ∝ viajes, color ∝ NO₂; slider de hora.
5. **Streamlit App skeleton**

   * Sidebar → rango de fechas, contaminante.
   * Tabs → Visión general · Mapas · Modelado · Predicción (opcional).

---

## 6 · Tareas pendientes / TODO

* [ ] Validar que los `.txt` de todas las estaciones 2022 están completos (sin días faltantes).
* [ ] Revisar `dist_km` > 2 km → decidir si excluir o reasignar.
* [ ] Documentar significado de columnas menos obvias (`bike_dur_tot`).
* [ ] Escribir `requirements.txt` definitivo.
* [ ] Commits iniciales y push a GitHub.

---

## 7 · Bitácora de trabajo

| Fecha          | Avance                                  | Notas                                                                      |
| -------------- | --------------------------------------- | -------------------------------------------------------------------------- |
| 2025‑06‑12     | Se creó y ejecutó el pipeline completo. | Script `build_valencia_bike_air_2022.py` funcionando y datasets generados. |
| Próxima sesión | EDA + primeros gráficos.                | Cargar `city_bike_air_2022.csv` en notebook / Streamlit.                   |

---

> **Tip**: si te pierdes, simplemente vuelve a lanzar `python build_valencia_bike_air_2022.py` – tardará \~1‑2 min y recreará todo desde cero.
