# data_loader.py
import pandas as pd
import numpy as np
from api_handlers import obter_dados_api, obter_e_processar_dados_tecnicos
from data_processing import processar_dados

def load_data():
    # Carregar dados da primeira API
    instrument_list = obter_dados_api("https://coinank.com/api/instruments/agg?page=1&size=500")
    df_agregado = processar_dados(instrument_list)

    # Carregar dados da segunda API
    api_url_tecnicos = "https://quantifycrypto.com/api/v1.0/common/init-table?currency=USD&fields=rank,symbol_name,price_usd,marketcap,volume24h,price5min,price15min,price1h,price2h,price4h,price24h,price1week,price2week,price30day,price_year_to_date,price1year,macd_5min,macd_15min,macd_30min,macd_1h,macd_2h,macd_4h,macd_24h,rsi5min,rsi15min,rsi30min,rsi1h,rsi2h,rsi4h,rsi24h,bb_5min,bb_15min,bb_30min,bb_1h,bb_2h,bb_4h,bb_24h,qc_key&exchange=binance,coinbase,kucoin,huobi,upbit,gate,cryptodotcom"
    df_tec = obter_e_processar_dados_tecnicos(api_url_tecnicos)

    # Processamento adicional ou combinação dos dados, se necessário
    df_final = pd.merge(df_tec, df_agregado, left_on='qc_key', right_on='baseCoin', how='outer')
    df_final['Crypto'] = df_final['baseCoin'].fillna(df_final['qc_key'])
    df_final['Market Cap'] = df_final['marketCap'].fillna(df_final['marketcap'])
    df_final['Rank'] = df_final['Market Cap'].rank(ascending=False)

    mapeamento_preenchimento = {
        'Price 5m': 'price5min',
        'Price 15m': 'price15min',
        'Price 1h': 'price1h',
        'Price 2h': 'price2h',
        'Price 4h': 'price4h',
        'Price 24h': 'price24h',          
        'price_usd': 'price',        
        'Volume 24h': 'volume24h',
        #'marketCap': 'marketcap',
        #'qc_key': 'qc_key'
    }


    for coluna, substituto in mapeamento_preenchimento.items():
        df_final[coluna] = df_final[coluna].fillna(df_final[substituto])

    #Substituir NaN em 'symbol' por qc_key + 'USDT'
    df_final['symbol'] = df_final.apply(
        lambda row: row['qc_key'] + 'USDT' if pd.isna(row['symbol']) else row['symbol'],
        axis=1
    )
    
    df_final['Price USD'] = np.where(
        df_final['price'].notna(), 
        df_final['price'], 
        df_final['price_usd']
    )
    df_final['OI/Market Cap'] = (df_final['Open Interest']/ df_final['marketcap'])
    df_final['Volume24h/OI'] = (df_final['Volume 24h']/df_final['Open Interest'])
    df_final['Volume24h/Market Cap'] = (df_final['Volume 24h']/df_final['Market Cap'])
    #df_final['Trades 24h'] = df_final['Buy Trades 24h'] + df_final['Sell Trades 24h']
    df_final['Liquidations 24h/OI'] = (df_final['Liquidation 24h']/ df_final['Open Interest'])*100
    df_final['Long Liquidations/OI'] = (df_final['Long Liquidation 24h']/ df_final['Open Interest'])*100
    df_final['Short Liquidations/OI'] = (df_final['Short Liquidation 24h']/ df_final['Open Interest'])*100
    df_final['Short-Term OI Trend'] = (df_final['Open Interest 5m'] + df_final['Open Interest 15m'] + df_final['Open Interest 30m'] + df_final['Open Interest 1h'])/4
    df_final['Long-Term OI Trend'] = (df_final['Open Interest 4h'] + df_final['Open Interest 24h'] + df_final['Open Interest 2d'] + df_final['Open Interest 3d']+ df_final['Open Interest 7d'])/5
    df_final['Top Trader Sentiment'] = (df_final['Top Trader LSR Position']+ df_final['Top Trader LSR Account'])/2
    df_final['Funding Rate Risk'] = df_final['Funding Rate']*10000 * df_final['Top Trader Sentiment']
    df_final['Short-Term RSI Trend'] = (df_final['rsi5min'] + df_final['rsi15min'] + df_final['rsi30min'] + df_final['rsi1h'])/4
    df_final['Long-Term RSI Trend'] = (df_final['rsi4h'] + df_final['rsi24h'])/2
    df_final['Coin'] = df_final.apply(
        lambda row: f'<img src="{row.coinImage}" width="25" height="auto"> {row.baseCoin}' 
                    if (not pd.isna(row['coinImage']) and row['coinImage'] != '' and not pd.isna(row['baseCoin']) and row['baseCoin'].strip() != '')
                    else f'<img src="https://github.com/Pymmdrza/Cryptocurrency_Logos/blob/mainx/PNG/{row.qc_key.lower()}.png?raw=true" width="25" height="auto"> {row.qc_key}',
        axis=1
    )

    colunas_para_remover = ['marketCapChange24H', 'marketCapChangeValue24H','show','follow','lsRatioCh24','buyTradeTurnover','sellTradeTurnover','price5min','price15min','price1h','price2h','price4h','price24h','volume24h','marketcap','marketCap','price','price_usd','qc_key','baseCoin']
    df_final = df_final.drop(columns=colunas_para_remover, errors='ignore')
    
    return df_final

