"""
Exporta el dato mas reciente a data/latest.json.

Gracias a esto el repo funciona como una mini-API gratuita: cualquier app
puede consumir el JSON crudo desde raw.githubusercontent.com sin servidor,
sin API key y siempre actualizado por el propio pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

from analyze import Stats

LATEST_PATH = Path(__file__).resolve().parent.parent / "data" / "latest.json"


def write_latest(stats: Stats) -> Path:
    """Escribe el resumen mas reciente como JSON y devuelve la ruta."""
    payload = {
        "pair": "USD/PEN",
        "source": "BCRP (serie PD04640PD, TC venta)",
        "date": stats.latest_date,
        "rate": stats.latest,
        "change_abs": stats.change_abs,
        "change_pct": stats.change_pct,
        "trend": stats.trend,
        "stats_30d": {
            "min": stats.min_30d,
            "max": stats.max_30d,
            "avg": stats.avg_30d,
            "volatility": stats.volatility_30d,
        },
    }
    LATEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return LATEST_PATH
