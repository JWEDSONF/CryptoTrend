import streamlit as st
import pandas as pd
from pandas.tseries.offsets import DateOffset
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import aiohttp
from aiohttp import ClientSession
import math
import pandas_ta as ta
from datetime import datetime


st.set_page_config(
    page_title="Crypto Signals",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://forms.gle/a9X3vpug4AXGV3JP7",
        'About': """
            **Crypto Signals: Harnessing Powerful Trend Indicators**

            Crypto Signals provides users with access to three robust trend indicators and signals for making informed trading decisions:

            1. **Alpha Quant Signal**
            2. **ATR-VWMA Trend Signal**
            3. **Price Transformation Oscillator**

            With Crypto Signals, users can adjust a wide range of parameters to fine-tune signals for each selected cryptocurrency. This customization ensures that traders can tailor signals to their specific preferences and trading strategies.

            Key Features:
            - **Customizable Parameters:** Adjust signal parameters to match individual trading preferences.
            - **Comprehensive Analysis:** Utilize multiple trend indicators to gain a deeper understanding of market dynamics.
            - **Buy and Sell Signals:** Receive timely signals for potential entry and exit points in the market.

            Whether you're a seasoned trader or new to cryptocurrency trading, Crypto Signals empowers users with actionable insights, enhancing trading strategies and decision-making processes.

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

async def fetch_data(session, symbol, interval, limit):
    url = 'https://api.binance.com/api/v3/klines'
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            df = pd.DataFrame(data)
            df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
            df.set_index('Open time', inplace=True)
            df['Open'] = df['Open'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['Close'] = df['Close'].astype(float)
            df['Volume'] = df['Volume'].astype(float)
            #df['Number of trades'] = df['Number of trades'].astype(float)
            #df['Taker buy quote asset volume'] = df['Taker buy quote asset volume'].astype(float)
            # Calcula CVD
            #df['CVD'] = (df['Taker buy quote asset volume'] - df['Quote asset volume'].astype(float) + df['Taker buy quote asset volume']).cumsum()
            df = df.sort_index()  # Ordena pelo índice
            return df
        else:
            return pd.DataFrame()



#st.sidebar.subheader('Dynamic parameters')

async def main():
    st.title("Crypto Signals")

    async with aiohttp.ClientSession() as session:
        symbols = await get_binance_symbols(session)
        

    # Definindo opções padrão
    default_symbol = "BTCUSDT"

    # Dividindo a tela em duas colunas
    col1, col2, col3, col4 = st.columns([1, 1, 0.5, 2])

    # Adicionando os seletores de símbolo e intervalo na primeira coluna
    with col1:
        selected_symbol = st.selectbox('Symbol', symbols, index=symbols.index(default_symbol))
    with col2:
        selected_interval = st.selectbox('Interval', ['1m', '5m', '15m', '30m','1h', '4h', '1d','1w'], index=6)
    with col3:
        selected_limit = st.slider('Limit', min_value=30, max_value=1000, value=1000)
    with col4:
        st.text("Update")  # Título vazio para alinhar corretamente os elementos

    # Adicionando o botão de atualização na mesma linha que os seletores
    with col4:
        if st.button('↻',help="Click to update data",type="primary"):
            asyncio.create_task(update_data(selected_symbol, selected_interval, selected_limit))


    # with st.sidebar:
    #     st.title('Alpha Quant')
    #     RSI_Period = st.sidebar.slider('RSI Length', 1, 100, 14)
    #     SF = st.sidebar.slider('RSI Smoothing', 1, 20, 5)
    #     QQE = st.sidebar.slider('Fast Quant Factor', 1.0, 10.0, 4.238)
    #     drift = st.sidebar.slider('Drift', 1, 10, 1)
    # #cci_length = st.slider('CCI Length', min_value=5, max_value=50, value=14)
    # with st.sidebar:
    #     st.title('ATR-VWMA Trend Signal')
    #     atr_period = st.sidebar.slider('ATR Period', min_value=1, max_value=100, value=10)
    #     factor = st.sidebar.slider('Factor', min_value=1.0, max_value=10.0, value=3.0)
    #     alpha = st.sidebar.slider('Alpha', min_value=0.0, max_value=1.0, value=0.7)
    #     x1 = st.sidebar.slider('VWMA Period', min_value=1, max_value=100, value=23)
    # with st.sidebar:
    #     st.title('Price Transformation')
    #     length = st.slider('Price Transformation Period', min_value=1, max_value=200, value=32)
    #     smoothing_period = st.slider('Smoothing Period', min_value=1, max_value=20, value=8)
    #     alta = st.slider('Alta', min_value=0.5, max_value=1.0, value=0.99)
    #     baixa = st.slider('Baixa', min_value=-1.0, max_value=-0.5, value=-0.99)
    #     Buysignal = st.slider('Buy Signal', min_value=-1.0, max_value=0.0, value=-0.9)
    #     Sellsignal = st.slider('Sell Signal', min_value=0.5, max_value=1.0, value=0.96)


    async with aiohttp.ClientSession() as session:
        df_price = await fetch_data(session, selected_symbol, selected_interval, selected_limit)

    with st.sidebar:
        st.title('Alpha Quant')
        RSI_Period = st.sidebar.slider('RSI Length', 1, 100, 14)
        SF = st.sidebar.slider('RSI Smoothing', 1, 20, 5)
        QQE = st.sidebar.slider('Fast Quant Factor', 1.0, 10.0, 4.238)
        drift = st.sidebar.slider('Drift', 1, 10, 1)
        st.title('ATR-VWMA Trend Signal')
        atr_period = st.sidebar.slider('ATR Period', min_value=1, max_value=100, value=10)
        factor = st.sidebar.slider('Factor', min_value=1.0, max_value=10.0, value=3.0)
        alpha = st.sidebar.slider('Alpha', min_value=0.0, max_value=1.0, value=0.7)
        x1 = st.sidebar.slider('VWMA Period', min_value=1, max_value=100, value=23)
        st.title('Price Transformation')
        length = st.sidebar.slider('Price Transformation Period', min_value=1, max_value=200, value=32)
        smoothing_period = st.sidebar.slider('Smoothing Period', min_value=1, max_value=20, value=8)
        alta = st.sidebar.slider('Upper cut', min_value=0.5, max_value=1.0, value=0.99)
        baixa = st.sidebar.slider('Lower cut', min_value=-1.0, max_value=-0.5, value=-0.99)
        Buysignal = st.sidebar.slider('Buy Signal', min_value=-1.0, max_value=0.0, value=-0.9)
        Sellsignal = st.sidebar.slider('Sell Signal', min_value=0.5, max_value=1.0, value=0.96)


    df_qqe = ta.qqe(df_price['Close'], length=RSI_Period, smooth=SF, factor=QQE, drift=drift)
    # Adicionar a coluna QQE ao DataFrame df
    qqe_column_name = f"QQE_{RSI_Period}_{SF}_{QQE}"
    rsima_column_name = f"QQE_{RSI_Period}_{SF}_{QQE}_RSIMA"
    qqe_long_column_name = f"QQEl_{RSI_Period}_{SF}_{QQE}"
    qqe_short_column_name = f"QQEs_{RSI_Period}_{SF}_{QQE}"

    df_price["QQE"] = df_qqe[qqe_column_name]
    df_price["RSIMA"] = df_qqe[rsima_column_name]
    df_price["QQE_LONG"] = df_qqe[qqe_long_column_name]
    df_price["QQE_SHORT"] = df_qqe[qqe_short_column_name]

    # Plotar gráfico
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.7, 0.3])

    # Adicionar candlestick
    fig.add_trace(go.Candlestick(x=df_price.index,
                                open=df_price['Open'],
                                high=df_price['High'],
                                low=df_price['Low'],
                                close=df_price['Close'],
                                increasing_line_color='#008DDA',
                                decreasing_line_color='red',  
                                increasing_fillcolor='#00bcd4',  
                                decreasing_fillcolor='#EF4040',  
                                showlegend=False,
                                name=selected_symbol), row=1, col=1)

    #opacity = 0.7,

    fig.add_trace(go.Scatter(x=df_price.index, y=df_price["QQE"], mode='lines', yaxis='y2', name='Alpha Quant', line=dict(color='orange', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_price.index, y=df_price["RSIMA"], mode='lines', yaxis='y2', name='RSI Smoothing', line=dict(color='gray', width=1.5, dash='dot')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_price.index, y=df_price["QQE_LONG"], mode='lines', yaxis='y2', name='Long', line=dict(color='#21BF73', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_price.index, y=df_price["QQE_SHORT"], mode='lines', yaxis='y2', name='Short', line=dict(color='#D83F31', width=1.5)), row=2, col=1)

    # Identificar os sinais de compra (long) e venda (short) baseados no cruzamento entre QQE e RSIMA
    df_price["Signal"] = np.where((df_price["QQE"] > df_price["RSIMA"]) & (df_price["QQE"].shift(1) <= df_price["RSIMA"].shift(1)), -1, np.nan) # Buy signal
    df_price["Signal"] = np.where((df_price["QQE"] < df_price["RSIMA"]) & (df_price["QQE"].shift(1) >= df_price["RSIMA"].shift(1)), 1, df_price["Signal"]) # Sell signal

    # Plotar apenas os sinais de compra (long) e venda (short)
    buy_signals = df_price[df_price["Signal"] == 1]
    sell_signals = df_price[df_price["Signal"] == -1]

    # Calcular o desvio padrão dos preços
    price_std = df_price["Close"].std()

    # Definir o fator de ajuste do espaçamento
    spacing_factor = 0.05 * price_std  # Você pode ajustar o multiplicador conforme necessário

    # Criar figuras para os sinais de compra (long)
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals["Low"] - spacing_factor, mode='markers', yaxis='y1',
                                name='Buy Signal', marker=dict(color='green', symbol='triangle-up', size=12),
                                text='Long', hoverinfo='text', showlegend=False,), row=1, col=1)

    # Criar figuras para os sinais de venda (short)
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals["High"] + spacing_factor, mode='markers', yaxis='y1',
                                name='Sell Signal', marker=dict(color='red', symbol='triangle-down', size=12),
                                text='Short', hoverinfo='text', showlegend=False,), row=1, col=1)

    # Adicionar anotações para os sinais de compra
    for i, buy_signal in buy_signals.iterrows():
        fig.add_annotation(x=i, y=buy_signal["Low"] - spacing_factor, text="Long", showarrow=False, font=dict(color="white"), xanchor="center", yanchor="top", yshift=-1, bgcolor="rgba(33, 191, 115, 0.7)", bordercolor="#21BF73", borderwidth=1, borderpad=2)

    # Adicionar anotações para os sinais de venda
    for i, sell_signal in sell_signals.iterrows():
        fig.add_annotation(x=i, y=sell_signal["High"] + spacing_factor, text="Short", showarrow=False, font=dict(color="white"), xanchor="center", yanchor="bottom", yshift=1, bgcolor="rgba(216, 63, 49, 0.7)", bordercolor="#D83F31", borderwidth=1, borderpad=2)
        
    fig.update_layout(
        title=dict(
            text=f"Alpha Quant Signal: {selected_symbol}",
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
        height=800,
        #template="simple_white",
        yaxis=dict(showgrid=False, zeroline=False, tickprefix="$", side='right'),
        yaxis2=dict(side='right'),
        #xaxis=dict(gridcolor='#0a0c11'),
        xaxis_rangeslider_visible=False,
        images=[dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.4,
            y=0.78,
            sizex=0.35,
            sizey=0.35,
            opacity=0.4,
            layer="below"
        )]
    )
    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.2,
    xanchor="left",
    x=0.01,
    bgcolor="rgba(255, 255, 255, 0.6)",
    font=dict(
            family="Arial",
            size=12
            #color="black"),
    )))
    fig.update_layout(hoverlabel=dict(namelength=-1), hovermode='x')

    update_date_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    fig.add_annotation(
        x=0,
        y=-0.11,
        xref='paper',
        yref='paper',
        text=f'Update: {update_date_formatted} (UTC)',
        showarrow=False,
        font=dict(color='#9BABB8', size=9)
    )

    fig.add_annotation(
        x=1,
        y=-0.11,
        xref='paper',
        yref='paper',
        text='© Dominando Cripto All rights reserved',
        showarrow=False,
        font=dict(color='#9BABB8', size=9)
    )

    config = {
    'scrollZoom': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'resetViews', 'toImage'],
    'toImageButtonOptions': {
       'format': 'png',  # one of png, svg, jpeg, webp
       'filename': f"Alpha Quant Signal: {selected_symbol}",
       'height': 900,
       'width': 1600,
       'scale': 1
        }
}

    st.plotly_chart(fig, use_container_width=True, config=config)


    # Cálculo do ATR manualmente
    df_price['TR'] = df_price['High'] - df_price['Low']
    df_price['High_Close'] = abs(df_price['High'] - df_price['Close'].shift(1))
    df_price['Low_Close'] = abs(df_price['Low'] - df_price['Close'].shift(1))
    df_price['TR'] = df_price[['TR', 'High_Close', 'Low_Close']].max(axis=1)
    df_price['ATR'] = df_price['TR'].rolling(atr_period).mean()

    # Verificando se o ATR foi calculado corretamente
    if 'ATR' not in df_price.columns:
        st.error(f"Erro ao calcular o ATR com período {atr_period}")
        return

    # Adicionando o ATR calculado ao dataframe
    df_price[f'ATR_{atr_period}'] = df_price['ATR']

    df_price.ta.supertrend(length=atr_period, multiplier=factor, append=True)
    df_price['HL2'] = (df_price['High'] + df_price['Low']) / 2
    a1 = df_price.ta.vwma(df_price['HL2'] * df_price['Volume'], math.ceil(x1 / 4)) / df_price.ta.vwma(df_price['Volume'], math.ceil(x1 / 4))
    a2 = df_price.ta.vwma(df_price['HL2'] * df_price['Volume'], math.ceil(x1 / 2)) / df_price.ta.vwma(df_price['Volume'], math.ceil(x1 / 2))
    a3 = 2 * a1 - a2
    df_price.ta.vwma(length=x1, append=True, column_name='VWMA')
    a4 = df_price.ta.vwma(a3, length=x1)
    b1 = df_price.ta.sma(length=x1, append=True)
    #df_price[f'VWMA_{x1}'] = df_price['VWMA']

    
    # Verificando se o ATR foi calculado corretamente
    if f'ATR_{atr_period}' not in df_price.columns:
        st.error(f"Erro ao calcular o ATR com período {atr_period}")
        return


    # Corrigindo a referência para o ATR
    buy_condition = (a4 <= df_price['Close'] - df_price[f'ATR_{atr_period}'] * alpha) & (df_price['Close'] > b1)  
    sell_condition = (a4 >= df_price['Close'] + df_price[f'ATR_{atr_period}'] * alpha) & (df_price['Close'] < b1)  

    xs = np.zeros(len(df_price))
    in_position = 0  

    for i in range(len(df_price)):
        if buy_condition[i]:
            if in_position <= 0:
                xs[i] = 1
                in_position = 1
            else:
                xs[i] = 0  
        elif sell_condition[i]:
            if in_position >= 0:  
                xs[i] = -1
                in_position = -1
            else:
                xs[i] = 0  
        else:
            xs[i] = 0  

    df_price['xs'] = xs

    price_std = df_price["Close"].std()
    spacing_factor = 0.05 * price_std 

    buy_points = df_price[df_price['xs'] == 1]
    sell_points = df_price[df_price['xs'] == -1]

    fig = go.Figure()

    fig = go.Figure(data=[go.Candlestick(x=df_price.index,
                                open=df_price['Open'],
                                high=df_price['High'],
                                low=df_price['Low'],
                                close=df_price['Close'],
                                increasing_line_color='#008DDA',
                                decreasing_line_color='red',  
                                increasing_fillcolor='#00bcd4',  
                                decreasing_fillcolor='#EF4040',   
                                #opacity = 0.7,
                                name=selected_symbol)])

    fig.add_trace(go.Scatter(x=buy_points.index, y=buy_points['Low']- spacing_factor,
                             mode='markers', name='Long', marker_line_width=1.5, marker_line_color="gray",  marker=dict(symbol='triangle-up', color='green', size=15)))
    fig.add_trace(go.Scatter(x=sell_points.index, y=sell_points['High']+ spacing_factor,
                             mode='markers', name='Short', marker_line_width=1.5, marker_line_color="gray",marker=dict(symbol='triangle-down', color='red', size=15)))

    fig.add_trace(go.Scatter(x=df_price.index, y=df_price['SUPERT_{}_{}'.format(atr_period, factor)],
                             mode='lines', name='SuperTrend', #visible='legendonly',
                             line=dict(color='#A5DD9B',width=1.5)))

    fig.add_trace(go.Scatter(x=df_price.index, y=df_price[f'VWMA_{x1}'],
                             mode='lines', name='Super VWMA', textposition='bottom center',
                             line=dict(color='#FBA834',width=1.5)))

    # Adicionar anotações para os sinais de compra
    for i, buy_signal in buy_points.iterrows():
        fig.add_annotation(x=buy_signal.name, y=buy_signal['Low'] - spacing_factor, text="Long", showarrow=False, font=dict(color="white"), xanchor="center", yanchor="top", yshift=-1, bgcolor="rgba(33, 191, 115, 0.7)", bordercolor="#21BF73", borderwidth=1, borderpad=2)

    # Adicionar anotações para os sinais de venda
    for i, sell_signal in sell_points.iterrows():
        fig.add_annotation(x=sell_signal.name, y=sell_signal['High'] + spacing_factor, text="Short", showarrow=False, font=dict(color="white"), xanchor="center", yanchor="bottom", yshift=1, bgcolor="rgba(216, 63, 49, 0.7)", bordercolor="#D83F31", borderwidth=1, borderpad=2)


    fig.update_layout(
        title=dict(
            text=f"ATR-VWMA Trend Signal: {selected_symbol}",
            font=dict(
                family='Arial',
                size=22,
            ),
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        #template="simple_white",
        yaxis=dict(showgrid=False, side='right', zeroline=False, tickprefix="$"), 
        #xaxis=dict(gridcolor='#0a0c11'),
        width=1600,
        height=800,
        images=[dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.4,
            y=0.78,
            sizex=0.35,
            sizey=0.35,
            opacity=0.4,
            layer="below"
        )]
    )

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01,
    bgcolor="rgba(255, 255, 255, 0.6)",
    font=dict(
            family="Arial",
            size=12
            #color="black"),
    )))

    fig.update_layout(hoverlabel=dict(namelength=-1), hovermode='x')

    update_date_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    fig.add_annotation(
        x=0,
        y=-0.11,
        xref='paper',
        yref='paper',
        text=f'Update: {update_date_formatted} (UTC)',
        showarrow=False,
        font=dict(color='#9BABB8', size=9)
    )

    fig.add_annotation(
        x=1,
        y=-0.11,
        xref='paper',
        yref='paper',
        text='© Dominando Cripto All rights reserved',
        showarrow=False,
        font=dict(color='#9BABB8', size=9)
    )

    st.plotly_chart(fig, use_container_width=True)


    fisher_data = ta.fisher(df_price["Low"], df_price["High"], length=length, signal=1, offset=0)
    combined_data = pd.concat([df_price, fisher_data], axis=1)

    def inverse_fisher_transform(x):
        result = (np.exp(2 * x) - 1) / (np.exp(2 * x) + 1)
        return -1 if result < baixa else (1 if result >= alta else round(result, 2))

     
    #smoothed_series = combined_data[f"FISHERT_{length}_1"].rolling(window=smoothing_period).mean().fillna(method='bfill')
    #smoothed_series = combined_data[f"FISHERT_{length}_1"].ewm(span=smoothing_period, min_periods=smoothing_period).mean().fillna(method='bfill')
    smoothed_series = combined_data[f"FISHERT_{length}_1"].ewm(span=smoothing_period).mean().fillna(method='bfill')


    combined_data['Inverse_Fisher'] = smoothed_series.apply(inverse_fisher_transform)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=combined_data.index, y=combined_data['Close'], mode='markers+lines', name='Price', line=dict(color='#35374B'),marker=dict(
        color=combined_data['Inverse_Fisher'],
        colorscale='Bluered',
        colorbar=dict(
            title='PTOi'
        ),
        size=6,
        symbol='circle'
    )), row=1, col=1)

    fig.add_trace(go.Scatter(x=combined_data.index, y=combined_data['Inverse_Fisher'], mode='lines', name='IFT', line=dict(color='orange')), row=2, col=1)

    combined_data['Price_Delta_3days'] = combined_data['Close'].pct_change(periods=2) * 100
    combined_data['buy_signal'] = (combined_data['Inverse_Fisher'] > -1) & (combined_data['Inverse_Fisher'].shift() <= Buysignal) & (combined_data['Price_Delta_3days'] > 1)
    combined_data['sell_signal'] = (combined_data['Inverse_Fisher'] < 0.99) & (combined_data['Inverse_Fisher'].shift(1) >= Sellsignal)

    fig.add_trace(go.Scatter(x=combined_data.index[combined_data['buy_signal']], y=combined_data['Inverse_Fisher'][combined_data['buy_signal']], mode='markers', marker=dict(color='green', size=10), name='Buy'), row=2, col=1)
    fig.add_trace(go.Scatter(x=combined_data.index[combined_data['sell_signal']], y=combined_data['Inverse_Fisher'][combined_data['sell_signal']], mode='markers', marker=dict(color='red', size=10), name='Sell'), row=2, col=1)

    fig.update_yaxes(title_text="Price", row=1, col=1, type="log")
    fig.update_yaxes(title_text="Fisher Transform", row=2, col=1, secondary_y=True)

    fig.update_layout(
        title=dict(
            text=f"Price Transformation Oscillator: {selected_symbol}",
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
        height=800,
        #template="simple_white",
        yaxis=dict(showgrid=False, zeroline=False, tickprefix="$", type="log"),
        xaxis=dict(gridcolor='#0a0c11'),
        images=[dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.4,
            y=0.78,
            sizex=0.35,
            sizey=0.35,
            opacity=0.4,
            layer="below"
        )]
    )
    fig.update_layout(showlegend=False)

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


async def update_data(selected_symbol, selected_interval, selected_limit):
    async with aiohttp.ClientSession() as session:
        df = await fetch_data(session, selected_symbol, selected_interval, selected_limit)
        # Atualizar o gráfico ou fazer qualquer outra coisa com os novos dados


if __name__ == "__main__":
    asyncio.run(main())

with st.expander("About the Indicators"):
    st.markdown("""
        **Alpha Quant Signal:** The Alpha Quant Signal is a powerful indicator for Long and Short signals. Its principles derive from recursive Volatility based on ATR, Smoothed RSI, and Momentum indicators such as Quantitative Qualitative Estimation and squeeze pro. We consider it the most assertive signal indicator of all, as it takes into account a range of calculations to generate the signal. In backtesting, its results have shown an accuracy rate between 92% and 96% with 73 Trades. It is necessary to adjust the parameters according to the selected TimeFrame and for each pair of Altcoins, as each project has its own statistical volatility.
        
        **ATR-VWMA Trend Signal:** The "ATR-VWMA Trend Signal" is an advanced technical indicator that combines the Average True Range (ATR), the Volume Weighted Moving Average (VWMA), and the Supertrend to identify short-term trend changes. With an impressive accuracy rate of 92%, it stands out as one of the most powerful technical indicators, providing valuable insights for traders and investors in the search for profitable opportunities.
        
        **Price Transformation Oscillator:** The "Price Transformation" indicator is a technical tool for analyzing asset price data, notable for its high accuracy. This indicator closely monitors price variations over a specific period and provides buy and sell signals based on rigorous criteria. What sets it apart is the custom Fisher inverse transform developed by Dominando Cripto, which further enhances its accuracy. This personalized approach is valuable for investors and traders seeking to identify trading opportunities with exceptional reliability.
    """)



hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)    





