# 📈 Dashboard de mercado cripto

**🔗 Pruébala en vivo: [crypto-dashboard-samuel.streamlit.app](https://crypto-dashboard-samuel.streamlit.app)**

Web interactiva para explorar el precio histórico de criptomonedas con
indicadores técnicos calculados a mano y métricas clave. Construida con
Python, datos en vivo de la [API de CoinGecko](https://www.coingecko.com/es/api).

## Qué problema resuelve

Comparar el comportamiento de varias criptomonedas exige saltar entre
páginas, y los valores absolutos engañan (un bitcoin vale decenas de miles
de euros; un dogecoin, céntimos). Este dashboard lo reúne en un solo sitio:
precio con contexto (medias móviles, RSI), riesgo cuantificado (volatilidad
anualizada), comparación en términos relativos (base 100) y correlaciones —
con los datos exportables a CSV para seguir analizando fuera.

También es un proyecto de aprendizaje: todos los indicadores están
calculados desde cero con pandas, sin librerías de análisis técnico,
precisamente para entender qué hay dentro de cada fórmula.

## Qué hace

- **Análisis individual**: gráfico interactivo del precio con medias
  móviles de 7 y 30 días, RSI de 14 días con bandas de sobrecompra y
  sobreventa, rendimientos diarios, y métricas clave (precio actual,
  variación del periodo, volatilidad anualizada).
- **Comparador**: varias monedas normalizadas a base 100 para ver el
  rendimiento relativo, y matriz de correlación entre sus rendimientos diarios.
- **Descarga en CSV** de los datos procesados.
- Selector de moneda y rango de histórico (7–365 días).

## Estructura

| Archivo | Responsabilidad |
|---|---|
| `datos.py` | Llamada a la API, limpieza, indicadores (SMA, RSI, rendimientos) |
| `grafico.py` | Construcción de las figuras Plotly |
| `app.py` | Interfaz Streamlit: pestañas, controles, métricas y caché |

## Ejecutar en local

```bash
git clone https://github.com/echeguate/crypto-dashboard.git
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
- **Correlaciones sobre rendimientos, no sobre precios**: dos series no
  estacionarias que simplemente suben parecerían correlacionadas aunque no
  tengan relación real.
- **Base 100 en la comparación**, para que monedas con precios de distinto
  orden de magnitud sean comparables en la misma escala.
- **`@st.cache_data(ttl=600)`**: Streamlit re-ejecuta el script en cada
  interacción; la caché evita repetir llamadas y respeta el rate limit
  (además hay una pausa de 1 s entre llamadas en el comparador).
- La clave de API nunca está en el código: `.env` en local (excluido por
  `.gitignore`) y `st.secrets` en Streamlit Community Cloud.

## Qué aprendí

- A consumir una API real: estructura del JSON, autenticación con clave,
  rate limits, y que la granularidad de los datos depende del rango pedido
  (algo que no dice la primera página de la documentación y condiciona todo
  el procesado posterior).
- La diferencia entre trabajar con precios y con rendimientos, y por qué
  casi toda la estadística se hace sobre los segundos.
- Que en cripto las correlaciones entre activos grandes son altísimas
  (0,85–0,9 entre Bitcoin, Ethereum y Solana en los últimos 90 días):
  diversificar dentro de cripto diversifica menos de lo que parece.
- Que los indicadores técnicos son descriptivos: el RSI marcó "sobreventa"
  varias veces durante una caída que simplemente continuó.

## Limitaciones y mejoras posibles

- Solo uso el precio de cierre diario: la API `market_chart` no da OHLC
  completo, así que no hay velas japonesas ni rango intradía. Habría que
  combinar con el endpoint `/ohlc`.
- La lista de monedas está fijada en el código; lo correcto sería poblarla
  desde el endpoint de búsqueda de CoinGecko.
- La volatilidad anualizada asume que la del periodo elegido es
  representativa, y en cripto cambia de régimen con frecuencia.
- No hay tests automatizados; los cálculos de indicadores (RSI, SMA) son
  buenos candidatos a tests unitarios con casos conocidos.
- Con rangos largos (>90 días) y varias monedas, la carga inicial del
  comparador es lenta por la pausa entre llamadas; una caché persistente
  (en disco) la evitaría entre sesiones.
