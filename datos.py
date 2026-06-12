"""Descarga precios de CoinGecko y los procesa con pandas:
DataFrame limpio con índice de fechas, medias móviles y rendimientos."""

import os

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def _clave_api() -> str | None:
    """En local la clave vive en .env; en Streamlit Cloud, en st.secrets."""
    clave = os.getenv("COINGECKO_API_KEY")
    if clave:
        return clave
    try:
        import streamlit as st

        return st.secrets.get("COINGECKO_API_KEY")
    except Exception:
        return None


def obtener_precios(moneda: str, dias: int, divisa: str = "eur") -> pd.DataFrame:
    """Llama a market_chart y devuelve un DataFrame diario con columna 'precio'."""
    url = f"https://api.coingecko.com/api/v3/coins/{moneda}/market_chart"
    params = {"vs_currency": divisa, "days": str(dias)}
    headers = {"x-cg-demo-api-key": _clave_api()}

    respuesta = requests.get(url, params=params, headers=headers)
    respuesta.raise_for_status()  # lanza error si no es 200, mejor que fallar en silencio
    data = respuesta.json()

    df = pd.DataFrame(data["prices"], columns=["timestamp_ms", "precio"])
    # el timestamp viene en milisegundos desde 1970
    df["fecha"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df = df.set_index("fecha").drop(columns="timestamp_ms")

    # Con days<=90 la API devuelve datos horarios; nos quedamos con el
    # último precio de cada día para que "7 días" signifiquen 7 filas.
    df = df.resample("1D").last().dropna()
    return df


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """Añade medias móviles de 7 y 30 días y rendimientos diarios."""
    df = df.copy()
    df["sma_7"] = df["precio"].rolling(window=7).mean()
    df["sma_30"] = df["precio"].rolling(window=30).mean()

    # rendimiento simple: (precio_hoy - precio_ayer) / precio_ayer
    df["rendimiento"] = df["precio"].pct_change()
    # rendimiento logarítmico: ln(precio_hoy / precio_ayer); se suma en el
    # tiempo y es el estándar en finanzas cuantitativas
    df["rendimiento_log"] = np.log(df["precio"] / df["precio"].shift(1))
    return df


if __name__ == "__main__":
    df = calcular_indicadores(obtener_precios("bitcoin", 90))

    print("Forma del DataFrame:", df.shape)
    print("\nPrimeras filas (las SMA aún no existen, no hay ventana completa):")
    print(df.head(3))
    print("\nÚltimas filas:")
    print(df.tail(5))
    print("\nEstadísticas del rendimiento diario:")
    print(df["rendimiento"].describe())
