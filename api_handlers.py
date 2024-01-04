import requests
import streamlit as st
import pandas as pd

@st.cache_data(ttl=90)
def obter_dados_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['list']
    else:
        st.error(f'Erro ao carregar dados da API: {response.status_code}')
        return []


@st.cache_data(ttl=90)
def obter_e_processar_dados_tecnicos(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        crypto_data = response.json()['data']
        df_tec = pd.DataFrame(crypto_data)
        return df_tec
    else:
        st.error(f'Erro ao carregar dados técnicos da API: {response.status_code}')
        return pd.DataFrame()

