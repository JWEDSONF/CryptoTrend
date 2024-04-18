import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import asyncio
import aiohttp
from aiohttp import ClientSession


st.set_page_config(
    page_title="Crypto Index Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://forms.gle/a9X3vpug4AXGV3JP7",
        'About': """
        Welcome to the Crypto Index Dashboard! This platform allows you to explore and analyze the performance of various cryptocurrency categories. You can compare them with Bitcoin or any pair of altcoins, as well as assess the risk using the Sharpe Ratio.

        Whether you're a seasoned trader or a curious enthusiast, our dashboard provides valuable insights to inform your investment decisions in the dynamic world of cryptocurrencies.

        Happy exploring and may your crypto journey be filled with success! 🚀
        """
    }
)


# Definição das categorias e criptomoedas correspondentes
indices = {
    "Layer-1": ["ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT", "TRXUSDT", "DOTUSDT", "NEARUSDT","MATICUSDT","ICPUSDT","APTUSDT","ETCUSDT","STXUSDT","ATOMUSDT","XLMUSDT","XMLUSDT"],
    "Memecoins": ["DOGEUSDT", "SHIBUSDT", "PEPEUSDT","WIFUSDT", "FLOKIUSDT", "BONKUSDT", "ORDIUSDT","1000SATSUSDT","BOMEUSDT","MEMEUSDT","PEOPLEUSDT"],
    "AI": ["TAOUSDT","GRTUSDT", "THETAUSDT", "FETUSDT", "AGIXUSDT", "WLDUSDT", "OCEANUSDT", "PONDUSDT","RLCUSDT","IQUSDT","AIUSDT","NFPUSDT"],
    "POW": ["BTCUSDT", "DOGEUSDT", "BCHUSDT", "LTCUSDT", "STXUSDT", "ETCUSDT", "CFXUSDT", "IOTAUSDT","CKBUSDT","ANKRUSDT","ZILUSDT","SCUSDT","RVNUSDT","ZECUSDT","DASHUSDT"],
    "Games": ["IMXUSDT", "BEAMXUSDT", "FLOKIUSDT","GALAUSDT","AXSUSDT","RONINUSDT","SANDUSDT","MANAUSDT","ENJUSDT","ILVUSDT","PIXELUSDT","YGGUSDT","BNXUSDT"],
    "Payments": ["XRPUSDT", "BCHUSDT", "LTCUSDT", "COTIUSDT", "ACHUSDT", "XNOUSDT", "PUNDIXUSDT","UTKUSDT","DASHUSDT"],
    "Fan Token": ["CHZUSDT", "PSGUSDT", "BARUSDT", "SANTOSUSDT","CITYUSDT","LAZIOUSDT", "OGUSDT","ALPINEUSDT","PORTOUSDT","JUVUSDT","JUVUSDT"],
    "Real World Assets": ["AVAXUSDT","ICPUSDT","MKRUSDT","PENDLEUSDT","SNXUSDT","OMUSDT","RSRUSDT","POLYXUSDT","CHRUSDT","DUSKUSDT"],
    "BSC Ecosystem": ["BNBUSDT", "INJUSDT", "GALAUSDT", "CAKEUSDT", "IDUSDT", "TWTUSDT", "SFPUSDT","ONTUSDT","BNXUSDT","C98USDT","XVSUSDT","HOOKUSDT","MBOXUSDT"],
    "Solana Ecosystem": ["RNDRUSDT", "WIFUSDT", "JUPUSDT", "WUSDT", "BONKUSDT","PYTHUSDT","BOMEUSDT","GMTUSDT","RAYUSDT","JTOUSDT","TNSRUSDT"],
    "Cardano Ecosystem": ["ADAUSDT", "COTIUSDT", "AGIXUSDT", "NEXOUSDT", "API3USDT"],
    "Polkadot Ecosystem": ["DOTUSDT","ASTRUSDT","GLMRUSDT", "KSMUSDT", "PHAUSDT", "ACAUSDT", "ATAUSDT", "REEFUSDT","LITUSDT","AKROUSDT"],
    "DeFi": ["UNIUSDT", "INJUSDT", "MKRUSDT", "RUNEUSDT", "PENDLEUSDT","LDOUSDT","ENAUSDT","JUPUSDT","AAVEUSDT","SNXUSDT","KAVAUSDT","CAKEUSDT","KLAYUSDT","OSMOUSDT"],
    "Storage": ["FILUSDT", "STXUSDT", "ARUSDT", "BTTCUSDT", "HOTUSDT", "SCUSDT", "STORJUSDT","RIFUSDT","BLZUSDT"],
    "Infrastructure": ["LINKUSDT","RNDRUSDT","GRTUSDT","THETAUSDT","TIAUSDT","FETUSDT","PYTHUSDT","QNTUSDT","WUSDT","WLDUSDT","JASMYUSDT","AXLUSDT","ASTRUSDT"]
}

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

# async def fetch_data(session, symbol, interval):
#     url = 'https://api.binance.com/api/v3/klines'
#     params = {'symbol': symbol, 'interval': interval, 'limit': 1000}
#     async with session.get(url, params=params) as response:
#         if response.status == 200:
#             data = await response.json()
#             df = pd.DataFrame(data)
#             df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
#             df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
#             df.set_index('Open time', inplace=True)
#             df['Close'] = df['Close'].astype(float)
#             df['Volume'] = df['Volume'].astype(float)
#             df['Number of trades'] = df['Number of trades'].astype(float)
#             df['Taker buy quote asset volume'] = df['Taker buy quote asset volume'].astype(float)
#             # Calcula CVD
#             df['Volume_Delta'] = df['Taker buy quote asset volume'] - (df['Quote asset volume'].astype(float) - df['Taker buy quote asset volume'])
#             df['CVD'] = df['Volume_Delta'].cumsum()
#             #df['CVD'] = (df['Taker buy quote asset volume'] - df['Quote asset volume'].astype(float) + df['Taker buy quote asset volume']).cumsum()
#             df = df.sort_index()  # Ordena pelo índice
#             return df[['Close', 'Volume', 'CVD','Number of trades', 'Volume_Delta' ]]
#         else:
#             return pd.DataFrame()

async def fetch_data(session, symbol, interval):
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': symbol, 'interval': interval, 'limit': 1000}
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                df = pd.DataFrame(data)
                df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
                df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
                df.set_index('Open time', inplace=True)
                df['Close'] = df['Close'].astype(float)
                df['Volume'] = df['Volume'].astype(float)
                df['Number of trades'] = df['Number of trades'].astype(float)
                df['Taker buy quote asset volume'] = df['Taker buy quote asset volume'].astype(float)
                # Calcula CVD
                df['Volume_Delta'] = df['Taker buy quote asset volume'] - (df['Quote asset volume'].astype(float) - df['Taker buy quote asset volume'])
                df['CVD'] = df['Volume_Delta'].cumsum()
                df = df.sort_index()  # Ordena pelo índice
                return df[['Close', 'Volume', 'CVD','Number of trades', 'Volume_Delta' ]]
            else:
                st.error(f"Erro ao fazer solicitação HTTP: {response.status}")
                return pd.DataFrame()
    except aiohttp.ClientError as ce:
        st.error(f"Erro de cliente ao fazer solicitação HTTP: {ce}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()




async def gather_data(symbols, selected_interval, session):
    tasks = [fetch_data(session, symbol, selected_interval) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    return results

def calculate_index(index_data, index_type):
    if index_type == 'Average price':
        return index_data['Close'].mean(axis=1)
    elif index_type == 'Normalize':
        normalized_data = index_data['Close'].pct_change().fillna(0) + 1
        return normalized_data.cumprod().mean(axis=1)


def calculate_variation(data, period=30):
    return (data - data.shift(periods=period)) / data.shift(periods=period) * 100


def calcular_sharpe_ratio(df, timeperiod):
    """Calcula o Sharpe Ratio para um DataFrame de preços de criptomoedas."""
    df['retorno_diario'] = df['Close'].pct_change()
    #timeperiod = 365
    df['retorno_anualizado'] = df['retorno_diario'].rolling(window=timeperiod, min_periods=1).mean() * 252
    df['desvio_padrao_anualizado'] = df['retorno_diario'].rolling(window=timeperiod, min_periods=1).std() * np.sqrt(252)
    df['sharpe_ratio'] = df['retorno_anualizado'] / df['desvio_padrao_anualizado']
    return df




async def main():
    st.title('Crypto Index Dashboard')
    #st.subheader('Explore cryptocurrency categories, evaluate performance, and compare with any cryptocurrency', divider='rainbow')

    async with ClientSession() as session:
        symbols = await get_binance_symbols(session)
        if symbols:
            with st.sidebar.form(key='my_form'):
                base_symbol = st.selectbox('Coin (Base)', symbols, index=symbols.index('BTCUSDT') if 'BTCUSDT' in symbols else 0)
                selected_category = st.selectbox('Index Category', list(indices.keys()))
                st.session_state.selected_category = selected_category
                index_type = st.selectbox('Index Type', ['Normalize', 'Average price'])
                selected_interval = st.selectbox('Timeframe', list({'1 day': '1d', '12 hours': '12h', '4 hours': '4h', '1 hour': '1h','30 minutes': '30m', '15 minutes': '15m','5 minutes': '5m','1 minute': '1m', '1 week': '1w'}.keys()))
                period = st.slider('Percentage change period', min_value=1, max_value=180, value=20)
                st.session_state.period = period
                timeperiod = st.slider('Sharpe Ratio period', min_value=1, max_value=365, value=90)
                submit_button = st.form_submit_button(label='🔄️Update')


            if submit_button:
                base_data = await fetch_data(session, base_symbol, {'1 day': '1d', '12 hours': '12h', '4 hours': '4h', '1 hour': '1h','30 minutes': '30m', '15 minutes': '15m','5 minutes': '5m','1 minute': '1m', '1 week': '1w'}[selected_interval])
                selected_coins = indices[selected_category]
                coins_data = await gather_data(selected_coins, {'1 day': '1d', '12 hours': '12h', '4 hours': '4h', '1 hour': '1h','30 minutes': '30m', '15 minutes': '15m','5 minutes': '5m','1 minute': '1m', '1 week': '1w'}[selected_interval], session)

                index_data = {'Close': pd.DataFrame(), 'Volume': pd.DataFrame(), 'CVD': pd.DataFrame(), 'Volume_Delta': pd.DataFrame(), 'Number of trades': pd.DataFrame()}
                for coin, coin_data in zip(selected_coins, coins_data):
                    if not coin_data.empty:
                        index_data['Close'] = pd.concat([index_data['Close'], coin_data['Close']], axis=1)
                        index_data['Volume'] = pd.concat([index_data['Volume'], coin_data['Volume']], axis=1)
                        index_data['CVD'] = pd.concat([index_data['CVD'], coin_data['CVD']], axis=1)
                        index_data['Volume_Delta'] = pd.concat([index_data['Volume_Delta'], coin_data['Volume_Delta']], axis=1)
                        index_data['Number of trades'] = pd.concat([index_data['Number of trades'], coin_data['Number of trades']], axis=1)                              
                              

                index_series = pd.Series()
                if not index_data['Close'].empty:
                    index_series = calculate_index(index_data, index_type)

                if not base_data.empty and not index_series.empty:
                    base_variation = calculate_variation(base_data['Close'], period=period)
                    index_variation = calculate_variation(index_series, period=period)

                    # Gráfico de Preços
                    # Criar subplots
                    fig_prices = make_subplots(rows=2, cols=1,
                                                specs=[[{"secondary_y": True}],[{"secondary_y": True}]],
                                                vertical_spacing=0.05, shared_xaxes=True,
                                                row_heights=[0.6, 0.4], subplot_titles=(f'Price comparison: {base_symbol} vs {selected_category}',f'Variation of {base_symbol} and {selected_category} (%)'))

                    # Adicionar os traços dos preços e das variações na primeira linha
                    fig_prices.add_trace(go.Scatter(x=base_data.index, y=base_data['Close'], name=base_symbol, line=dict(color='#5356FF')), row=1, col=1)
                    fig_prices.add_trace(go.Scatter(x=index_series.index, y=index_series, name=f'{selected_category} ({index_type})',line=dict(color='#FAA300')), row=1, col=1, secondary_y=True)

                    # Adicionar os traços das variações calculadas na segunda linha
                    fig_prices.add_trace(go.Scatter(x=base_variation.index, y=base_variation, name=f'Base: {base_symbol}',line=dict(color='#5356FF')), row=2, col=1)
                    fig_prices.add_trace(go.Scatter(x=index_variation.index, y=index_variation, name=f'Index: {selected_category}', line=dict(color='#FAA300')), row=2, col=1, secondary_y=False)

                    # Atualizar o layout
                    fig_prices.update_layout(
                        #title=f'Price comparison: {base_symbol} vs {selected_category}',
                        title=dict(text='Performance Analysis', font=dict(family='Arial',size=22,)),
                        yaxis=dict(title=f'Price: {base_symbol}', side='left'),
                        yaxis2=dict(title=f'Index {selected_category} ({index_type})', side='right', overlaying='y', showgrid=False),
                        legend=dict(x=0.01, y=0.99),
                        hoverlabel=dict(namelength=-1),
                        hovermode='x',
                        width=1600,
                        height=900,
                    )
                    fig_prices.update_yaxes(title_text=f'Variation of {base_symbol} and {selected_category} (%)', side='right', ticksuffix="%", showgrid=False, row=2, col=1, secondary_y=False)


                    fig_prices.update_layout(hoverlabel=dict(namelength=-1), hovermode='x')

                    update_date_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    fig_prices.add_annotation(
                        x=0,
                        y=-0.1,
                        xref='paper',
                        yref='paper',
                        text=f'Update: {update_date_formatted} (UTC)',
                        showarrow=False,
                        font=dict(color='#9BABB8', size=10)
                    )

                    fig_prices.add_annotation(
                        x=1,
                        y=-0.1,
                        xref='paper',
                        yref='paper',
                        text='© Dominando Cripto All rights reserved',
                        showarrow=False,
                        font=dict(color='#9BABB8', size=11)
                    )
                    fig_prices.update_layout(newshape={'line': {'color': '#5356FF', 'width': 1.5}})

                    config = {
                    'scrollZoom': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'resetViews', 'toImage'],
                    'toImageButtonOptions': {
                    'format': 'png',  # one of png, svg, jpeg, webp
                    'filename': "Performance Analysis",
                    'height': 900,
                    'width': 1600,
                    'scale': 1
                        }
                    }
                    st.plotly_chart(fig_prices, use_container_width=True, config=config)

                    # Gráfico de Variação Percentual
                    index_data_cvd = index_data['CVD'].sum(axis=1)
                    index_data_vd = index_data['Volume_Delta'].sum(axis=1) 
                    fig_cvd = make_subplots(rows=3, cols=1,
                                                specs=[[{"secondary_y": True}],[{"secondary_y": True}],[{"secondary_y": True}]],
                                                vertical_spacing=0.02, shared_xaxes=True,
                                                row_heights=[0.44, 0.28, 0.28], subplot_titles=(f'Price comparison: {base_symbol} vs {selected_category}',f'CVD of {base_symbol} vs {selected_category} ($)',f'Volume Delta of {base_symbol} vs {selected_category} ($)' ))

                    # Adicionar os traços dos preços e das variações na primeira linha
                    fig_cvd.add_trace(go.Scatter(x=base_data.index, y=base_data['Close'], name=base_symbol, line=dict(color='#5356FF')), row=1, col=1)
                    fig_cvd.add_trace(go.Scatter(x=index_series.index, y=index_series, name=f'{selected_category} ({index_type})',line=dict(color='#FAA300')), row=1, col=1, secondary_y=True)

                    # Adicionar os traços das variações calculadas na segunda linha
                    fig_cvd.add_trace(go.Scatter(x=base_data.index, y=base_data['CVD'], name=f'CVD: {base_symbol}',line=dict(color='#5356FF')), row=2, col=1)
                    fig_cvd.add_trace(go.Scatter(x=index_data_cvd.index, y=index_data_cvd, name=f'CVD: {selected_category}', line=dict(color='#FAA300')), row=2, col=1, secondary_y=True)

                    fig_cvd.add_trace(go.Scatter(x=base_data.index, y=base_data['Volume_Delta'], name=f'Volume Delta: {base_symbol}',line=dict(color='#5356FF')), row=3, col=1)
                    fig_cvd.add_trace(go.Scatter(x=index_data_vd.index, y=index_data_vd, name=f'Volume Delta: {selected_category}', line=dict(color='#FAA300')), row=3, col=1, secondary_y=True)

                    # Atualizar o layout
                    fig_cvd.update_layout(
                        #title=f'Price comparison: {base_symbol} vs {selected_category}',
                        title=dict(text='Volume Analysis',font=dict(family='Arial',size=22,)),
                        yaxis=dict(title=f'Price: {base_symbol}', side='left'),
                        yaxis2=dict(title=f'Index {selected_category} ({index_type})', side='right', overlaying='y', showgrid=False),
                        legend=dict(x=0.01, y=0.99),
                        hoverlabel=dict(namelength=-1),
                        hovermode='x',
                        width=1600,
                        height=900,
                        images=[dict(
                            source='https://i.imgur.com/GyN6BI4.png',
                            xref="paper",
                            yref="paper",
                            x=0.4,
                            y=0.92,
                            sizex=0.24,
                            sizey=0.24,
                            opacity=0.33,
                            layer="below"
                        )]
                    )
                    fig_cvd.update_yaxes(title_text=f'CVD of {base_symbol}', side='left', tickprefix="$", row=2, col=1)
                    fig_cvd.update_yaxes(title_text=f'CVD of {selected_category}', side='right', tickprefix="$", showgrid=False, row=2, col=1, secondary_y=True)

                    fig_cvd.update_yaxes(title_text=f'Volume Delta of {base_symbol}', side='left', tickprefix="$",showgrid=False, row=3, col=1)
                    fig_cvd.update_yaxes(title_text=f'Volume Delta of {selected_category}', side='right', tickprefix="$", showgrid=False, row=3, col=1, secondary_y=True)


                    fig_cvd.update_layout(hoverlabel=dict(namelength=-1), hovermode='x')

                    update_date_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    fig_cvd.add_annotation(
                        x=0,
                        y=-0.1,
                        xref='paper',
                        yref='paper',
                        text=f'Update: {update_date_formatted} (UTC)',
                        showarrow=False,
                        font=dict(color='#9BABB8', size=10)
                    )

                    fig_cvd.add_annotation(
                        x=1,
                        y=-0.1,
                        xref='paper',
                        yref='paper',
                        text='© Dominando Cripto All rights reserved',
                        showarrow=False,
                        font=dict(color='#9BABB8', size=11)
                    )
                    fig_cvd.update_layout(newshape={'line': {'color': '#5356FF', 'width': 1.5}})

                    config = {
                    'scrollZoom': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'resetViews', 'toImage'],
                    'toImageButtonOptions': {
                    'format': 'png',  # one of png, svg, jpeg, webp
                    'filename': "Corr",
                    'height': 900,
                    'width': 1600,
                    'scale': 1
                        }
                    }
                    st.plotly_chart(fig_cvd, use_container_width=True, config=config)

                    
                    # Calculando o total de trades
                    total_trades = index_data['Number of trades'].sum(axis=1)

                    # Criando subplots
                    fig_trades = make_subplots(rows=2, cols=1,
                                            specs=[[{"secondary_y": True}],[{"secondary_y": True}]],
                                            vertical_spacing=0.05, shared_xaxes=True,
                                            row_heights=[0.6, 0.4], subplot_titles=("Number of Trades Over Time", "Dominance Over Time"))

                    # Definindo a paleta de cores personalizada
                    custom_colors = ['#ff2442', '#fd543a', '#fc8531', '#fab529', '#ecd629', '#b8cb41', '#84bf58', '#50b470', '#2fa78d', '#2099b0', '#128bd3', '#047df6', '#1d63e1', '#4445b8', '#6a2890', '#910a67']
                    opacity = 0.7  # Definindo a opacidade

                    # Criando lista para armazenar os dados de barras empilhadas
                    stacked_bars = []

                    # Iterando sobre os dataframes de moeda e as cores personalizadas
                    for coin, df, color in zip(selected_coins, coins_data, custom_colors):
                        if not df.empty:
                            # Adicionando os dados de barras empilhadas à lista
                            stacked_bars.append(go.Bar(x=df.index, y=df['Number of trades'], name=coin, marker=dict(color=color, opacity=opacity)))

                    fig_trades.add_trace(go.Scatter(x=index_series.index, y=index_series, name=f'{selected_category} ({index_type})',line=dict(color='#FAA300')), row=1, col=1, secondary_y=True)         

                    # Adicionando todos os dados de barras empilhadas ao subplot superior
                    for bar in stacked_bars:
                        fig_trades.add_trace(bar, row=1, col=1)

                    # Calculando a dominância de cada moeda em relação ao total de trades
                    for coin, df, color in zip(selected_coins, coins_data, custom_colors):
                        if not df.empty:
                            dominance = (df['Number of trades'] / total_trades) *100
                            dominance= dominance.rolling(window=3,min_periods=1).mean()
                            # Adicionando os dados de dominância ao subplot inferior
                            fig_trades.add_trace(go.Scatter(x=df.index, y=dominance, name=f'{coin} Dominance', mode='lines', line=dict(color=color,width=1.5)), row=2, col=1)

       

                    # Atualizando layout do subplot superior
                    fig_trades.update_yaxes(title_text="Number of Trades", secondary_y=False, row=1, col=1)

                    # Atualizando layout do subplot inferior
                    fig_trades.update_yaxes(title_text="Dominance (%)", ticksuffix="%", secondary_y=False, row=2, col=1)

                    # Atualizando o layout para o modo de barras empilhadas
                    fig_trades.update_layout(barmode='stack', title="Number of Trades and Dominance Over Time")

                    fig_trades.update_layout(
                        #title=f'Price comparison: {base_symbol} vs {selected_category}',
                        title=dict(text=f'Number of Trades and Dominance - {selected_category}',font=dict(family='Arial',size=22,)),
                        # yaxis=dict(title=f'Price: {base_symbol}', side='left'),
                        yaxis2=dict(title=f'Index {selected_category} ({index_type})', side='right', overlaying='y', showgrid=False),
                        hoverlabel=dict(namelength=-1),
                        hovermode='x',
                        width=1600,
                        height=900,
                    )

                    fig_trades.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        bgcolor="rgba(255, 255, 255, 0.38)",
                        font=dict(size=10)
                    ))

                    update_date_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    fig_trades.add_annotation(
                        x=0,
                        y=-0.1,
                        xref='paper',
                        yref='paper',
                        text=f'Update: {update_date_formatted} (UTC)',
                        showarrow=False,
                        font=dict(color='#9BABB8', size=10)
                    )

                    fig_trades.add_annotation(
                        x=1,
                        y=-0.1,
                        xref='paper',
                        yref='paper',
                        text='© Dominando Cripto All rights reserved',
                        showarrow=False,
                        font=dict(color='#9BABB8', size=11)
                    )
                    fig_trades.update_layout(newshape={'line': {'color': '#5356FF', 'width': 1.5}})

                    config = {
                    'scrollZoom': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'resetViews', 'toImage'],
                    'toImageButtonOptions': {
                    'format': 'png',  # one of png, svg, jpeg, webp
                    'filename': f'Number of Trades and Dominance - {selected_category}',
                    'height': 900,
                    'width': 1600,
                    'scale': 1
                        }
                    }
                    st.plotly_chart(fig_trades, use_container_width=True, config=config)

                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.5])
                    # Adicionando os dados de Sharpe Ratio para cada criptomoeda ao subplot da linha 2
                    for coin, df in zip(selected_coins, coins_data):
                        if not df.empty:
                            df['return'] = df['Close'].pct_change()
                            df['rolling_mean'] = df['return'].rolling(window=timeperiod,min_periods=20).mean()
                            df['rolling_std'] = df['return'].rolling(window=timeperiod,min_periods=20).std()
                            df['sharpe_ratio'] = df['rolling_mean'] / df['rolling_std']
                            
                            # Adiciona a linha do Sharpe Ratio no subplot de baixo
                            fig.add_trace(go.Scatter(x=df.index, y=df['sharpe_ratio'], mode='lines', name=f'{coin} Sharpe'), row=2, col=1)

                    # Adicionando o índice ao gráfico no subplot da linha 1, eixo y secundário
                    fig.add_trace(go.Scatter(x=index_series.index, y=index_series, name=f'{selected_category} ({index_type})', line=dict(color='#FAA300')), row=1, col=1)

                    # Atualiza layout para adicionar títulos e ajustar eixos
                    #fig.update_layout(title=f'{selected_category}: Index and Sharpe Ratio',font=dict(family='Arial',size=22), width=1600,height=900,)
                    fig.update_layout(
                        title=dict(text=f'{selected_category}: Index and Sharpe Ratio',font=dict(family='Arial',size=22,)),
                        # yaxis=dict(title=f'Price: {base_symbol}', side='left'),
                        #yaxis2=dict(title=f'Index {selected_category} ({index_type})', side='right', overlaying='y', showgrid=False),
                        hoverlabel=dict(namelength=-1),
                        hovermode='x',
                        width=1600,
                        height=900,
                    )
                    fig.update_layout(
                        updatemenus=[
                            dict(
                                buttons=[
                                    dict(
                                        args=[{'yaxis.type': 'log'}],
                                        label='Log',
                                        method='relayout'
                                    ),
                                    dict(
                                        args=[{'yaxis.type': 'linear'}],
                                        label='Linear',
                                        method='relayout'
                                    )
                                ],
                                direction='down',
                                pad={'r': 10, 't': 10},
                                showactive=True,
                                x=0.92,
                                xanchor='center',
                                y=1.08,
                                yanchor='top',
                                font=dict(size=10),
                                visible=True
                            ),
                            dict(
                                buttons=[
                                    dict(
                                        args=[{'yaxis2.type': 'linear'}],
                                        label='Linear',
                                        method='relayout'
                                    ),
                                    dict(
                                        args=[{'yaxis2.type': 'log'}],
                                        label='Log',
                                        method='relayout'
                                    )
                                ],
                                direction='down',
                                pad={'r': 10, 't': 10},
                                showactive=True,
                                x=1,
                                xanchor='center',
                                y=1.08,
                                yanchor='top',
                                font=dict(size=10)
                            ),
                        ],
                    )

                    fig.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        bgcolor="rgba(255, 255, 255, 0.38)" 
                    ))
                    # fig.update_yaxes(title_text="Preços", secondary_y=False, row=1, col=1)
                    # fig.update_yaxes(title_text="Índice", secondary_y=True, row=1, col=1)
                    # fig.update_yaxes(title_text="Sharpe Ratio", row=2, col=1)

                    st.plotly_chart(fig, use_container_width=True, config=config)
                else:
                    st.error('Unable to fetch base currency data or calculate index for selected category.')

                                # Adicionar a mensagem dinâmica no final da página
                # if st.session_state.selected_category:
                #     st.write(f"Este índice é composto por {', '.join(indices[st.session_state.selected_category])}")


if __name__ == "__main__":
    asyncio.run(main())

    # Inicialize o estado da sessão
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None
    
    # Verifique se o selected_category foi inicializado corretamente
    if st.session_state.selected_category:
        category_name = st.session_state.selected_category
        cryptocurrencies = ', '.join([crypto.replace("USDT", "") for c in category_name])
        st.write(f"{category_name} is an index composed of {len(index_data)} cryptocurrencies: {cryptocurrencies}")

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


