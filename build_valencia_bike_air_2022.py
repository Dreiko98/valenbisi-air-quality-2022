"""
build_valencia_bike_air_2022.py
--------------------------------
Pipeline completo: Valenbisi 2022 + Calidad del aire 2022 (Valencia)

Salida:
  data/bike_city_agg_2022.csv           (mes × día_semana × hora)
  data/air_city_agg_2022.csv
  data/city_bike_air_2022.csv           (merge global)
  data/bike_station_hour_2022.csv       (estación bici × hora)
  data/air_station_hour_2022.csv        (estación aire × hora)
  data/stations_crosswalk.csv           (bici ↔ aire + distancia km)
  data/bike_air_spatial_hour_2022.csv   (detalle espacial)

Requisitos:
    pip install pandas requests scipy tqdm python-dateutil
Uso:
    python build_valencia_bike_air_2022.py
"""
from __future__ import annotations
import re, requests
from pathlib import Path
from io import StringIO
import pandas as pd
from scipy.spatial import cKDTree

# ───────────── paths & ids ─────────────
DATA_DIR  = Path("data"); DATA_DIR.mkdir(exist_ok=True)
AIR_DIR   = Path("air_txt")                           # .txt horarios 2022
AIR_COORD = DATA_DIR / "air_station_coords.csv"       # manual (12 filas)

VAL_API = ("https://valencia.opendatasoft.com/api/explore/v2.1/catalog/"
           "datasets/{}/exports/csv?limit=-1")
VAL_IDS = {
    "bike_hour" : "valenbici-2022-alquileres-por-mes-dia-hora",
    "bike_dev"  : "valenbisi-2022-alquileres-y-devoluciones",
    "bike_geo"  : "valenbisi-disponibilitat-valenbisi-dsiponibilidad",
}

ENCODING="latin1"; DECIMAL=","; NA=["","-","NA"]

MES = {m:i for i,m in enumerate(
    ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
     "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])}
DOW={"Lunes":0,"Martes":1,"Miércoles":2,"Miercoles":2,
     "Jueves":3,"Viernes":4,"Sábado":5,"Sabado":5,"Domingo":6}

# ───────── helpers ─────────
def fetch(dataset:str, out:Path, sep=";")->pd.DataFrame:
    csv=requests.get(VAL_API.format(dataset),timeout=60).text
    out.write_text(csv,encoding="utf-8")
    return pd.read_csv(StringIO(csv),sep=sep)

def bike_city()->pd.DataFrame:
    df=fetch(VAL_IDS["bike_hour"],DATA_DIR/"raw_bike_hour.csv")
    df["hour"]=df["tramo_horario"].str[:2].astype(int)
    df["month"]=df["mes"].map(MES); df["dow"]=df["dia_semana"].map(DOW)
    out=(df.groupby(["month","dow","hour"],as_index=False)
           .agg(bike_trips=("suma_numero_viajes","sum"),
                bike_dur_tot=("suma_duracion_total_viajes","sum")))
    out.to_csv(DATA_DIR/"bike_city_agg_2022.csv",index=False)
    return out

def bike_station_hour() -> pd.DataFrame:
    df = fetch(VAL_IDS["bike_dev"], DATA_DIR / "raw_bike_dev.csv")
    df["hour"] = df["tramo_horario"].str[:2].astype(int)

    agg = (
        df.groupby(["codigo_estacion", "hour"], as_index=False)
          .agg(prestamos_sum=("numero_de_prestamos", "sum"),
               devol_sum    =("numero_de_devoluciones", "sum"))
    )

    # Promedio diario (dividir solo las métricas)
    agg["prestamos_mean"] = agg["prestamos_sum"] / 365
    agg["devol_mean"]     = agg["devol_sum"]     / 365
    agg = agg.drop(columns=["prestamos_sum", "devol_sum"])

    agg.to_csv(DATA_DIR / "bike_station_hour_2022.csv", index=False)
    return agg


def bike_geo() -> pd.DataFrame:
    """
    Descarga el dataset de disponibilidad y extrae:
        codigo_estacion (int), lat, lon
    """
    url = ("https://valencia.opendatasoft.com/api/explore/v2.1/catalog/"
           "datasets/valenbisi-disponibilitat-valenbisi-dsiponibilidad/exports/csv?limit=-1")
    df = pd.read_csv(url, sep=";")

    # geo_point_2d → 2 columnas
    lat_lon = df["geo_point_2d"].str.split(",", expand=True).astype(float)
    df["lat"], df["lon"] = lat_lon[0], lat_lon[1]

    # id numérico
    df = df.rename(columns={"number": "codigo_estacion"})
    df["codigo_estacion"] = df["codigo_estacion"].astype(int)

    keep = df[["codigo_estacion", "lat", "lon"]].drop_duplicates("codigo_estacion")
    keep.to_csv(DATA_DIR / "bike_station_coords.csv", index=False)
    return keep


def load_txt(f:Path)->pd.DataFrame:
    rows=f.read_text(encoding=ENCODING).splitlines()
    st_line=next(l for l in rows if l.startswith("Estación:"))
    st_id,st_name=re.findall(r"Estación:\s*(\d+)-\s*(.+)",st_line)[0]
    hdr_i=next(i for i,l in enumerate(rows) if l.lstrip().startswith("FECHA"))
    hdr=re.split(r"\s+",rows[hdr_i].strip()); data=rows[hdr_i+2:]
    df=pd.read_csv(StringIO(" ".join(hdr)+"\n"+"\n".join(data)),
                   sep=r"\s+",decimal=DECIMAL,na_values=NA,encoding=ENCODING)
    df["datetime"]=pd.to_datetime(df["FECHA"]+" "+df["HORA"].astype(str).str.zfill(2),
                                  format="%d/%m/%Y %H")
    df.drop(columns=["FECHA","HORA"],inplace=True)
    df["station_id"],df["station_name"]=st_id,st_name.strip()
    return df

def air_data()->tuple[pd.DataFrame,pd.DataFrame]:
    full=pd.concat([load_txt(f) for f in AIR_DIR.glob("*.txt")],ignore_index=True)
    full.to_csv(DATA_DIR/"air_station_hour_2022.csv",index=False)

    full["month"]=full["datetime"].dt.month
    full["dow"]=full["datetime"].dt.dayofweek
    full["hour"]=full["datetime"].dt.hour
    city=(full.groupby(["month","dow","hour"],as_index=False)
            .agg(NO2=("NO2","mean"),PM10=("PM10","mean"),PM2_5=("PM2.5","mean"),
                 NOx=("NOx","mean"),O3=("O3","mean"),
                 Veloc=("Veloc.","mean"),Temp=("Temp.","mean")))
    city.to_csv(DATA_DIR/"air_city_agg_2022.csv",index=False)
    return city,full

# ─── En la función crosswalk(), fuerza ambos ids a int ───────────────
def crosswalk(bike_hour: pd.DataFrame, air_full: pd.DataFrame):
    st_b = bike_geo()                         # ← ya con lat/lon correctas
    st_a = pd.read_csv(AIR_COORD)

    # id del csv manual a int por coherencia
    st_a["station_id"] = st_a["station_id"].astype(int)

    # KD-Tree
    tree = cKDTree(st_a[["lat", "lon"]])
    dist, idx = tree.query(st_b[["lat", "lon"]], k=1)
    st_b["nearest_aq_station"] = st_a.loc[idx, "station_id"].values
    st_b["dist_km"] = dist * 111
    st_b.to_csv(DATA_DIR / "stations_crosswalk.csv", index=False)

    # merge final
    bike_hour["codigo_estacion"] = bike_hour["codigo_estacion"].astype(int)
    bike_geo_hour = bike_hour.merge(
        st_b[["codigo_estacion", "nearest_aq_station", "dist_km"]],
        on="codigo_estacion"
    )

    air_full["station_id"] = air_full["station_id"].astype(int)
    air_full["hour"] = air_full["datetime"].dt.hour
    air_hour = (
        air_full.groupby(["station_id", "hour"], as_index=False)
        .agg(NO2=("NO2", "mean"), PM10=("PM10", "mean"), PM2_5=("PM2.5", "mean"))
    )

    df = (
        bike_geo_hour.merge(
            air_hour,
            left_on=["nearest_aq_station", "hour"],
            right_on=["station_id", "hour"]
        )
        .drop(columns="station_id")
    )
    df.to_csv(DATA_DIR / "bike_air_spatial_hour_2022.csv", index=False)


# ───────── pipeline ─────────
if __name__=="__main__":
    print("▶ Valenbisi ciudad-hora");   bike_c=bike_city()
    print("▶ Valenbisi estación-hora"); bike_s=bike_station_hour()
    print("▶ Aire horario 2022");        air_c,air_f=air_data()

    city=bike_c.merge(air_c,on=["month","dow","hour"])
    city.to_csv(DATA_DIR/"city_bike_air_2022.csv",index=False)

    print("▶ Cross-walk espacial")
    crosswalk(bike_s,air_f)

    # ── Validación rápida ───────────────────────
    summary={
        "bike_city_agg":pd.read_csv(DATA_DIR/"bike_city_agg_2022.csv").shape,
        "air_city_agg": pd.read_csv(DATA_DIR/"air_city_agg_2022.csv").shape,
        "city_merge":  city.shape,
        "bike_station_hour": pd.read_csv(DATA_DIR/"bike_station_hour_2022.csv").shape,
        "air_station_hour":  pd.read_csv(DATA_DIR/"air_station_hour_2022.csv").shape,
        "crosswalk": pd.read_csv(DATA_DIR/"stations_crosswalk.csv").shape,
        "bike_air_spatial": pd.read_csv(DATA_DIR/"bike_air_spatial_hour_2022.csv").shape,
    }
    print("\n📊  Resumen de CSVs generados:")
    for k,v in summary.items(): print(f"  {k:20s} → {v[0]:6,d} filas × {v[1]} cols")

    print("\n✅ Pipeline finalizado sin peticiones externas en cross-walk.")
