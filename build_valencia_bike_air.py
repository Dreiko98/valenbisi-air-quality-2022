"""
build_valencia_bike_air_2022.py
--------------------------------
Pipeline completo para el TFG/TFM.

• Descarga:
    - Valenbisi 2022  ▸ alquileres-por-mes-dia-hora  (para uso global)
    - Valenbisi 2022  ▸ alquileres-y-devoluciones    (para detalle espacial)
• Procesa todos los .txt horarios 2022 de calidad del aire en ./air_txt/
• Agrega ambos bloques a nivel:
      (mes, dia_semana, hour)  ➔ city_agg
• Genera:
      data/bike_city_agg_2022.csv
      data/air_city_agg_2022.csv
      data/city_bike_air_2022.csv
      data/bike_station_hour_2022.csv          (detalle espacial opcional)
      data/air_station_hour_2022.csv
      data/stations_crosswalk.csv              (bici ↔ aire por proximidad)

Requisitos:
    pip install pandas requests tqdm python-dateutil scipy
Uso:
    python build_valencia_bike_air_2022.py
"""
from __future__ import annotations
import re, calendar, requests, json
from pathlib import Path
from io import StringIO
from datetime import datetime

import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.spatial import cKDTree
from dateutil.relativedelta import relativedelta

# ───────────────────────── CONFIG ──────────────────────────
DATA_DIR   = Path("data")
AIR_DIR    = Path("air_txt")      # aquí metiste los .txt descargados
DATA_DIR.mkdir(exist_ok=True)

VALENBISI_IDS = {
    "alquileres_hora":        "valenbici-2022-alquileres-por-mes-dia-hora",
    "alquileres_devoluciones":"valenbisi-2022-alquileres-y-devoluciones",
}
VALENCIA_OD = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/{}/exports/csv?limit=-1"

ENCODING  = "latin1"
DECIMAL   = ","
NA_VALUES = ["", "-", "NA", "N/A"]

# Mapeos español → número
MES_MAP  = {m: i for i, m in enumerate([
    "", "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])}
DOW_MAP  = {"Lunes":0,"Martes":1,"Miércoles":2,"Miercoles":2,
            "Jueves":3,"Viernes":4,"Sábado":5,"Sabado":5,"Domingo":6}

# ────────────────────── HELPER FUNCTIONS ───────────────────
def fetch_csv(dataset_id:str) -> pd.DataFrame:
    url = VALENCIA_OD.format(dataset_id)
    r   = requests.get(url, timeout=60)
    r.raise_for_status()
    path = DATA_DIR / f"{dataset_id}.csv"
    path.write_text(r.text, encoding="utf-8")
    return pd.read_csv(StringIO(r.text), sep=";")

def build_bike_hour_city() -> pd.DataFrame:
    """Agrega alquileres-hora a (mes,dia_semana,hour) ciudad."""
    df = fetch_csv(VALENBISI_IDS["alquileres_hora"])
    df["hour"] = df["tramo_horario"].str.slice(0,2).astype(int)
    df["month"] = df["mes"].map(MES_MAP)
    df["dow"]   = df["dia_semana"].map(DOW_MAP)
    out = (df.groupby(["month","dow","hour"], as_index=False)
             [["suma_numero_viajes","suma_duracion_total_viajes"]]
             .sum()
             .rename(columns={"suma_numero_viajes":"bike_trips",
                              "suma_duracion_total_viajes":"bike_dur_tot"}))
    out.to_csv(DATA_DIR/"bike_city_agg_2022.csv", index=False)
    return out

def build_bike_station_hour() -> pd.DataFrame:
    """Viajes promedio por estación Valenbisi × hora (detalle espacial)."""
    df = fetch_csv(VALENBISI_IDS["alquileres_devoluciones"])
    df["hour"] = df["tramo_horario"].str.slice(0,2).astype(int)
    hourly = (df.groupby(["codigo_estacion","hour"], as_index=False)
                [["numero_de_prestamos","numero_de_devoluciones"]]
                .sum()
                .div(365)
                .rename(columns={"numero_de_prestamos":"prestamos_mean",
                                 "numero_de_devoluciones":"devol_mean"}))
    hourly.to_csv(DATA_DIR/"bike_station_hour_2022.csv", index=False)
    return hourly

# ── AIR QUALITY ─────────────────────────────────────────────
def load_station_txt(path:Path) -> pd.DataFrame:
    rows = path.read_text(encoding=ENCODING).splitlines()
    est   = next(l for l in rows if l.startswith("Estación:"))
    st_id, st_name = re.findall(r"Estación:\s*(\d+)-\s*(.+)", est)[0]
    hdr_i = next(i for i,l in enumerate(rows) if l.lstrip().startswith("FECHA"))
    hdr   = re.split(r"\s+", rows[hdr_i].strip())
    data  = rows[hdr_i+2:]
    df = pd.read_csv(StringIO(" ".join(hdr)+"\n"+"\n".join(data)),
                     sep=r"\s+", decimal=DECIMAL, na_values=NA_VALUES,
                     encoding=ENCODING)
    df["datetime"] = pd.to_datetime(df["FECHA"]+" "+df["HORA"].astype(str).str.zfill(2),
                                    format="%d/%m/%Y %H")
    df.drop(columns=["FECHA","HORA"], inplace=True)
    df["station_id"] = st_id
    df["station_name"] = st_name.strip()
    return df.set_index("datetime")

def build_air_hour_city() -> pd.DataFrame:
    dfs=[]
    for txt in AIR_DIR.glob("*.txt"):
        print("↳", txt.name)
        dfs.append(load_station_txt(txt))
    full = pd.concat(dfs)
    full.reset_index(inplace=True)
    full.to_csv(DATA_DIR/"air_station_hour_2022.csv", index=False)

    full["month"] = full["datetime"].dt.month
    full["dow"]   = full["datetime"].dt.dayofweek
    full["hour"]  = full["datetime"].dt.hour
    city = (full.groupby(["month","dow","hour"], as_index=False)
                 [ ["NO2","PM10","PM2.5","NOx","O3","Veloc.","Temp."] ]
                 .mean())
    city.to_csv(DATA_DIR/"air_city_agg_2022.csv", index=False)
    return city, full

# ── STATIONS GEO (para emparejar aire↔bici) ─────────────────
def load_geo_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    # ∙ Valenbisi estaciones
    url_b = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/valenbisi-estaciones/exports/csv?limit=-1"
    st_b  = pd.read_csv(url_b, sep=";")[["code","lat","lon"]].rename(columns={"code":"codigo_estacion"})
    # ∙ Aire estaciones
    url_a = "https://mediambient.gva.es/documents/21332679/123984664/listado_estaciones_red_valenciana.csv"
    st_a  = load_air_stations_geo().rename(columns={"station_id":"station_id"})
    st_a.rename(columns={"CODI":"station_id","LATITUD":"lat","LONGITUD":"lon"}, inplace=True)
    return st_b, st_a

def load_air_stations_geo() -> pd.DataFrame:
    """
    Descarga desde OpenData València (dataset 'rvvcca') solo la lista de estaciones
    y sus coordenadas únicas.
    """
    url = ("https://valencia.opendatasoft.com/api/explore/v2.1/catalog/"
           "datasets/rvvcca/exports/csv?select=station_id%2C%20station_name%2C%20"
           "lat%2C%20lon&distinct=station_id&limit=-1")
    geo = pd.read_csv(url)
    return geo.dropna(subset=["lat","lon"])


def build_crosswalk(bike_hour:pd.DataFrame, air_full:pd.DataFrame):
    st_b, st_a = load_geo_tables()

    # KD-tree nearest neighbour
    tree = cKDTree(st_a[["lat","lon"]].values)
    dist, idx = tree.query(st_b[["lat","lon"]].values, k=1)
    st_b["nearest_aq_station"] = st_a.loc[idx,"station_id"].values
    st_b["dist_km"] = dist*111  # aprox 1° ≈111 km
    st_b.to_csv(DATA_DIR/"stations_crosswalk.csv", index=False)

    # merge bike-hour + air-hour
    bike_geo = bike_hour.merge(st_b[["codigo_estacion","nearest_aq_station","dist_km"]],
                               on="codigo_estacion")
    air_full["hour"] = air_full["datetime"].dt.hour
    air_hour = (air_full.groupby(["station_id","hour"], as_index=False)
                          [["NO2","PM10","PM2.5"]].mean())
    df = (bike_geo.merge(air_hour,
                         left_on=["nearest_aq_station","hour"],
                         right_on=["station_id","hour"])
                 .drop(columns="station_id"))
    df.to_csv(DATA_DIR/"bike_air_spatial_hour_2022.csv", index=False)

# ────────────────────────── MAIN ────────────────────────────
if __name__ == "__main__":
    print("▸ 1. Valenbisi ciudad-hora …")
    bike_city = build_bike_hour_city()

    print("▸ 2. Valenbisi estación-hora …")
    bike_station_hour = build_bike_station_hour()

    print("▸ 3. Calidad del aire …")
    air_city, air_full = build_air_hour_city()

    print("▸ 4. Unión CITY-LEVEL …")
    city_merged = bike_city.merge(air_city, on=["month","dow","hour"])
    city_merged.to_csv(DATA_DIR/"city_bike_air_2022.csv", index=False)
    print("   ➜ city_bike_air_2022.csv", city_merged.shape)

    print("▸ 5. Unión ESPACIAL (opcional) …")
    try:
        build_crosswalk(bike_station_hour, air_full)
    except Exception as e:
        print("   ⚠️  No se pudo construir el crosswalk:", e)

    print("\n✅ Pipeline completo. ¡Listo para analizar!")
