"""Gráfico interactivo con Plotly: precio + medias móviles de 7 y 30 días."""

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


if __name__ == "__main__":
    moneda = "bitcoin"
    df = calcular_indicadores(obtener_precios(moneda, 90))
    fig = crear_grafico_precio(df, f"{moneda.capitalize()} — últimos 90 días")
    fig.write_html("grafico.html")
    print("Gráfico guardado en grafico.html")
