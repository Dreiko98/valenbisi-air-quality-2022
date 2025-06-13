# Proyecto **Valenbisi × Calidad del Aire 2022**

> **Estado**: *ETL estable* — datasets limpios y validados listos para EDA y app Streamlit

---

## 1 · Resumen rápido

Investigamos la relación entre el **uso de Valenbisi** y la **contaminación atmosférica** en València (2022).

* **Granularidad ciudad** → mes × día‑de‑la‑semana × hora (2 016 filas)
* **Granularidad estación** → estación Valenbisi × hora (6 532 filas) enlazada a la estación de aire más cercana.

---

## 2 · Ejecutar el pipeline

```bash
# Clonar repo y entrar
pip install -r requirements.txt  # pandas, requests, scipy, tqdm …

# Colocar .txt de aire 2022
mkdir air_txt
# (pega aquí los 12 ficheros descargados de la Generalitat)

# Lanzar el ETL
python build_valencia_bike_air_2022.py
```

El script descarga los datasets Valenbisi, procesa `air_txt/` y valida los CSV finales.

---

## 3 · Estructura de carpetas

```
📂 data/
   ├─ bike_city_agg_2022.csv           # Bici ciudad (2 016 × 5)
   ├─ air_city_agg_2022.csv            # Aire ciudad (2 016 × 10)
   ├─ city_bike_air_2022.csv           # Merge ciudad (2 016 × 12)
   ├─ bike_station_hour_2022.csv       # Bici estación‑hora (6 609 × 4)
   ├─ air_station_hour_2022.csv        # Aire estación‑hora (104 412 × 24)
   ├─ stations_crosswalk.csv           # Emparejamiento bici↔aire (273 × 5)
   └─ bike_air_spatial_hour_2022.csv   # Merge espacial (6 532 × 9)
📂 air_txt/  # ficheros de aire 2022
build_valencia_bike_air_2022.py        # Script ETL
README.md                               # Este documento
```

---

## 4 · Descripción de outputs clave

| CSV                                    | Clave primaria          | Columnas destacadas                                                        |
| -------------------------------------- | ----------------------- | -------------------------------------------------------------------------- |
| **city\_bike\_air\_2022.csv**          | `month, dow, hour`      | `bike_trips`, `bike_dur_tot`, **NO₂**, PM₁₀, PM₂.₅, NOx, O₃, viento, temp. |
| **bike\_air\_spatial\_hour\_2022.csv** | `codigo_estacion, hour` | `prestamos_mean`, **NO₂**, PM₁₀, PM₂.₅, `dist_km`, `lat`, `lon`            |

*Contaminantes a nivel ciudad = media de 12 estaciones. A nivel estación = datos de la estación de aire más cercana.*

---

## 5 · Próximos pasos sugeridos

1. **EDA** — series temporales y heatmaps.
2. **Correlaciones** ciudad‑nivel.
3. **Modelo lineal**: `NO2 ~ bike_trips + Veloc + Temp`.
4. **Mapa interactivo** con burbujas.
5. **App Streamlit** con sidebar y pestañas.

---

## 6 · TODO

* [ ] Verificar huecos en los `.txt` de aire.
* [ ] Revisar estaciones con `dist_km > 2` km.
* [ ] Documentar `bike_dur_tot`.
* [ ] Completar `requirements.txt`.
* [ ] Iniciar app Streamlit.

---

## 7 · Bitácora

| Fecha      | Avance                                      | Notas                                                 |
| ---------- | ------------------------------------------- | ----------------------------------------------------- |
| 2025‑06‑12 | Pipeline inicial construido y ejecutado.    | primer ETL completo, CSVs generados.                  |
| 2025‑06‑13 | Validación de CSVs + corrección cross‑walk. | 6 532 filas espaciales correctas, README actualizado. |
| Próxima    | EDA + primeras visualizaciones.             | Notebook / Streamlit.                                 |

> **Tip**: borra `data/` y vuelve a lanzar `python build_valencia_bike_air_2022.py` para recrear todo en \~2 min.
