import streamlit as st
import pandas as pd
import numpy as np
from data_processing import processar_dados
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_loader import load_data
from table_formatters import colunas_dolar, colunas_percentual, dollar_formatter, percent_formatter
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode


st.set_page_config(
    page_title="Crypto Trend",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://forms.gle/a9X3vpug4AXGV3JP7",
        'About': """
        CryptoTrend is a powerful and fully visual charting tool that revolutionizes cryptocurrency market analysis. 
        It allows users to select various metrics for the x, y, and z axes in a scatter plot, creating an innovative indicator for the cryptocurrency market. 
        Additionally, the tool offers the flexibility to change the color and size of the plot bubbles, providing a unique perspective to aid in the selection of cryptocurrencies and strategies. 
        What sets CryptoTrend apart is its 3D version, making it the world's first 3D screener, offering sharp analysts a groundbreaking 3D perspective. 
        This tool encourages users to let their creativity flow when choosing cryptocurrencies, offering an unmatched analytical experience.

        Dominando Cripto - All rights reserved.
        """
    }
)

st.title('CryptoTrend')
with st.spinner('Loading data...'):
    df_final = load_data()

# Inicializar estados da sessão para seleções do gráfico
if 'x_axis_column' not in st.session_state:
    st.session_state['x_axis_column'] = 'Rank'
if 'y_axis_column' not in st.session_state:
    st.session_state['y_axis_column'] = 'rsi1h'
if 'z_axis_column' not in st.session_state:
    st.session_state['z_axis_column'] = 'Price 24h'
if 'color_column' not in st.session_state:
    st.session_state['color_column'] = None
if 'size_column' not in st.session_state:
    st.session_state['size_column'] = None
if 'tipo_grafico' not in st.session_state:
    st.session_state['tipo_grafico'] = '2D'

# Verifique se 'size_column' foi definido antes de usar
if st.session_state.get('size_column') and st.session_state['size_column'] in df_final.columns:
    # Substituir NaN na coluna de tamanho por um valor padrão (por exemplo, 0)
    df_final[st.session_state['size_column']] = df_final[st.session_state['size_column']].fillna(0)
    
    # Garantir que os valores são numéricos (converter para float, por exemplo)
    df_final[st.session_state['size_column']] = df_final[st.session_state['size_column']].astype(float)


# Armazenar seleções atuais
x_axis_selection = st.session_state['x_axis_column']
y_axis_selection = st.session_state['y_axis_column']
z_axis_selection = st.session_state['z_axis_column']
color_column_selection = st.session_state['color_column']
size_column_selection = st.session_state['size_column']


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

    

x_axis_options = df_final.select_dtypes(include=[np.number]).columns.tolist()
y_axis_options = df_final.select_dtypes(include=[np.number]).columns.tolist()

# Criando uma nova lista de opções para o filtro de cor
colunas_excluidas = ['Coin', 'exchangeName','Crypto','coinImage','symbol','symbol_name']
color_options = [None] + [col for col in df_final.columns if col not in colunas_excluidas]



def add_icon_to_selector(selector_name, icon_unicode):
    return f'{icon_unicode} {selector_name}'

st.session_state['tipo_grafico'] = st.radio("Choose the chart type::", ('2D', '3D🔥'), horizontal=True)

if st.session_state['tipo_grafico'] == '2D':
    col1, col2, col3, col4 = st.columns(4)
else:
    col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.session_state['x_axis_column'] = st.selectbox(add_icon_to_selector('X-axis', '🔍'), x_axis_options, index=x_axis_options.index(st.session_state['x_axis_column']))

with col2:
    st.session_state['y_axis_column'] = st.selectbox(add_icon_to_selector('Y-axis', '📊'), y_axis_options, index=y_axis_options.index(st.session_state['y_axis_column']))

if st.session_state['tipo_grafico'] == '3D🔥':
    z_axis_options = df_final.columns.tolist()
    with col3:
        st.session_state['z_axis_column'] = st.selectbox(add_icon_to_selector('Z-axis', '🔼'), z_axis_options, index=z_axis_options.index(st.session_state['z_axis_column']))

with col4:
    st.session_state['color_column'] = st.selectbox(add_icon_to_selector('Color', '🎨'), color_options, index=color_options.index(st.session_state['color_column']))


colunas_para_tamanho = ['OI/Market Cap', 'Volume24h/OI','Open Interest','Volume24h/Market Cap','Top Trader Sentiment','Short-Term RSI Trend','Long-Term RSI Trend','rsi5min','rsi15min', 'rsi30min', 'rsi1h', 'rsi2h', 'rsi4h', 'rsi24h','Liquidations 24h/OI', 'Long Liquidations/OI', 'Short Liquidations/OI','Liquidation 1h', 'Long Liquidation 1h', 'Short Liquidation 1h', 'Liquidation 4h', 'Long Liquidation 4h', 'Short Liquidation 4h', 'Liquidation 12h', 'Long Liquidation 12h', 'Short Liquidation 12h', 'Liquidation 24h', 'Long Liquidation 24h', 'Short Liquidation 24h']
# Opções de tamanho para os gráficos
size_options = [None] + colunas_para_tamanho
# Adicionar o selectbox para escolher a coluna de tamanho
if st.session_state['tipo_grafico'] == '3D🔥':
    with col5:
        st.session_state['size_column'] = st.selectbox(add_icon_to_selector('Size', '📏'), size_options, index=size_options.index(st.session_state.get('size_column', None)))
else:
    with col3:
        st.session_state['size_column'] = st.selectbox(add_icon_to_selector('Size', '📏'), size_options, index=size_options.index(st.session_state.get('size_column', None)))

size_column = st.session_state.get('size_column')
if size_column and size_column in df_final.columns:
    # Substituir NaN na coluna de tamanho por um valor padrão (por exemplo, 0)
    df_final[size_column] = df_final[size_column].fillna(0)



#df_final.fillna(NaN, inplace=True)


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

# Verifique qual gráfico foi selecionado e exiba-o
if st.session_state['tipo_grafico'] == '2D':
    # [Seu código existente para criar e exibir o gráfico de dispersão 2D]
    fig = px.scatter(df_final, x=st.session_state['x_axis_column'], y=st.session_state['y_axis_column'], hover_name='Crypto', text='Crypto',
                     title=f"{st.session_state['x_axis_column']} vs {st.session_state['y_axis_column']}", color=st.session_state['color_column'], size=st.session_state['size_column'],
                     color_continuous_scale=px.colors.diverging.Portland_r, height=800, color_discrete_map={"Bearish": "#FF0060",
                                                 "Bullish": "#00DFA2",
                                                 "Below": "#FF0060",
                                                 "Inside": "#0079FF",
                                                 "Above": "#00DFA2",
                                                 None: "#0079FF"},
                     hover_data={'Price USD': ':$,.2f',
                                'Open Interest': ':$,.0f',
                                'Funding Rate': ':,.0%',                            
                                'Liquidation 24h': ':$,.0f',
                                'Long Liquidation 24h': ':$,.0f',
                                'Short Liquidation 24h': ':$,.0f',
                                # 'Liquidated traders':':,.0f',
                                })
    fig.update_traces(textposition='top center', textfont=dict(size=10))
    fig.add_layout_image(
        dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.75,
            y=0.3,
            sizex=0.3,
            sizey=0.3,
            opacity=0.30,
            layer="below"
        )
    )
    st.plotly_chart(fig, use_container_width=True, config=config)
elif st.session_state['tipo_grafico'] == '3D🔥':
    # Crie e exiba o gráfico de dispersão 3D
    fig_3d = px.scatter_3d(df_final, x=st.session_state['x_axis_column'], y=st.session_state['y_axis_column'], z=st.session_state['z_axis_column'],
                           title=f"{st.session_state['x_axis_column']} vs {st.session_state['y_axis_column']} vs {st.session_state['z_axis_column']}", color=st.session_state['color_column'],
                           size=st.session_state['size_column'], hover_name='Crypto', text='Crypto', color_continuous_scale=px.colors.diverging.Portland_r,
                           color_discrete_map={"Bearish": "#FF0060",
                                                 "Bullish": "#00DFA2",
                                                 "Below": "#FF0060",
                                                 "Inside": "#0079FF",
                                                 "Above": "#00DFA2",
                                                  None: "#0079FF"},
                           hover_data={'Price USD': ':$,.2f',
                                'Open Interest': ':$,.0f',
                                'Funding Rate': ':,.0%',                            
                                'Liquidation 24h': ':$,.0f',
                                'Long Liquidation 24h': ':$,.0f',
                                'Short Liquidation 24h': ':$,.0f',
                                # 'Liquidated traders':':,.0f',
                                })
    fig_3d.update_traces(textposition='top center', textfont=dict(size=10))
    fig_3d.add_layout_image(
        dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.78,
            y=0.33,
            sizex=0.25,
            sizey=0.25,
            opacity=0.26,
            layer="below"
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True, config=config)

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



