"""
Reescribe el bloque de datos del README con la info mas reciente.

Busca los marcadores <!--DATA:START--> y <!--DATA:END--> y reemplaza todo
lo que hay entre ellos. Asi el resto del README lo editas a mano sin miedo.
"""

from __future__ import annotations

from pathlib import Path

from analyze import Stats

README_PATH = Path(__file__).resolve().parent.parent / "README.md"
START = "<!--DATA:START-->"
END = "<!--DATA:END-->"


def _arrow(change_pct: float) -> str:
    if change_pct > 0.15:
        return "🔺"
    if change_pct < -0.15:
        return "🔻"
    return "▪️"


def build_block(stats: Stats) -> str:
    """Arma el fragmento de markdown con la tabla y el grafico."""
    arrow = _arrow(stats.change_pct)
    return f"""{START}

### 💵 Dólar hoy: **S/ {stats.latest:.3f}**  {arrow} {stats.change_pct:+.2f}%

_Última actualización: {stats.latest_date} (automática vía GitHub Actions)_

| Métrica | Valor |
|---|---|
| Tipo de cambio actual | S/ {stats.latest:.4f} |
| Variación vs. día anterior | {stats.change_abs:+.4f} ({stats.change_pct:+.2f}%) |
| Tendencia | {stats.trend} |
| Mínimo (30 días) | S/ {stats.min_30d:.4f} |
| Máximo (30 días) | S/ {stats.max_30d:.4f} |
| Promedio (30 días) | S/ {stats.avg_30d:.4f} |

![Evolución USD/PEN](charts/usd_pen.png)

{END}"""


def update(stats: Stats) -> None:
    """Reemplaza el bloque de datos dentro del README."""
    text = README_PATH.read_text(encoding="utf-8")
    block = build_block(stats)

    if START in text and END in text:
        before = text.split(START)[0]
        after = text.split(END)[1]
        text = before + block + after
    else:
        # Si no hay marcadores todavia, lo pegamos al final.
        text = text.rstrip() + "\n\n" + block + "\n"

    README_PATH.write_text(text, encoding="utf-8")
