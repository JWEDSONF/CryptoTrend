import streamlit as st
import pandas as pd
import numpy as np
from data_processing import processar_dados
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_loader import load_data
from table_formatters import colunas_dolar, colunas_percentual, colunas_percentual2, dollar_formatter, percent_formatter, percent_formatter2
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode


st.set_page_config(
    page_title="Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://forms.gle/a9X3vpug4AXGV3JP7",
        'About': """
            **Screener: Your Gateway to Cryptocurrency Insights**

            The Screener is an advanced, user-friendly tool designed to provide in-depth analysis and insights into the dynamic world of cryptocurrencies. It's a robust platform ideal for investors and enthusiasts seeking comprehensive market data and trends.

            Key Features:
            - **Detailed Table-Format Analysis:** Dive deep into a wide array of market data with ease, thanks to our intuitive filtering system.
            - **Real-Time Data Visualization:** Quickly visualize detailed charts for each cryptocurrency selected in the table, offering insights at a glance.
            - **Customizable Filters:** Tailor your analysis by applying various filters, focusing on the data that matters most to you.
            - **Market Trend Overview:** Gain a holistic view of the market trends, helping you make informed decisions based on the latest market movements.

            Our Screener is more than just a data aggregation tool; it's a comprehensive solution for anyone looking to enhance their understanding of the cryptocurrency market, from casual observers to serious investors.
            
            Dominando Cripto - All rights reserved.
        """
    }
)

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

# Função para atualizar as colunas selecionadas no estado da sessão
def update_custom_columns():
    st.session_state['custom_columns'] = st.session_state['temp_custom_columns']


# Carregamento e processamento de dados das APIs
with st.spinner('Loading data...'):
    df_final = load_data()

st.sidebar.subheader('Filters')

min_rank_value = int(df_final['Rank'].min())
max_rank_value = int(df_final['Rank'].max())

# Adicionar o select slider na sidebar para escolher o intervalo de 'Rank'
selected_rank_range = st.sidebar.select_slider(
    'Rank (Market Cap)',
    options=range(min_rank_value, max_rank_value + 1),
    value=(min_rank_value, max_rank_value)
)

# Filtrar o DataFrame com base no intervalo do slider
df_final = df_final[(df_final['Rank'] >= selected_rank_range[0]) & (df_final['Rank'] <= selected_rank_range[1])]

busca_moeda = st.sidebar.text_input("🔍Search Coin (name or symbol)", help="Use a comma to filter more than one cryptocurrency. Example: BTC, ETH, BNB.")

# Verificar se há entrada no campo de pesquisa
if busca_moeda:
    # Dividir a entrada do usuário em várias moedas
    moedas = busca_moeda.split(',')
    
    # Converter todas as moedas para maiúsculas
    moedas = [moeda.strip().upper() for moeda in moedas]  # strip() remove espaços em branco
    
    # Filtrar o DataFrame com base nas moedas fornecidas pelo usuário
    filtro = df_final['Crypto'].str.upper().isin(moedas) | \
             df_final['symbol'].str.upper().isin(moedas) | \
             df_final['symbol_name'].str.upper().isin(moedas)
    
    # Aplicar o filtro ao DataFrame final
    df_final = df_final[filtro]




filtro_binance = st.sidebar.checkbox('Only Binance coins')

# Aplicar o filtro de Exchange se o checkbox estiver marcado
if filtro_binance:
    df_final = df_final[df_final['exchangeName'] == 'Binance']
else:
    df_final = df_final.copy()

filtro_open_interest = st.sidebar.checkbox('Derivative coins')

# Aplicar o filtro de 'Open Interest' se o checkbox estiver marcado
if filtro_open_interest:
    df_final = df_final[df_final['Open Interest'].notna()]



def calcular_metricas(df):
    media_openInterestCh24 = df['Open Interest 24h'].mean()*100
    media_longShortPerson = df['Long Short Ratio'].mean()
    media_lsPersonChg4h = df['LSR 4h'].mean()*100
    media_oicap = df['OI/Market Cap'].mean()
    media_volume = df['Volume Change 24h'].mean()*100
    fundingrate = df['Funding Rate'].mean()*100
    soma_openInterest = df['Open Interest'].sum()
    soma_volume = df['Volume 24h'].sum()
    soma_liquidationH24 = df['Liquidation 24h'].sum()
    soma_liquidationH1 = df['Liquidation 1h'].sum()
    return media_openInterestCh24, soma_openInterest, soma_volume, soma_liquidationH24, soma_liquidationH1, media_longShortPerson, media_lsPersonChg4h, fundingrate,  media_volume, media_oicap


def formatar_numero(num):
    if num >= 1e9:
        return f'${num / 1e9:.2f}B'
    elif num >= 1e6:
        return f'${num / 1e6:.2f}M'
    elif num >= 1e3:
        return f'${num / 1e3:.2f}K'
    else:
        return str(num)

# Função para exibir métricas
def exibir_metricas(media_openInterestCh24, soma_openInterest, soma_volume, soma_liquidationH24, soma_liquidationH1, media_longShortPerson, media_lsPersonChg4h, fundingrate, media_volume, media_oicap):
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        #st.metric(label="Total Open Interest", value="${:,.0f}".format(soma_openInterest), delta="{:.1f}%".format(media_openInterestCh24))
        st.metric(label="Total Open Interest", value=formatar_numero(soma_openInterest), delta="{:.1f}%".format(media_openInterestCh24))
    with col2:
        st.metric(label="Volume 24h", value=formatar_numero(soma_volume), delta="{:.1f}%".format(media_volume))
    with col3:
        st.metric(label="Liquidation 24h", value=formatar_numero(soma_liquidationH24))
    with col4:
        st.metric(label="Liquidation 1h", value=formatar_numero(soma_liquidationH1))
    with col5:
        st.metric(label="Long Short Ratio", value="{:,.2f}".format(media_longShortPerson), delta="{:.2f}%".format(media_lsPersonChg4h)) 
    with col6:
        st.metric(label="Funding Rate", value="{:.2f}%".format(fundingrate))
    with col7:
        st.metric(label="OI/Market Cap", value="{:.2f}%".format(media_oicap))    


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
    ('Default', 'Performance', 'Formulas', 'Technical indicators', 'Open Interest', 'Liquidations', 'Longs vs Shorts', 'Funding Rate', 'Volume', 'Market Cap', 'Custom'),
    horizontal=True
)
st.session_state['filter_option'] = filter_option

# Mapeamento das colunas para cada filtro
filtro_colunas = {
    'Default': ['Coin', 'Price USD', 'Price 24h','Open Interest', 'Open Interest 24h', 'OI/Market Cap', 'Volume24h/OI','Volume24h/Market Cap','Short-Term OI Trend', 'Long-Term OI Trend', 'Top Trader Sentiment', 'Top Trader LSR Account', 'Top Trader LSR Position','Liquidation 24h','rsi24h', 'bb_24h', 'macd_24h'],
    'Open Interest': ['Coin', 'Price USD', 'Open Interest', 'Short-Term OI Trend', 'Long-Term OI Trend','Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m', 'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h', 'Open Interest 2d', 'Open Interest 3d', 'Open Interest 7d'],
    'Formulas': ['Coin', 'Price USD', 'OI/Market Cap', 'Volume24h/OI','Volume24h/Market Cap','Short-Term OI Trend', 'Long-Term OI Trend', 'Top Trader Sentiment', 'Short-Term RSI Trend','Long-Term RSI Trend','Funding Rate Risk','Liquidations 24h/OI', 'Long Liquidations/OI', 'Short Liquidations/OI'],
    'Performance': ['Coin', 'Price USD', 'Volume Change 24h', 'Price 5m','Price 15m','Price 30m','Price 1h','Price 2h','Price 4h','Price 6h','Price 8h','Price 12h','Price 24h','price1week','price2week','price30day','price_year_to_date','price1year'],
    'Technical indicators': ['Coin', 'Price USD', 'rsi5min', 'rsi15min', 'rsi30min', 'rsi1h', 'rsi2h', 'rsi4h', 'rsi24h', 'macd_5min', 'macd_15min', 'macd_30min', 'macd_1h', 'macd_2h', 'macd_4h', 'macd_24h', 'bb_5min', 'bb_15min', 'bb_30min', 'bb_1h', 'bb_2h', 'bb_4h', 'bb_24h'],
    'Liquidations': ['Coin', 'Price USD', 'Liquidation 1h', 'Long Liquidation 1h', 'Short Liquidation 1h', 'Liquidation 4h', 'Long Liquidation 4h', 'Short Liquidation 4h', 'Liquidation 12h', 'Long Liquidation 12h', 'Short Liquidation 12h', 'Liquidation 24h', 'Long Liquidation 24h', 'Short Liquidation 24h'],
    'Longs vs Shorts': ['Coin', 'Price USD', 'Long Short Ratio', 'Top Trader LSR Account', 'Top Trader LSR Position', 'Top Trader Sentiment','LSR 5m', 'LSR 15m', 'LSR 30m', 'LSR 1h', 'LSR 4h', 'Long vs Short Real Time', 'Long Ratio', 'Short Ratio'],
    'Funding Rate': ['Coin', 'Price USD', 'Funding Rate','Funding Rate Risk'],
    'Volume': ['Coin', 'Price USD', 'Volume 24h', 'Volume Change 24h','Volume24h/Market Cap','Buy Volume 5m','Sell Volume 5m','Buy Volume 15m','Sell Volume 15m','Buy Volume 30m','Sell Volume 30m','Buy Volume 1h','Sell Volume 1h','Buy Volume 2h','Sell Volume 2h','Buy Volume 4h','Sell Volume 4h','Buy Volume 6h','Sell Volume 6h','Buy Volume 8h','Sell Volume 8h','Buy Volume 12h','Sell Volume 12h','Buy Volume 24h','Sell Volume 24h',],
    'Market Cap': ['Coin', 'Price USD', 'Market Cap','circulatingSupply', 'totalSupply','maxSupply','OI/Market Cap','Volume24h/Market Cap'],
    'Custom': [],
    #'All': ['Coin'] + df_final.columns.tolist()
}


# Selecionar colunas baseado no filtro escolhido
colunas_selecionadas = filtro_colunas[filter_option]

if filter_option == 'Custom':
    # Seletor de colunas customizadas
    st.session_state['temp_custom_columns'] = st.multiselect(
        'Choose the columns:',
        df_final.columns.tolist(),
        default=st.session_state.get('custom_columns', []),
        key='unique_custom_columns_select'
    )

    # Botão para atualizar as colunas no AgGrid
    if st.button('Update Columns'):
        st.session_state['custom_columns'] = st.session_state['temp_custom_columns']

    colunas_selecionadas = st.session_state.get('custom_columns', [])
else:
    colunas_selecionadas = filtro_colunas[filter_option]


# Adicionar 'Coin' se não estiver presente
if 'Coin' not in colunas_selecionadas:
    colunas_selecionadas = ['Coin'] + colunas_selecionadas

# Filtrar o DataFrame com base nas colunas selecionadas
df_filtrado = df_final[colunas_selecionadas]


if filter_option == 'Open Interest':
    df_filtrado = df_filtrado[df_filtrado['Open Interest'].notna()] 
elif filter_option == 'Funding Rate':
    df_filtrado = df_filtrado[df_filtrado['Funding Rate'].notna()]
elif filter_option == 'Technical indicators':
    df_filtrado = df_filtrado[df_filtrado['rsi5min'].notna()]
elif filter_option == 'Liquidations':
    df_filtrado = df_filtrado[df_filtrado['Liquidation 24h'].notna()]
elif filter_option == 'Longs vs Shorts':
    df_filtrado = df_filtrado[df_filtrado['Long vs Short Real Time'].notna()]             



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
other_options = {'suppressColumnVirtualisation': True}
gb.configure_grid_options(**other_options)
#gb.configure_selection('single', use_checkbox=True, rowMultiSelectWithClick=False, suppressRowDeselection=False, pre_selected_rows=selected_row_indices)
gb.configure_side_bar()

for coluna in colunas_dolar:
    if coluna in colunas_selecionadas:
        gb.configure_column(coluna, cellRenderer=dollar_formatter)

for coluna in colunas_percentual:
    if coluna in colunas_selecionadas:
        gb.configure_column(coluna, cellRenderer=percent_formatter)

for coluna in colunas_percentual2:
    if coluna in colunas_selecionadas:
        gb.configure_column(coluna, cellRenderer=percent_formatter2)

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
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
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
            <div id="tradingview_7b9c5" style="width: 100%; height: 700px;"></div>
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
                "locale": "en",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "gridColor": "rgba(240, 243, 250, 0.03)",
                "allow_symbol_change": true,
                "container_id": "tradingview_7b9c5"
            }});
            </script>
        </div>
        """
    st.components.v1.html(tradingview_html, height=700)
else:
    st.warning("Select a cryptocurrency to view the chart")


tradingview_html1 = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-quotes.js" async>
      {
        "width": "100%",
        "height": "600",
        "symbolsGroups": [
            {
            "name": "Crypto",
            "symbols": [
                {
                "name": "CRYPTOCAP:BTC.D",
                "displayName": "BTC Dominance"
                },
                {
                "name": "CRYPTOCAP:ETH.D",
                "displayName": "ETH Dominance"
                },
                {
                "name": "CRYPTOCAP:TOTAL",
                "displayName": "Crypto Total Market Cap"
                },
                {
                "name": "CRYPTOCAP:TOTAL2",
                "displayName": "Crypto Total Market Cap (Exclude BTC)"
                },
                {
                "name": "CRYPTOCAP:USDT",
                "displayName": "Market Cap USDT"
                },
                {
                "name": "BTCUSDLONGS/BTCUSDSHORTS",
                "displayName": "Bitfinex Long Short Ratio"
                }
            ]
            },
            {
            "name": "Market",
            "symbols": [
                {
                "name": "OANDA:SPX500USD",
                "displayName": "S&P500"
                },
                {
                "name": "OANDA:NAS100USD",
                "displayName": "NASDAQ100"
                },
                {
                "name": "CAPITALCOM:DXY",
                "displayName": "US DOLLAR INDEX"
                },
                {
                "name": "TVC:GOLD",
                "displayName": "GOLD"
                }
            ]
            }
        ],
        "showSymbolLogo": true,
        "isTransparent": false,
        "colorTheme": "dark",
        "locale": "en"
        }
      </script>
    </div>
    <!-- TradingView Widget END -->
"""

# HTML para o segundo widget do TradingView
tradingview_html2 = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
      {
        "width": "100%",
        "height": "600",
        "defaultColumn": "overview",
        "screener_type": "crypto_mkt",
        "displayCurrency": "USD",
        "colorTheme": "dark",
        "locale": "en"
      }
      </script>
    </div>
    <!-- TradingView Widget END -->
"""

# Usar o layout de colunas para organizar os widgets
col1, col2 = st.columns(2)

# Coluna 1: Primeiro widget do TradingView
with col1:
    st.components.v1.html(tradingview_html1, height=700)

# Coluna 2: Segundo widget do TradingView
with col2:
    st.components.v1.html(tradingview_html2, height=700)


with st.expander("About the Indicators"):
    st.markdown("""
        **OI/Market Cap:** Measures the risk level of cryptocurrencies. A very high Open Interest in relation to Market Cap is a sign of high leverage, indicating that significant volatility is imminent.  
        **OI/Volume24h:** The relationship between Open Interest and 24-hour trading volume.   
        **24h Volume/Market Cap:** Measures how much the Trading Volume in the last 24 hours represents against the Market Cap of the Cryptocurrency. If the ratio is very high, it signals a high demand for the coins in the short term and this indicates the entry or exit of large market players.        
        **Short-Term OI Trend:** This metric measures the variation in Open Interest from 5 minutes to 1 hour. It proves quite effective for rapid and short-term trends. It's calculated from the average variation of (5m + 15m + 30m + 1h) / 4.  
        **Long-Term OI Trend:** This metric measures the variation in Open Interest from 4 hours to 1 week. It is highly effective for medium and long-term trends and also indicates the level of interest in leverage. Calculated from the combined average variation of (4h + 24h + 2d + 3d + 7d) / 5.  
        **Top Trader Sentiment:** Monitors the sentiment of top traders' positions on Binance, OKX, Bybit, and Bitget. High values indicate a large number of accounts positioned in Longs and a high value of the positions of the top 20% traders. Generally, the price tends to move against this indicator due to forced liquidations by Exchanges. It is a proprietary indicator of Dominando Cripto.  
        **Short-Term RSI Trend:** Tracks the evolution of RSI from 5 minutes to 1 hour. Excellent for demonstrating the strength or weakness of the asset in the short term.  
        **Long-Term RSI Trend:** Monitors the evolution of RSI from 4 hours to 24 hours. An important indicator to eliminate bias in market strength or weakness or to support strategies of RSI divergence.  
        **Funding Rate Risk:** This is the multiplication of the aggregated Funding Rate from various exchanges with the Top Trader Sentiment indicator. In other words, it is an experimental metric that assesses how much Exchanges are willing to maintain a Positive or Negative Funding Rate in favor of trader sentiment. For example, if the Funding Rate is relatively high and Top Trader Sentiment is also high, it signals a risk that a Dump could occur in the currency at any moment, favoring Short positions.
    """)


hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


