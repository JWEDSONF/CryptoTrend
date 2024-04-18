import requests
import streamlit as st
import pandas as pd
import base64
from datetime import datetime, timedelta

# Calcular a data e hora futura (7 meses após a data atual)
data_futura = datetime.utcnow() + timedelta(days=550*30)

# Converter a data e hora futura em um timestamp Unix (em milissegundos)
timestamp = int(data_futura.timestamp() * 1000)

# Criar a chave API no formato desejado
api_key = f"-b31e-c547-d299-b6d07b7631aba2c903cc|28{timestamp}7"

# Codificar a chave API em Base64
api_key_base64 = base64.b64encode(api_key.encode()).decode('utf-8')
# URL da API
url = 'https://coinank.com/api/instruments/agg?page=1&size=50&sortBy=&baseCoin=&isFollow=false'

# Cabeçalhos conforme capturados no navegador
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    #'Coinank-Apikey': 'LWIzMWUtYzU0Ny1kMjk5LWI2ZDA3Yjc2MzFhYmEyYzkwM2NjfDI4MTcyNDI4MTk4NzM3NDc=',
    'Coinank-Apikey': api_key_base64,
    'Referer': 'https://coinank.com/',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Kl-Saas-Ajax-Request': 'Ajax_Request'
}


cookies = {
    'i18n_redirected': 'en',
    '_ga_BDEPVNN1SX': 'GS1.1.1706120315.1.0.1706120315.0.0.0',
    '_ga': 'GA1.1.127937836.1706120315'
}

@st.cache_data(ttl=120)
def obter_dados_api(url):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.json()['data']['list']
    else:
        st.error(f'Erro ao carregar dados da API: {response.status_code}')
        return []


@st.cache_data(ttl=120)
def obter_e_processar_dados_tecnicos(api_url):
    
    response = requests.get(api_url)
    if response.status_code == 200:
        crypto_data = response.json()['data']
        df_tec = pd.DataFrame(crypto_data)
        return df_tec
    else:
        st.error(f'Erro ao carregar dados técnicos da API: {response.status_code}')
        return pd.DataFrame()

