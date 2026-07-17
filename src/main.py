"""
Punto de entrada del pipeline: junta todos los pasos.

    fetch  ->  storage  ->  analyze  ->  chart  ->  readme

Se corre con:  python src/main.py
Si la API no responde, el pipeline NO borra nada: reutiliza el historico ya
guardado para regenerar el grafico y el README.
"""

from __future__ import annotations

import sys

import analyze
import chart
import export
import readme
import storage
from fetch import fetch_window


def run() -> int:
    print("[1/4] Descargando tipo de cambio del BCRP...")
    try:
        rows = fetch_window(days=180)
        print(f"      OK: {len(rows)} dias recibidos. Ultimo: {rows[-1]['date']} = S/ {rows[-1]['usd_pen']:.4f}")
        df = storage.upsert_many(rows)
    except Exception as exc:  # red caida, API abajo, etc.
        print(f"      AVISO: no se pudo obtener dato nuevo: {exc}")
        print("      Uso el historico existente para regenerar salidas.")
        df = storage.load_history()
        if df.empty:
            print("      ERROR: no hay historico y no hay red. Nada que hacer.")
            return 1

    print("[2/5] Calculando estadisticas...")
    stats = analyze.compute(df)

    print("[3/5] Generando grafico...")
    chart.render(df)

    print("[4/5] Exportando latest.json...")
    export.write_latest(stats)

    print("[5/5] Actualizando README...")
    readme.update(stats)

    print(f"LISTO. {len(df)} dias en el historico. Dolar: S/ {stats.latest:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
