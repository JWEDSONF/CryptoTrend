import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as ps
from datetime import datetime
import asyncio
import aiohttp

st.set_page_config(
    page_title="Correlation Heatmap",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://forms.gle/a9X3vpug4AXGV3JP7",
        'About': """
            **Correlation Heatmap: Exploring Cryptocurrency Relationships**

            The Correlation Heatmap is a powerful tool for visualizing the relationships between different cryptocurrencies within a dataset. With this feature, users can compare any pair of cryptocurrencies with diverse altcoins, with BTCUSDT set as the default comparison. 

            Key Features:
            - **Customizable Parameters:** Adjust the rolling period and timeframe to suit your analysis needs.
            - **Color Customization:** Change the heatmap color scheme to enhance visualization.
            - **Insightful Analysis:** Quickly identify patterns, trends, and dependencies between cryptocurrencies.

            Whether you're a seasoned investor or a cryptocurrency enthusiast, the Correlation Heatmap provides valuable insights into market dynamics, aiding in informed decision-making and portfolio management.

            Dominando Cripto - All rights reserved.
        """
    }
)


async def get_binance_symbols(session):
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    try:
        async with session.get(url) as response:
            data = await response.json()
            symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
            return symbols
    except Exception as e:
        st.error(f"Erro ao buscar símbolos: {e}")
        return []

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def get_data(coin, interval, limit):
    url = f"https://api.binance.com/api/v3/klines?symbol={coin}&interval={interval}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url)
        df = pd.DataFrame(response)
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                      'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df['close'].astype(float)
        return df


async def main():
    st.title("Correlation Heatmap")
    st.subheader('', divider='rainbow')

    async with aiohttp.ClientSession() as session:
        symbols = await get_binance_symbols(session)
    
    # Verificar se 'BTCUSDT' está na lista de símbolos
    default_symbol = "BTCUSDT"
    if default_symbol not in symbols:
        st.error(f"'{default_symbol}' is not available in the list of symbols.")
        return
   
    available_color_scales = ["Portland_r","Spectral", "Inferno", "Thermal","Viridis", "Jet", "Agsunset","Bluered","Plasma", "Rainbow"]

        # Selecionar moedas
    coins = ["ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "DOGEUSDT", "SOLUSDT", "UNIUSDT",
            "LTCUSDT", "LINKUSDT", "MATICUSDT", "THETAUSDT", "XLMUSDT", "VETUSDT", "TRXUSDT", "EOSUSDT", "FILUSDT",
            "AAVEUSDT", "SHIBUSDT", "PEPEUSDT", "ATOMUSDT", "NEOUSDT", "COTIUSDT","CAKEUSDT", "CHZUSDT", "EGLDUSDT", "NEARUSDT", 
            "XTZUSDT", "ENJUSDT", "KSMUSDT", "ICPUSDT", "MKRUSDT", "STXUSDT", "AXSUSDT", "GALAUSDT", "ETCUSDT", "ORDIUSDT",
            "BATUSDT", "SNXUSDT", "RENUSDT", "YFIUSDT", "MANAUSDT", "SUSHIUSDT", "ALGOUSDT", "COMPUSDT", "AVAXUSDT", 
            "SANDUSDT", "ANKRUSDT", "RUNEUSDT", "GRTUSDT", "1INCHUSDT", "ICXUSDT", "WAVESUSDT", "ZRXUSDT", "SXPUSDT",
            "ALICEUSDT", "LUNAUSDT", "GTCUSDT"]


    # Dividindo a tela em duas colunas
    col1, col2, col3, col4, col5, col6, col7= st.columns([1, 1, 1, 0.5, 0.5, 1, 1])


    # Adicionando os seletores de símbolo e intervalo na primeira coluna
    with col1:
        selected_symbol = st.selectbox('Symbol', symbols, index=symbols.index(default_symbol))
    with col2:
        st.write("")
        st.write("")
        popover = st.popover("Select Altcoins", use_container_width=True)
        selected_coins = popover.multiselect('Select Altcoins', symbols, default=coins)
    with col3:
        selected_interval = st.selectbox('Interval', ['1m', '5m', '15m', '30m','1h', '4h','12h','1d','1w'], index=6)
    with col4:
        correlation_period = st.slider("Correlation Period", min_value=1, max_value=100, value=20, step=1)
    with col5:
        selected_limit = st.slider('Limit', min_value=30, max_value=1000, value=1000)
    with col6:
        selected_color = st.selectbox("Select Color", available_color_scales)   
    with col7:
        st.write("Update")
        if st.button('↻',help="Click to update data",type="primary"):
            asyncio.create_task(update_data(selected_symbol, selected_interval, selected_limit))

    # with st.sidebar:
    #     st.title('Select Altcoins')
    #     with st.expander("Filter Altcoins", expanded=True):
    #         selected_coins = st.multiselect('Select Altcoins', symbols, default=coins)

    

    # Obter dados do Bitcoin
    btc_data = await get_data(selected_symbol, selected_interval, selected_limit)


    # Obter dados de outras moedas
    #tasks = [get_data(selected_coins, selected_interval, selected_limit) for coin in coins[1:]]
    # Obter dados de outras moedas
    tasks = [get_data(selected_coin, selected_interval, selected_limit) for selected_coin in selected_coins]
    #tasks = [get_data(coin, selected_interval, selected_limit) for coin in coins[1:]]


    other_coins_data = await asyncio.gather(*tasks)

    # Criar DataFrame para armazenar a correlação
    correlation_df = pd.DataFrame(index=btc_data.index)

    # Calcular a correlação de acordo com o período selecionado
    for column, coin_data in zip(coins[1:], other_coins_data):
        correlation = btc_data.rolling(window=correlation_period).corr(coin_data)
        correlation_df[column] = correlation

    # Calcular a média da correlação de todas as altcoins com o Bitcoin para cada período de tempo
    average_correlation = correlation_df.mean(axis=1)

    # Criar subplot com o preço do Bitcoin e marcadores coloridos com base na média da correlação
    fig = ps.make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.4, 0.4, 0.3])

    # Adicionar linha com o preço do Bitcoin
    #fig.add_trace(go.Scatter(x=btc_data.index, y=btc_data.values, mode='lines', name='BTC Price'), row=1, col=1)

    # Adicionar marcadores coloridos com base na média da correlação
    fig.add_trace(go.Scatter(x=average_correlation.index, y=btc_data.values, mode='lines+markers', 
                         marker=dict(color=average_correlation, colorscale=selected_color),
                         name=selected_symbol), row=1, col=1)


    # Criar heatmap com Plotly
    fig.add_trace(go.Heatmap(
        z=correlation_df.T.values,
        x=correlation_df.index,
        y=correlation_df.columns,
        colorscale=selected_color,
        name="Correlation",
        colorbar=dict(
            title='Correlation',
            len=0.45,
            lenmode='fraction',
            thickness=25,
        )
    ), row=2, col=1)


    # Adicionar scatter plot colorido representando a média da correlação ao longo do tempo
    fig.add_trace(go.Scatter(x=average_correlation.index, y=average_correlation.values, mode='lines+markers',
                             marker=dict(color=average_correlation, colorscale=selected_color),
                             name='Average Correlation'), row=3, col=1)


    fig.update_layout(
        title=dict(
            text=f"🚦Correlation Heatmap - {selected_symbol} versus ALTCOINS  <br><sup style='font-size: 9px;'>Timeframe: {selected_interval} • Correlation Period: {correlation_period}  • Total Pairs: {len(selected_coins)}</sup>",
            font=dict(
                family='Arial',
                size=22,
            ),
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        width=1600,
        height=900,
        showlegend=False,
        #yaxis=dict(tickangle=45),
        #template="simple_white",
        yaxis=dict(zeroline=False, tickprefix="$", side='left'),
        yaxis2=dict(side='left', showgrid=False,),
        #xaxis=dict(gridcolor='#0a0c11'),
        xaxis_rangeslider_visible=False,
        images=[dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.4,
            y=0.92,
            sizex=0.3,
            sizey=0.3,
            opacity=0.33,
            layer="below"
        )]
    )
    fig.update_yaxes(tickfont=dict(size=9), row=2, col=1)


    fig.update_layout(hoverlabel=dict(namelength=-1), hovermode='x')

    update_date_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    fig.add_annotation(
        x=0,
        y=-0.1,
        xref='paper',
        yref='paper',
        text=f'Update: {update_date_formatted} (UTC)',
        showarrow=False,
        font=dict(color='#9BABB8', size=10)
    )

    fig.add_annotation(
        x=1,
        y=-0.1,
        xref='paper',
        yref='paper',
        text='© Dominando Cripto All rights reserved',
        showarrow=False,
        font=dict(color='#9BABB8', size=11)
    )
    fig.update_layout(newshape={'line': {'color': '#5356FF', 'width': 1.5}})

    config = {
    'scrollZoom': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'resetViews', 'toImage'],
    'toImageButtonOptions': {
       'format': 'png',  # one of png, svg, jpeg, webp
       'filename': "Correlation Heatmap",
       'height': 900,
       'width': 1600,
       'scale': 1
        }
    }

    st.plotly_chart(fig, use_container_width=True, config=config)
    #category_name = "All Cryptocurrencies"
    #cryptocurrencies = ', '.join([crypto.replace("USDT", "") for crypto in selected_coins])
    cryptocurrencies = ', '.join([crypto for crypto in selected_coins])
    st.write(f"The correlation heatmap includes data from {len(selected_coins)} pairs of cryptocurrencies - {cryptocurrencies}")

 


async def update_data(selected_symbol, selected_interval, selected_limit):
    async with aiohttp.ClientSession() as session:
        df = await get_data(selected_symbol, selected_interval, selected_limit)
        # Atualizar o gráfico ou fazer qualquer outra coisa com os novos dados

# Executar o programa principal
if __name__ == "__main__":
    asyncio.run(main())

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


