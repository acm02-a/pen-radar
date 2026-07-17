"""
Tests del pipeline (sin tocar la red).

Se pueden correr de dos formas:
    pytest                      # si tienes pytest instalado
    python tests/test_pipeline.py   # sin instalar nada extra
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Permitimos importar los modulos de src/ sin instalar el paquete.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import analyze  # noqa: E402
import storage  # noqa: E402
from fetch import _parse_bcrp_date  # noqa: E402


def test_parse_fecha_ingles():
    assert _parse_bcrp_date("01.Jul.26") == "2026-07-01"


def test_parse_fecha_espanol():
    # setiembre en espanol lo abrevian "Set"
    assert _parse_bcrp_date("15.Set.24") == "2024-09-15"


def test_variacion_diaria():
    df = pd.DataFrame(
        {"date": pd.to_datetime(["2026-07-01", "2026-07-02"]), "usd_pen": [3.40, 3.44]}
    )
    stats = analyze.compute(df)
    assert stats.latest == 3.44
    assert round(stats.change_abs, 2) == 0.04
    assert stats.trend == "subiendo"


def test_upsert_no_duplica_dias(tmp_path=None):
    # Redirigimos el CSV a un archivo temporal para no ensuciar data/.
    original = storage.HISTORY_PATH
    tmp = Path(__file__).resolve().parent / "_tmp_history.csv"
    storage.HISTORY_PATH = tmp
    try:
        storage.upsert_many([{"date": "2026-07-01", "usd_pen": 3.40}])
        storage.upsert_many([{"date": "2026-07-01", "usd_pen": 3.99}])  # mismo dia
        df = storage.load_history()
        assert len(df) == 1  # no se duplico
        assert float(df["usd_pen"].iloc[0]) == 3.99  # gano el mas reciente
    finally:
        storage.HISTORY_PATH = original
        if tmp.exists():
            tmp.unlink()


if __name__ == "__main__":
    passed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
            passed += 1
    print(f"\n{passed} tests OK")
