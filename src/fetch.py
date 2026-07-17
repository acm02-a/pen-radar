"""
Obtiene el tipo de cambio del dolar (venta) desde la API del BCRP.

Fuente: Banco Central de Reserva del Peru — serie PD04640PD
("Tipo de cambio - TC Sistema bancario SBS (S/ por US$) - Venta"), diaria.
Es dato oficial, gratuito y sin API key.

La API devuelve las fechas en espanol ("01.May.24"), asi que las convertimos
a formato ISO (AAAA-MM-DD) antes de usarlas.
"""

from __future__ import annotations

import datetime as dt

import requests

BCRP_SERIE = "PD04640PD"
BASE_URL = (
    "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
    "{serie}/json/{start}/{end}/ing"
)
TIMEOUT = 30

# El BCRP abrevia los meses; el endpoint /ing los da en ingles (Jan, Feb...) y
# el /esp en espanol (Ene, Abr, Ago, Set...). Aceptamos ambos por seguridad.
_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    "Ene": 1, "Abr": 4, "Ago": 8, "Set": 9, "Dic": 12,
}


def _parse_bcrp_date(name: str) -> str:
    """Convierte '01.May.24' -> '2024-05-01'."""
    day, mon, year = name.split(".")
    return dt.date(2000 + int(year), _MONTHS[mon], int(day)).isoformat()


def fetch_window(days: int = 180) -> list[dict]:
    """
    Descarga los ultimos `days` dias de la serie y devuelve una lista de
    filas {'date': 'AAAA-MM-DD', 'usd_pen': float}, ya sin los dias 'n.d.'
    (feriados/fines de semana que el BCRP no publica).
    """
    end = dt.date.today()
    start = end - dt.timedelta(days=days)
    url = BASE_URL.format(
        serie=BCRP_SERIE, start=start.isoformat(), end=end.isoformat()
    )

    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    periods = resp.json().get("periods", [])

    rows: list[dict] = []
    for p in periods:
        raw = p["values"][0]
        if raw in ("n.d.", "", None):  # dia sin cotizacion
            continue
        rows.append({"date": _parse_bcrp_date(p["name"]), "usd_pen": round(float(raw), 4)})

    if not rows:
        raise RuntimeError("El BCRP no devolvio ningun dato en el rango pedido.")
    return rows


if __name__ == "__main__":
    data = fetch_window(30)
    print(f"{len(data)} dias. Ultimo: {data[-1]}")
