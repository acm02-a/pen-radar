"""
Guarda y lee el historico del tipo de cambio en un CSV.

Regla clave: un dia = una fila. Al fusionar datos nuevos, si un dia ya existe
se queda con el valor mas reciente (upsert), nunca duplica.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "history.csv"
COLUMNS = ["date", "usd_pen"]


def load_history() -> pd.DataFrame:
    """Lee el historico. Si no existe, devuelve un DataFrame vacio."""
    if HISTORY_PATH.exists():
        df = pd.read_csv(HISTORY_PATH, parse_dates=["date"])
        return df.sort_values("date").reset_index(drop=True)
    return pd.DataFrame(columns=COLUMNS)


def upsert_many(rows: list[dict]) -> pd.DataFrame:
    """Fusiona una lista de filas nuevas con el historico y lo guarda."""
    df = load_history()
    new = pd.DataFrame(rows)
    new["date"] = pd.to_datetime(new["date"])

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        # Nos quedamos con las filas viejas cuyo dia NO viene en el lote nuevo,
        # y les sumamos todas las nuevas (el dato nuevo manda).
        df = df[~df["date"].isin(new["date"])]
        merged = pd.concat([df, new], ignore_index=True)
    else:
        merged = new

    merged = merged.sort_values("date").reset_index(drop=True)

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = merged.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(HISTORY_PATH, index=False)
    return merged
