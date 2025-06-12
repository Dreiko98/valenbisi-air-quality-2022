# build_air_quality_2022.py
# ---------------------------------------------------------------
# Convierte todos los .txt horarios de la Red Valenciana (Valencia 2022)
# en un único CSV limpio y homogéneo
# ---------------------------------------------------------------
import re
from pathlib import Path
from io import StringIO

import pandas as pd

# ---------------------------
# 1. Configuración
# ---------------------------
TXT_DIR   = Path("calidad_aire_2022") # Carpeta donde hayas metido los .txt
OUT_CSV   = Path("data/air_quality_valencia_2022.csv")
ENCODING  = "latin1"                  # El portal usa ANSI / ISO-8859-1
DECIMAL   = ","                       # Notación española “3,5”
NA_VALUES = ["", "-", "NA", "N/A"]    # Marcadores de nulo a interpretar

# ---------------------------
# 2. Función para un archivo
# ---------------------------
def load_station_txt(path: Path) -> pd.DataFrame:
    """
    Lee el .txt de una estación, detecta cabeceras y devuelve un DataFrame.
    - Convierte coma decimal a punto (decimal=DECIMAL)
    - Añade columnas station_id y station_name
    - Devuelve datetime como índice
    """
    # Leemos todo el fichero
    raw = path.read_text(encoding=ENCODING).splitlines()

    # ---- 2.1 Extraer metadatos de la línea 'Estación:' -------------
    est_line  = next(l for l in raw if l.startswith("Estación:"))
    station_id, station_name = re.findall(r"Estación:\s*(\d+)-\s*(.+)", est_line)[0]
    station_name = station_name.strip()

    # ---- 2.2 Localizar la cabecera “FECHA HORA …” ------------------
    hdr_idx = next(i for i, l in enumerate(raw) if l.lstrip().startswith("FECHA"))
    header  = re.split(r"\s+", raw[hdr_idx].strip())           # Ej.: ['FECHA','HORA','Veloc.','Direc.',…]
    # Dos líneas más abajo suelen venir las unidades -> saltamos 2
    data_lines = raw[hdr_idx + 2 :]

    # ---- 2.3 Construir CSV en memoria y parsear con pandas ----------
    tmp = " ".join(header) + "\n" + "\n".join(data_lines)
    df  = pd.read_csv(
        StringIO(tmp),
        sep=r"\s+",
        decimal=DECIMAL,
        na_values=NA_VALUES,
        encoding=ENCODING,
    )

    # ---- 2.4 Datetime unificada ------------------------------------
    df["datetime"] = pd.to_datetime(
        df["FECHA"] + " " + df["HORA"].astype(str).str.zfill(2),
        format="%d/%m/%Y %H",
    )
    df = df.drop(columns=["FECHA", "HORA"]).set_index("datetime")

    # ---- 2.5 Añadir columnas estación ------------------------------
    df["station_id"]   = station_id
    df["station_name"] = station_name

    return df


# ---------------------------
# 3. Cargar TODOS los .txt
# ---------------------------
def build_all():
    dfs = []
    for txt in TXT_DIR.glob("*.txt"):
        print(f"↳ Procesando {txt.name}")
        try:
            dfs.append(load_station_txt(txt))
        except Exception as e:
            print(f"   ⚠️  Error en {txt.name}: {e}")

    merged = pd.concat(dfs).sort_index()
    OUT_CSV.parent.mkdir(exist_ok=True)
    merged.to_csv(OUT_CSV, index=True)
    print("\n✅ CSV final guardado en:", OUT_CSV, "→", merged.shape, "filas,columnas")


if __name__ == "__main__":
    build_all()
