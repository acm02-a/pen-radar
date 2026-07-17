"""
Calcula estadisticas simples sobre el historico del dolar.

Nada de magia: variacion diaria, minimo/maximo/promedio de los ultimos
30 dias y una etiqueta de tendencia. Es lo que un lector quiere ver de un
vistazo.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Stats:
    latest: float
    latest_date: str
    change_abs: float  # variacion vs el dato anterior (en soles)
    change_pct: float  # variacion vs el dato anterior (en %)
    min_30d: float
    max_30d: float
    avg_30d: float
    volatility_30d: float  # desviacion estandar de los ultimos 30 dias
    trend: str  # "subiendo", "bajando" o "estable"


def _trend_label(change_pct: float) -> str:
    if change_pct > 0.15:
        return "subiendo"
    if change_pct < -0.15:
        return "bajando"
    return "estable"


def compute(df: pd.DataFrame, col: str = "usd_pen") -> Stats:
    """Devuelve las estadisticas de la columna pedida (por defecto USD/PEN)."""
    if df.empty:
        raise ValueError("El historico esta vacio, no hay nada que analizar.")

    df = df.sort_values("date").reset_index(drop=True)
    latest = float(df[col].iloc[-1])
    latest_date = pd.to_datetime(df["date"].iloc[-1]).strftime("%Y-%m-%d")

    if len(df) >= 2:
        prev = float(df[col].iloc[-2])
        change_abs = latest - prev
        change_pct = (change_abs / prev) * 100 if prev else 0.0
    else:
        change_abs = 0.0
        change_pct = 0.0

    last_30 = df.tail(30)[col]
    # Con una sola observacion la desviacion estandar es NaN; usamos 0.
    vol = float(last_30.std()) if len(last_30) >= 2 else 0.0
    return Stats(
        latest=round(latest, 4),
        latest_date=latest_date,
        change_abs=round(change_abs, 4),
        change_pct=round(change_pct, 3),
        min_30d=round(float(last_30.min()), 4),
        max_30d=round(float(last_30.max()), 4),
        avg_30d=round(float(last_30.mean()), 4),
        volatility_30d=round(vol, 4),
        trend=_trend_label(change_pct),
    )
