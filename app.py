"""Dashboard de mercado cripto: elige moneda y rango, ve precio,
indicadores y métricas clave. Ejecutar con: streamlit run app.py"""

import numpy as np
import streamlit as st

from datos import calcular_indicadores, obtener_comparacion, obtener_precios
from grafico import (
    crear_grafico_comparacion,
    crear_grafico_precio,
    crear_grafico_rsi,
    crear_mapa_correlacion,
)

MONEDAS = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]

st.set_page_config(page_title="Dashboard cripto", page_icon="📈", layout="wide")

st.title("📈 Dashboard de mercado cripto")

# ---- Menú lateral: controles del usuario ----
moneda = st.sidebar.selectbox("Moneda", MONEDAS)
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


@st.cache_data(ttl=600)
def cargar_comparacion(monedas: tuple[str, ...], dias: int):
    return obtener_comparacion(list(monedas), dias)


tab_analisis, tab_comparar = st.tabs(["📊 Análisis individual", "⚖️ Comparar monedas"])

# ================= Pestaña 1: análisis de una moneda =================
with tab_analisis:
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

    # ---- RSI ----
    st.subheader("RSI — Índice de fuerza relativa (14 días)")
    st.plotly_chart(crear_grafico_rsi(df), use_container_width=True)
    st.caption(
        "El RSI compara la magnitud media de subidas y bajadas recientes. "
        "Las bandas de 70/30 son convenciones descriptivas, no señales infalibles."
    )

    # ---- Rendimientos diarios ----
    with st.expander("Ver rendimientos diarios"):
        st.bar_chart(df["rendimiento"], height=200)
        st.caption(
            "Rendimiento simple diario. Fíjate en que el ruido domina: "
            "los indicadores describen el pasado, no predicen el futuro."
        )

    # ---- Descarga ----
    st.download_button(
        "⬇️ Descargar datos en CSV",
        data=df.to_csv().encode("utf-8"),
        file_name=f"{moneda}_{dias}dias.csv",
        mime="text/csv",
    )

# ================= Pestaña 2: comparador =================
with tab_comparar:
    seleccion = st.multiselect(
        "Monedas a comparar",
        MONEDAS,
        default=["bitcoin", "ethereum"],
    )
    if len(seleccion) < 2:
        st.info("Elige al menos dos monedas para comparar.")
    else:
        try:
            # tuple porque cache_data necesita argumentos inmutables (hashables)
            df_comp = cargar_comparacion(tuple(seleccion), dias)
        except Exception as e:
            st.error(f"No se pudieron cargar los datos de la API: {e}")
            st.stop()

        st.subheader(f"Evolución comparada — últimos {dias} días")
        st.plotly_chart(crear_grafico_comparacion(df_comp), use_container_width=True)
        st.caption(
            "Cada serie parte de 100 al inicio del periodo: lo que se compara "
            "es el rendimiento relativo, no el precio absoluto."
        )

        st.subheader("Correlación entre rendimientos diarios")
        st.plotly_chart(crear_mapa_correlacion(df_comp), use_container_width=True)
        st.caption(
            "1 = se mueven igual, 0 = independientes, −1 = opuestas. "
            "Se calcula sobre rendimientos, no sobre precios: dos series que "
            "suben a la vez parecerían correlacionadas aunque no lo estén."
        )
