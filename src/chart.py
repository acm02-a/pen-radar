"""
Genera el grafico de la evolucion del dolar y lo guarda como PNG.

Se usa el backend "Agg" de matplotlib para poder correr en un servidor sin
pantalla (como el runner de GitHub Actions).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin interfaz grafica; imprescindible en CI
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

CHART_PATH = Path(__file__).resolve().parent.parent / "charts" / "usd_pen.png"


def render(df: pd.DataFrame, days: int = 90) -> Path:
    """Dibuja los ultimos `days` dias de USD/PEN y devuelve la ruta del PNG."""
    df = df.sort_values("date").tail(days).copy()
    df["date"] = pd.to_datetime(df["date"])

    x = df["date"].values
    y = df["usd_pen"].values
    baseline = float(df["usd_pen"].min())

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=130)
    ax.plot(x, y, linewidth=2.2, color="#2563eb", marker="o", markersize=3)
    ax.fill_between(x, y, baseline, alpha=0.08, color="#2563eb")

    ax.set_title("USD / PEN  —  tipo de cambio venta (BCRP)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Soles por dolar")
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)

    if len(df) > 0:
        last = df.iloc[-1]
        ax.annotate(
            f"S/ {last['usd_pen']:.3f}",
            xy=(last["date"], last["usd_pen"]),
            xytext=(6, 6),
            textcoords="offset points",
            fontweight="bold",
            color="#2563eb",
        )

    fig.autofmt_xdate()
    fig.tight_layout()

    CHART_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHART_PATH)
    plt.close(fig)
    return CHART_PATH
