import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import processar_dados
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_loader import load_data
import requests

st.set_page_config(
    page_title="Crypto Compare",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://forms.gle/a9X3vpug4AXGV3JP7",
        'About': """
            **Crypto Compare: Comprehensive Cryptocurrency Analysis**

            Crypto Compare is a state-of-the-art tool designed to deliver extensive comparative analyses across a diverse range of over 360 cryptocurrencies. This innovative platform caters to both seasoned investors and cryptocurrency enthusiasts keen on dissecting the unique features and trends of various digital currencies.

            Key Features:
            - **In-Depth Comparative Analysis:** Explore and compare detailed aspects of different cryptocurrencies.
            - **Intuitive User Interface:** Enjoy a user-friendly experience that simplifies data exploration and comparison.
            - **Detailed Insights:** Delve into the nuances and characteristics of each cryptocurrency, aiding in informed decision-making.
            - **Market Trends and Patterns:** Identify and understand market behaviors, trends, and patterns across a wide spectrum of digital currencies.

            With Crypto Compare, users gain a powerful analytical tool, offering a clearer picture of the cryptocurrency landscape. This platform is instrumental in guiding strategic investment decisions and enhancing market knowledge.
            
            Dominando Cripto - All rights reserved.
        """
    }
)
st.title('Crypto Compare - Dashboard')

with st.spinner('Loading data...'):
    df_final = load_data()

col1, col2 = st.columns(2)

# Seletor de moedas na coluna 1
with col1:
    opcoes_de_moedas = df_final['Crypto'].unique()
    moedas_pre_selecionadas = opcoes_de_moedas[:10]  # Pré-selecionar as top 10 primeiras moedas
    moedas_selecionadas = st.multiselect('Select the coins', opcoes_de_moedas, default=moedas_pre_selecionadas)

# Seletor de métricas na coluna 2
with col2:
    metricas_disponiveis = ['Open Interest', 'Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m', 'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h', 'Open Interest 2d', 'Open Interest 3d', 'Open Interest 7d','OI/Market Cap','Volume24h/Market Cap','Volume24h/OI', 'Short-Term OI Trend', 'Long-Term OI Trend', 'Top Trader Sentiment', 'Top Trader LSR Account', 'Top Trader LSR Position','Long Short Ratio', 'LSR 5m','LSR 15m', 'LSR 30m', 'LSR 1h', 'LSR 4h','Long Ratio', 'Short Ratio', 'Long vs Short Real Time', 'Funding Rate', 'Funding Rate','Funding Rate Risk','Liquidations 24h/OI', 'Long Liquidations/OI', 'Short Liquidations/OI','Price 5m','Price 15m','Price 30m','Price 1h','Price 2h','Price 4h','Price 6h','Price 8h','Price 12h','Price 24h','price1week','price2week','price30day','price_year_to_date','price1year','Short-Term RSI Trend','Long-Term RSI Trend','rsi5min', 'rsi15min', 'rsi30min', 'rsi1h', 'rsi2h', 'rsi4h', 'rsi24h','Market Cap','circulatingSupply', 'totalSupply','maxSupply','Liquidation 1h', 'Long Liquidation 1h', 'Short Liquidation 1h', 'Liquidation 4h', 'Long Liquidation 4h', 'Short Liquidation 4h', 'Liquidation 12h', 'Long Liquidation 12h', 'Short Liquidation 12h', 'Liquidation 24h', 'Long Liquidation 24h', 'Short Liquidation 24h']
    metricas_pre_selecionadas = ['OI/Market Cap','Volume24h/OI','Volume24h/Market Cap','Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m', 'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h']
    metricas_selecionadas = st.multiselect('Select metrics to display', metricas_disponiveis, default=metricas_pre_selecionadas)


# Função para criar gráficos comparativos
def criar_grafico_comparativo(df, moedas, metrica, titulo, orientacao='v'):
    df_filtrado = df[df['Crypto'].isin(moedas)]
    
    # Adicionando uma coluna temporária para definir a cor das barras
    df_filtrado['Color'] = df_filtrado[metrica].apply(lambda x: 'Negative' if x < 0 else 'Positive')

    if orientacao == 'v':
        grafico = px.bar(df_filtrado, x='Crypto', y=metrica, title=titulo,
                         labels={'value': metrica}, color='Color', 
                         color_discrete_map={'Positive': '#3AB0FF', 'Negative': '#F87474'})
    else:
        grafico = px.bar(df_filtrado, y='Crypto', x=metrica, title=titulo,
                         labels={'value': metrica}, color='Color', 
                         color_discrete_map={'Positive': '#3AB0FF', 'Negative': '#F87474'},
                         orientation='h')
    
    grafico.add_layout_image(
        dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.35,
            y=0.7,
            sizex=0.35,
            sizey=0.35,
            opacity=0.40,
            layer="below"
        )
    )
    grafico.update_layout(showlegend=False)
    
    # Removendo a coluna temporária 'Cor' antes de retornar o gráfico
    df_filtrado.drop('Color', axis=1, inplace=True)

    return grafico



config = {
    'scrollZoom': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'resetViews', 'toImage'],
    'toImageButtonOptions': {
       'format': 'png',  # one of png, svg, jpeg, webp
       'filename': 'Dominando Cripto - Screener',
       'height': 900,
       'width': 1600,
       'scale': 1
        }
}

# Inicializando os estados dos gráficos
for metrica in metricas_selecionadas:
    if f'orientacao_{metrica}' not in st.session_state:
        st.session_state[f'orientacao_{metrica}'] = 'v'

# Criar e exibir os gráficos com botões para alternar orientação
for i in range(0, len(metricas_selecionadas), 2):
    row = st.columns([0.6, 5, 0.6, 5])
    for j in range(2):
        idx = i + j
        if idx < len(metricas_selecionadas):
            metrica = metricas_selecionadas[idx]
            with row[j * 2]:
                if st.button('↷', key=f'botao_{metrica}'):
                    st.session_state[f'orientacao_{metrica}'] = 'h' if st.session_state[f'orientacao_{metrica}'] == 'v' else 'v'
            with row[j * 2 + 1]:
                grafico = criar_grafico_comparativo(df_final, moedas_selecionadas, metrica, metrica, st.session_state[f'orientacao_{metrica}'])
                st.plotly_chart(grafico, use_container_width=True, config=config)



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