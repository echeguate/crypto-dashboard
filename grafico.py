"""Gráficos interactivos con Plotly: precio con medias móviles, RSI,
comparación entre monedas y mapa de correlaciones."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from datos import calcular_indicadores, obtener_precios


def crear_grafico_precio(df, titulo: str, divisa: str = "EUR") -> go.Figure:
    """Devuelve una figura con el precio y las dos SMA superpuestas."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["precio"],
        name="Precio", line=dict(color="#636efa", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["sma_7"],
        name="Media móvil 7 días", line=dict(color="#ef553b", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["sma_30"],
        name="Media móvil 30 días", line=dict(color="#00cc96", width=1.5),
    ))

    fig.update_layout(
        title=titulo,
        yaxis_title=f"Precio ({divisa})",
        hovermode="x unified",  # el hover muestra las 3 series a la vez
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        template="plotly_white",
    )
    return fig


def crear_grafico_rsi(df) -> go.Figure:
    """RSI con las bandas convencionales de sobrecompra (70) y sobreventa (30)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["rsi"],
        name="RSI (14 días)", line=dict(color="#ab63fa", width=1.5),
    ))
    fig.add_hline(y=70, line_dash="dash", line_color="#ef553b", opacity=0.5,
                  annotation_text="sobrecompra (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="#00cc96", opacity=0.5,
                  annotation_text="sobreventa (30)")
    fig.update_layout(
        yaxis=dict(title="RSI", range=[0, 100]),
        height=280,
        margin=dict(t=30, b=20),
        template="plotly_white",
        showlegend=False,
    )
    return fig


def crear_grafico_comparacion(df_precios: pd.DataFrame) -> go.Figure:
    """Compara monedas en base 100: cada serie parte de 100 el primer día,
    así se ve el rendimiento relativo aunque los precios difieran en órdenes
    de magnitud (un bitcoin vale ~55.000 €, un dogecoin céntimos)."""
    base_100 = df_precios / df_precios.iloc[0] * 100
    fig = go.Figure()
    for moneda in base_100.columns:
        fig.add_trace(go.Scatter(
            x=base_100.index, y=base_100[moneda], name=moneda.capitalize(),
        ))
    fig.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.5)
    fig.update_layout(
        yaxis_title="Evolución (base 100 = inicio del periodo)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        template="plotly_white",
    )
    return fig


def crear_mapa_correlacion(df_precios: pd.DataFrame) -> go.Figure:
    """Correlación entre los rendimientos diarios (no entre precios: dos
    series que solo suben parecerían correlacionadas aunque no lo estén)."""
    correlacion = df_precios.pct_change().corr().round(2)
    fig = px.imshow(
        correlacion,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        aspect="auto",
    )
    fig.update_layout(height=400, margin=dict(t=30, b=20))
    return fig


if __name__ == "__main__":
    moneda = "bitcoin"
    df = calcular_indicadores(obtener_precios(moneda, 90))
    fig = crear_grafico_precio(df, f"{moneda.capitalize()} — últimos 90 días")
    fig.write_html("grafico.html")
    print("Gráfico guardado en grafico.html")
