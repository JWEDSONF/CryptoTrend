import requests
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r'C:\Users\João Wedson\Firebase\key.json')
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Obtenção de Dados da API
api_url = "https://quantifycrypto.com/api/v1.0/common/init-table?currency=USD&fields=rank,symbol_name,price_usd,marketcap,volume24h,price5min,price15min,price1h,price2h,price4h,price24h,price1week,price2week,price30day,price_year_to_date,price1year,macd_5min,macd_15min,macd_30min,macd_1h,macd_2h,macd_4h,macd_24h,rsi5min,rsi15min,rsi30min,rsi1h,rsi2h,rsi4h,rsi24h,bb_5min,bb_15min,bb_30min,bb_1h,bb_2h,bb_4h,bb_24h,qc_key&exchange=binance,coinbase,kucoin,huobi,upbit,gate,cryptodotcom"
response = requests.get(api_url)
data = response.json()
crypto_data = data['data']
df_tec = pd.DataFrame(crypto_data)

# Enviando Dados para o Firebase
for index, row in df_tec.iterrows():
    doc_ref = db.collection("screener_derivative").document(str(index))
    doc_ref.set(row.to_dict())