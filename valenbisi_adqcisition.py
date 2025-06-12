"""
download_and_merge_valencia.py
------------------------------
Starter script for the university project.

* Downloads the three 2022 Valenbisi datasets from Valencia's Open‑Data portal.
* Concatenates them into a single DataFrame (valenbisi_2022_merged.csv).
* Contains scaffolding functions to incorporate 2022 air‑quality data
  from Generalitat Valenciana once the final file URLs are known.

Run:
    python download_and_merge_valencia.py

Dependencies:
    pip install pandas requests tqdm openpyxl
"""
import os
from pathlib import Path
import requests
import pandas as pd
from io import BytesIO, StringIO
from tqdm import tqdm

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Valenbisi 2022 ----------------------------------------------------------------
# ---------------------------------------------------------------------------
VALENBISI_DATASETS = {
    "alquileres_hora": "valenbici-2022-alquileres-por-mes-dia-hora",
    "alquileres_devoluciones": "valenbisi-2022-alquileres-y-devoluciones",
    "tipo_abonos": "valenbisi-2022-tipo-de-abonos",
}

VALENCIA_OD_BASE = (
    "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/{}/exports/csv?limit=-1"
)

def fetch_valenbisi_dataset(dataset_id: str) -> pd.DataFrame:
    """Download a Valenbisi dataset via the Opendatasoft CSV export API."""
    url = VALENCIA_OD_BASE.format(dataset_id)
    print(f"→ Downloading {dataset_id} …".ljust(60), end="")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    # Guardar el contenido para inspección
    with open(f"data/{dataset_id}.csv", "w", encoding="utf-8") as f:
        f.write(r.text)
    # Detectar el separador según el dataset
    sep = ";"
    df = pd.read_csv(StringIO(r.text), sep=sep)
    print("✅", f"{len(df):,} rows")
    return df

def build_valenbisi_2022() -> pd.DataFrame:
    """Download & concatenate the three 2022 Valenbisi datasets."""
    dfs = []
    for key, ds_id in VALENBISI_DATASETS.items():
        df = fetch_valenbisi_dataset(ds_id)
        df["source"] = key
        dfs.append(df)
    merged = pd.concat(dfs, ignore_index=True, sort=False)
    out_csv = DATA_DIR / "valenbisi_2022_merged.csv"
    merged.to_csv(out_csv, index=False)
    print(f"→ Saved merged Valenbisi CSV to {out_csv} (shape={merged.shape})")
    return merged

# ---------------------------------------------------------------------------
# 2. Entry‑point -------------------------------------------------------------
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("▸ Building Valenbisi 2022 dataset …")    
    valenbisi_df = build_valenbisi_2022()