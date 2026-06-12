"""Script exploratorio: llama al endpoint market_chart de CoinGecko
y muestra la estructura del JSON que devuelve, antes de procesarlo."""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()  # carga las variables de .env
API_KEY = os.getenv("COINGECKO_API_KEY")

moneda = "bitcoin"
url = f"https://api.coingecko.com/api/v3/coins/{moneda}/market_chart"
params = {"vs_currency": "eur", "days": "90"}
headers = {"x-cg-demo-api-key": API_KEY}

respuesta = requests.get(url, params=params, headers=headers)
print("Código de estado HTTP:", respuesta.status_code)

data = respuesta.json()

print("\nClaves del JSON:", list(data.keys()))

print("\nPrimeros 3 elementos de 'prices':")
for item in data["prices"][:3]:
    print(" ", item)

print("\nNúmero de puntos de precio:", len(data["prices"]))

# El timestamp viene en milisegundos desde 1970 (época Unix)
ts_ms, precio = data["prices"][0]
fecha = datetime.fromtimestamp(ts_ms / 1000)
print(f"\nEl primer punto: timestamp {ts_ms} = {fecha} -> {precio:.2f} EUR")

ts_ms, precio = data["prices"][-1]
fecha = datetime.fromtimestamp(ts_ms / 1000)
print(f"El último punto:  timestamp {ts_ms} = {fecha} -> {precio:.2f} EUR")
