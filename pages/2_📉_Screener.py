import streamlit as st
import pandas as pd
import numpy as np
from data_processing import processar_dados
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_loader import load_data
from table_formatters import colunas_dolar, colunas_percentual, dollar_formatter, percent_formatter
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

st.set_page_config(layout="wide")
st.title('Screener')

if 'selected_coin' not in st.session_state:
    st.session_state['selected_coin'] = None

if 'selected_row_indices' not in st.session_state:
    st.session_state['selected_row_indices'] = []

# Inicializar ou carregar o estado da sessão
if 'filter_option' not in st.session_state:
    st.session_state['filter_option'] = 'Default'

if 'custom_columns' not in st.session_state:
    st.session_state['custom_columns'] = []

# Carregamento e processamento de dados das APIs
with st.spinner('Loading data...'):
    df_final = load_data()


def calcular_metricas(df):
    media_openInterestCh24 = df['Open Interest 24h'].mean()*100
    media_longShortPerson = df['Long Short Ratio'].mean()
    media_lsPersonChg4h = df['LSR 4h'].mean()*100
    fundingrate = df['Funding Rate'].mean()*1000
    soma_openInterest = df['Open Interest'].sum()
    soma_volume = df['Volume 24h'].sum()
    soma_liquidationH24 = df['Liquidation 24h'].sum()
    soma_liquidationH1 = df['Liquidation 1h'].sum()
    return media_openInterestCh24, soma_openInterest, soma_volume, soma_liquidationH24, soma_liquidationH1, media_longShortPerson, media_lsPersonChg4h, fundingrate

# Função para exibir métricas
def exibir_metricas(media_openInterestCh24, soma_openInterest, soma_volume, soma_liquidationH24, soma_liquidationH1, media_longShortPerson, media_lsPersonChg4h, fundingrate):
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric(label="Total Open Interest", value="${:,.0f}".format(soma_openInterest), delta="{:.1f}%".format(media_openInterestCh24))
    with col2:
        st.metric(label="Volume 24h", value="${:,.0f}".format(soma_volume))
    with col3:
        st.metric(label="Liquidation 24h", value="${:,.0f}".format(soma_liquidationH24))
    with col4:
        st.metric(label="Liquidation 1h", value="${:,.0f}".format(soma_liquidationH1))
    with col5:
        st.metric(label="Long Short Ratio", value="{:,.2f}".format(media_longShortPerson), delta="{:.2f}%".format(media_lsPersonChg4h)) 
    with col6:
        st.metric(label="Funding Rate", value="{:.2f}%".format(fundingrate))


valores_metricas = calcular_metricas(df_final)
exibir_metricas(*valores_metricas)


# Função JavaScript para renderizar a célula como HTML
render = JsCode("""
class ThumbnailRenderer {
    init(params) {
        this.eGui = document.createElement('div');
        this.eGui.innerHTML = params.value;
    }
    getGui() {
        return this.eGui;
    }
}
""")


filter_option = st.radio(
    "Choose the column filter.:",
    ('Default', 'Performance', 'Formulas', 'Technical indicators', 'Open Interest', 'Longs vs Shorts', 'Liquidations', 'Funding Rate', 'Volume', 'Market Cap', 'Custom'),
    horizontal=True
)
st.session_state['filter_option'] = filter_option

# Mapeamento das colunas para cada filtro
filtro_colunas = {
    'Default': ['Coin', 'priceUSD', 'Open Interest', 'Open Interest 24h', 'OI/Market Cap', 'Short-Term OI Trend', 'Long-Term OI Trend', 'Top Trader Sentiment', 'rsi24h', 'bb_24h', 'macd_24h'],
    'Open Interest': ['Coin', 'priceUSD', 'Open Interest', 'Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m', 'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h', 'Open Interest 2d', 'Open Interest 3d', 'Open Interest 7d'],
    'Formulas': ['Coin', 'priceUSD', 'OI/Market Cap', 'Short-Term OI Trend', 'Long-Term OI Trend', 'Top Trader Sentiment', 'Funding Rate Risk', 'Liquidations 24h/OI', 'Long Liquidations/OI', 'Short Liquidations/OI', 'Funding Rate'],
    'Performance': ['Coin', 'priceUSD', 'Volume Change 24h', 'Open Interest 5m'],
    'Technical indicators': ['Coin', 'priceUSD', 'rsi5min', 'rsi15min', 'rsi30min', 'rsi1h', 'rsi2h', 'rsi4h', 'rsi24h', 'macd_5min', 'macd_15min', 'macd_30min', 'macd_1h', 'macd_2h', 'macd_4h', 'macd_24h', 'bb_5min', 'bb_15min', 'bb_30min', 'bb_1h', 'bb_2h', 'bb_4h', 'bb_24h'],
    'Liquidations': ['Coin', 'priceUSD', 'Liquidation 1h', 'Liquidation Long 1h', 'Liquidation Short 1h', 'Liquidation 4h', 'Liquidation Long 4h', 'Liquidation Short 4h', 'Liquidation 12h', 'Liquidation Long 12h', 'Liquidation Short 12h', 'Liquidation 24h', 'Liquidation Long 24h', 'Liquidation Short 24h'],
    'Funding Rate': ['Coin', 'priceUSD', 'Funding Rate'],
    'Volume': ['Coin', 'priceUSD', 'Volume 24h', 'Volume Change 24h', 'Buy Volume 5m', 'Sell Volume 5m'],
    'Custom': []
    # 'All': ['Coin'] + df_final.columns.tolist()
}


# Selecionar colunas baseado no filtro escolhido
colunas_selecionadas = filtro_colunas[filter_option]


if filter_option == 'Custom':
    colunas_selecionadas = st.multiselect(
        'Choose the columns:',
        df_final.columns.tolist(),
        default=st.session_state['custom_columns']
    )
    st.session_state['custom_columns'] = colunas_selecionadas
else:
    colunas_selecionadas = filtro_colunas[filter_option]


# Adicionar 'Coin' e 'qc_key' se não estiverem presentes
if 'Coin' not in colunas_selecionadas:
    colunas_selecionadas = ['Coin'] + colunas_selecionadas
# if 'qc_key' not in colunas_selecionadas:
#     colunas_selecionadas.append('Crypto')

# Filtrar o DataFrame com base nas colunas selecionadas
df_filtrado = df_final[colunas_selecionadas]

selected_coin = st.session_state['selected_coin']
if selected_coin:
    selected_row_indices = df_final.index[df_final['Coin'] == selected_coin].tolist()
else:
    selected_row_indices = []


# Configuração do Ag-Grid
gb = GridOptionsBuilder.from_dataframe(df_final[colunas_selecionadas])
for col in colunas_selecionadas:
    gb.configure_column(col, autoSize=True)
gb.configure_column("Coin", pinned="left", cellRenderer=render, filterable=False, suppress_csv_export=True, suppress_excel_export=True)
# Configurar estilos de célula para vários campos
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum')
#gb.configure_selection('single', use_checkbox=True, rowMultiSelectWithClick=False, suppressRowDeselection=False, pre_selected_rows=selected_row_indices)
gb.configure_side_bar()

for coluna in colunas_dolar:
    if coluna in colunas_selecionadas:
        gb.configure_column(coluna, cellRenderer=dollar_formatter)

for coluna in colunas_percentual:
    if coluna in colunas_selecionadas:
        gb.configure_column(coluna, cellRenderer=percent_formatter)

if 'selected_row_index' in st.session_state and st.session_state['selected_row_index'] is not None:
    selected_row_indices = [st.session_state['selected_row_index']]
else:
    selected_row_indices = []


gb.configure_selection('single', use_checkbox=True, rowMultiSelectWithClick=False, suppressRowDeselection=False, pre_selected_rows=selected_row_indices)
grid_options = gb.build()

# Renderizar o AgGrid
selection = AgGrid(
    df_filtrado,
    gridOptions=grid_options,
    theme='streamlit',
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True,
    height=600,
    width='100%',
    data_return_mode=DataReturnMode.AS_INPUT,
    update_mode=GridUpdateMode.MODEL_CHANGED
)


# Atualizar o session_state com a nova seleção
if selection and selection['selected_rows']:
    selected_row = selection['selected_rows'][0]
    new_selected_coin = selected_row['Coin']
    new_selected_coin_index = df_final.index[df_final['Coin'] == new_selected_coin].tolist()[0]

    # Atualizar o session_state apenas se a seleção mudou
    if new_selected_coin != st.session_state['selected_coin']:
        st.session_state['selected_coin'] = new_selected_coin
        st.session_state['selected_coin_index'] = new_selected_coin_index

        # Atualizar o símbolo da moeda selecionada
        st.session_state['selected_symbol'] = df_final.loc[df_final['Coin'] == new_selected_coin, 'Crypto'].values[0]
else:
    st.session_state['selected_coin'] = None
    st.session_state['selected_coin_index'] = None

# Exibindo a mensagem logo abaixo da tabela AgGrid
if st.session_state.get('selected_coin'):
    # Colocando apenas o nome da moeda em negrito
    st.markdown(f"You have selected the coin: **{st.session_state.get('selected_symbol', 'Unknown')}**")


# Agora exiba as métricas
if st.session_state.get('selected_coin'):
    df_selected = df_final[df_final['Coin'] == st.session_state['selected_coin']]
    valores_metricas = calcular_metricas(df_selected)
    exibir_metricas(*valores_metricas)


# Exibir o widget do TradingView com base na seleção
if st.session_state['selected_coin']:
    st.session_state['selected_symbol'] = df_final.loc[df_final['Coin'] == st.session_state['selected_coin'], 'symbol'].values[0]
    tradingview_html = f"""
        <div class="tradingview-widget-container" style="width: 100%;">
            <div id="tradingview_7b9c5" style="width: 100%; height: 600px;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget(
            {{
                "autosize": true,
                "symbol": "{st.session_state['selected_symbol']}",
                "interval": "240",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "br",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_7b9c5"
            }});
            </script>
        </div>
        """
    st.components.v1.html(tradingview_html, height=600)
else:
    st.warning("Select a cryptocurrency to view the chart")


