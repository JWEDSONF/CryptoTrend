import pandas as pd
import requests

# URLs para diferentes intervalos
urls = [    
    "https://coinank.com/api/priceChange/history?interval=week&baseCoin=BTC",
    "https://coinank.com/api/priceChange/history?interval=month&baseCoin=BTC",
    "https://coinank.com/api/priceChange/history?interval=quarterly&baseCoin=BTC"
]

# Lista para armazenar os DataFrames de cada intervalo
dfs = []

# Loop sobre as URLs
for url in urls:
    # Obtendo os dados da URL
    response = requests.get(url)
    data_json = response.json()

    # Extraindo dados relevantes
    price_data = []
    for year, months in data_json['data'].items():
        for month_data in months:
            price_data.append(month_data)

    # Criando o DataFrame para o intervalo atual
    df_interval = pd.DataFrame(price_data)

    # Adicionando o DataFrame à lista
    dfs.append(df_interval)

# Concatenando os DataFrames
df = pd.concat(dfs, ignore_index=True)
df['createTime'] = pd.to_datetime(df['createTime'], unit='ms')

def create_conditional_column(row):
    if row['interval'] == 'week':
        return int(row['week'])
    elif row['interval'] == 'month':
        # Mapear o número do mês para o nome do mês abreviado
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        return month_names.get(int(row['month']), 'Unknown Month')
    elif row['interval'] == 'quarterly':
        return f"Q{int(row['quarterly'])}"
    else:
        return None

        
# Adicionando a coluna condicional
df['Target'] = df.apply(create_conditional_column, axis=1)
df['priceChangePercent'] = pd.to_numeric(df['priceChangePercent'], errors='coerce')

def assign_color(value):
    return 'red' if value < 0 else 'green'

# Aplicar a função para criar a coluna 'color'
df['color'] = df['priceChangePercent'].apply(assign_color)
df['year'] = df['year'].astype(str)