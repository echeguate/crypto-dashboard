"""Dashboard de mercado cripto: elige moneda y rango, ve precio,
indicadores y métricas clave. Ejecutar con: streamlit run app.py"""

import numpy as np
import streamlit as st

from datos import calcular_indicadores, obtener_precios
from grafico import crear_grafico_precio

st.set_page_config(page_title="Dashboard cripto", page_icon="📈", layout="wide")

st.title("📈 Dashboard de mercado cripto")

# ---- Menú lateral: controles del usuario ----
moneda = st.sidebar.selectbox(
    "Moneda",
    ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"],
)
dias = st.sidebar.slider("Días de histórico", min_value=7, max_value=365, value=90)
st.sidebar.caption(
    "Datos de [CoinGecko](https://www.coingecko.com). "
    "Con más de 90 días la resolución pasa a ser diaria."
)


# Streamlit re-ejecuta TODO el script con cada interacción; la caché evita
# repetir la misma llamada a la API (y agotar el rate limit). Expira a los 10 min.
@st.cache_data(ttl=600)
def cargar_datos(moneda: str, dias: int):
    return calcular_indicadores(obtener_precios(moneda, dias))


try:
    df = cargar_datos(moneda, dias)
except Exception as e:
    st.error(f"No se pudieron cargar los datos de la API: {e}")
    st.stop()

# ---- Métricas clave ----
precio_actual = df["precio"].iloc[-1]
variacion_dia = df["rendimiento"].iloc[-1]
variacion_periodo = df["precio"].iloc[-1] / df["precio"].iloc[0] - 1
# volatilidad anualizada: std de rendimientos log diarios * raíz de 365
volatilidad = df["rendimiento_log"].std() * np.sqrt(365)

col1, col2, col3 = st.columns(3)
col1.metric(
    "Precio actual",
    f"{precio_actual:,.2f} €",
    delta=f"{variacion_dia:+.2%} hoy",
)
col2.metric(f"Variación en {dias} días", f"{variacion_periodo:+.2%}")
col3.metric(
    "Volatilidad anualizada",
    f"{volatilidad:.1%}",
    help="Desviación típica de los rendimientos logarítmicos diarios × √365. "
    "Mide cuánto se mueve el precio, no hacia dónde.",
)

# ---- Gráfico principal ----
fig = crear_grafico_precio(df, f"{moneda.capitalize()} — últimos {dias} días")
st.plotly_chart(fig, use_container_width=True)

# ---- Rendimientos diarios ----
with st.expander("Ver rendimientos diarios"):
    st.bar_chart(df["rendimiento"], height=200)
    st.caption(
        "Rendimiento simple diario. Fíjate en que el ruido domina: "
        "los indicadores describen el pasado, no predicen el futuro."
    )
