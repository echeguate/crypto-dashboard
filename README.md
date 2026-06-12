# 📈 Dashboard de mercado cripto

**🔗 Pruébala en vivo: [crypto-dashboard-samuel.streamlit.app](https://crypto-dashboard-samuel.streamlit.app)**

Web interactiva para explorar el precio histórico de criptomonedas con
indicadores técnicos calculados a mano y métricas clave. Construida con
Python, datos en vivo de la [API de CoinGecko](https://www.coingecko.com/es/api).

## Qué hace

- Selector de moneda (Bitcoin, Ethereum, Solana, Cardano, Dogecoin) y rango
  de histórico (7–365 días).
- Gráfico interactivo del precio con **medias móviles de 7 y 30 días**
  calculadas con pandas (`rolling().mean()`), sin librerías de indicadores.
- Métricas clave: precio actual, variación del periodo y **volatilidad
  anualizada** (desviación típica de los rendimientos logarítmicos diarios × √365).
- Vista de rendimientos diarios, que ilustra por qué el ruido domina en las
  series financieras: los indicadores describen, no predicen.

## Estructura

| Archivo | Responsabilidad |
|---|---|
| `datos.py` | Llamada a la API, limpieza y cálculo de indicadores con pandas |
| `grafico.py` | Construcción de la figura Plotly |
| `app.py` | Interfaz Streamlit: controles, métricas y caché |

## Ejecutar en local

```bash
git clone <url-de-este-repo>
cd crypto-dashboard
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz con tu clave (gratuita) de CoinGecko:

```
COINGECKO_API_KEY=tu_clave
```

Y lanza la app:

```bash
streamlit run app.py
```

## Decisiones técnicas

- **Remuestreo a diario**: con `days ≤ 90` la API devuelve datos horarios;
  se toma el cierre de cada día para que una ventana de 7 signifique 7 días.
- **Rendimientos logarítmicos** para la volatilidad, porque son aditivos en
  el tiempo y permiten anualizar con √365.
- **`@st.cache_data(ttl=600)`**: Streamlit re-ejecuta el script en cada
  interacción; la caché evita repetir llamadas y respeta el rate limit.
- La clave de API nunca está en el código: `.env` en local (excluido por
  `.gitignore`) y `st.secrets` en Streamlit Community Cloud.
