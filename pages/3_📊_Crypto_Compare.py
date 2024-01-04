import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import processar_dados
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_loader import load_data
import requests

st.set_page_config(layout="wide")
st.title('Crypto Compare - Dashboard')

with st.spinner('Loading data...'):
    df_final = load_data()

col1, col2 = st.columns(2)

# Seletor de moedas na coluna 1
with col1:
    opcoes_de_moedas = df_final['Crypto'].unique()
    moedas_pre_selecionadas = opcoes_de_moedas[:10]  # Pré-selecionar as top 10 primeiras moedas
    moedas_selecionadas = st.multiselect('"Select the coins', opcoes_de_moedas, default=moedas_pre_selecionadas)

# Seletor de métricas na coluna 2
with col2:
    metricas_disponiveis = ['Open Interest', 'Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m', 'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h', 'Open Interest 2d', 'Open Interest 3d', 'Open Interest 7d','OI/Market Cap', 'Short-Term OI Trend', 'Long-Term OI Trend', 'Top Trader Sentiment', 'Long Ratio', 'Short Ratio', 'Long vs Short Real Time', 'Funding Rate', 'Long Short Ratio', 'LSR 5m','LSR 15m', 'LSR 30m', 'LSR 1h', 'LSR 4h', 'Funding Rate']
    metricas_pre_selecionadas = ['Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m', 'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h']
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


