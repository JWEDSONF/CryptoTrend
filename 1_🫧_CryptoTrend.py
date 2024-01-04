import streamlit as st
import pandas as pd
import numpy as np
from data_processing import processar_dados
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_loader import load_data
from table_formatters import colunas_dolar, colunas_percentual, dollar_formatter, percent_formatter
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
from streamlit_plotly_events import plotly_events

st.set_page_config(
    page_title="CryptoTrend",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://academy.dominandocripto.com',
        'Report a bug': "https://academy.dominandocripto.com",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
st.title('CryptoTrend')

# Inicializar estados da sessão para seleções do gráfico
if 'x_axis_column' not in st.session_state:
    st.session_state['x_axis_column'] = 'Rank'
if 'y_axis_column' not in st.session_state:
    st.session_state['y_axis_column'] = 'rsi1h'
if 'z_axis_column' not in st.session_state:
    st.session_state['z_axis_column'] = 'priceChangeM5'
if 'color_column' not in st.session_state:
    st.session_state['color_column'] = None
if 'size_column' not in st.session_state:
    st.session_state['size_column'] = None
if 'tipo_grafico' not in st.session_state:
    st.session_state['tipo_grafico'] = '2D'

# Armazenar seleções atuais
x_axis_selection = st.session_state['x_axis_column']
y_axis_selection = st.session_state['y_axis_column']
z_axis_selection = st.session_state['z_axis_column']
color_column_selection = st.session_state['color_column']
size_column_selection = st.session_state['size_column']

with st.spinner('Loading data...'):
    df_final = load_data()

   

x_axis_options = df_final.select_dtypes(include=[np.number]).columns.tolist()
y_axis_options = df_final.select_dtypes(include=[np.number]).columns.tolist()

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
    color_options = [None] + list(df_final.columns)
    st.session_state['color_column'] = st.selectbox(add_icon_to_selector('Color', '🎨'), color_options, index=color_options.index(st.session_state['color_column']))

valid_size_columns = [col for col in df_final.columns if df_final[col].dtype in ['float64', 'int64'] and df_final[col].gt(0).any()]
size_options = [None] + valid_size_columns

if st.session_state['tipo_grafico'] == '3D🔥':
    with col5:
        st.session_state['size_column'] = st.selectbox(add_icon_to_selector('Size', '📏'), size_options, index=size_options.index(st.session_state['size_column']))
else:
    with col3:
        st.session_state['size_column'] = st.selectbox(add_icon_to_selector('Size', '📏'), size_options, index=size_options.index(st.session_state['size_column']))


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
                     color_continuous_scale=px.colors.sequential.Viridis, height=800,
                     hover_data={'priceUSD': ':$,.2f',
                                'Open Interest': ':$,.0f',
                                'Funding Rate': ':,.0%',                            
                                # 'Total Liquidation 24h': ':$,.0f',
                                # 'Long liquidation 24h': ':$,.0f',
                                # 'Short liquidation 24h': ':$,.0f',
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
                           size=st.session_state['size_column'], hover_name='Crypto', text='Crypto', color_continuous_scale=px.colors.sequential.Viridis,
                           hover_data={'priceUSD': ':$,.2f',
                                'Open Interest': ':$,.0f',
                                'Funding Rate': ':,.0%',                            
                                # 'Total Liquidation 24h': ':$,.0f',
                                # 'Long liquidation 24h': ':$,.0f',
                                # 'Short liquidation 24h': ':$,.0f',
                                # 'Liquidated traders':':,.0f',
                                })
    fig_3d.update_traces(textposition='top center', textfont=dict(size=10))
    fig_3d.add_layout_image(
        dict(
            source='https://i.imgur.com/GyN6BI4.png',
            xref="paper",
            yref="paper",
            x=0.75,
            y=0.3,
            sizex=0.25,
            sizey=0.24,
            opacity=0.3,
            layer="below"
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True, config=config)


hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 



