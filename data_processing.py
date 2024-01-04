import pandas as pd

colunas_renomear = {
    'openInterest': 'Open Interest',
    'liquidationH1': 'Liquidation 1h',
    'liquidationH1Long': 'Liquidation Long 1h',
    'liquidationH1Short': 'Liquidation Short 1h',
    'liquidationH4': 'Liquidation 4h',
    'liquidationH4Long': 'Liquidation Long 4h',
    'liquidationH4Short': 'Liquidation Short 4h',
    'liquidationH12': 'Liquidation 12h',
    'liquidationH12Long': 'Liquidation Long 12h',
    'liquidationH12Short': 'Liquidation Short 12h',
    'liquidationH24': 'Liquidation 24h',
    'liquidationH24Long': 'Liquidation Long 24h',
    'liquidationH24Short': 'Liquidation Short 24h',
    'buyTradeTurnover': 'Buy Trades 24h',
    'sellTradeTurnover': 'Sell Trades 24h',
    'buy24h': 'Buy Volume 24h',
    'sell24h': 'Sell Volume 24h',
    'buy12h': 'Buy Volume 12h',
    'sell12h': 'Sell Volume 12h',
    'buy8h': 'Buy Volume 8h',
    'sell8h': 'Sell Volume 8h',
    'buy6h': 'Buy Volume 6h',
    'sell6h': 'Sell Volume 6h',
    'buy4h': 'Buy Volume 4h',
    'sell4h': 'Sell Volume 4h',
    'buy2h': 'Buy Volume 2h',
    'sell2h': 'Sell Volume 2h',
    'buy1h': 'Buy Volume 1h',
    'sell1h': 'Sell Volume 1h',
    'buy30m': 'Buy Volume 30m',
    'sell30m': 'Sell Volume 30m',
    'buy15m': 'Buy Volume 15m',
    'sell15m': 'Sell Volume 15m',
    'buy5m': 'Buy Volume 5m',
    'sell5m': 'Sell Volume 5m',
    'turnover24h': 'Volume 24h',
    'openInterestChM5': 'Open Interest 5m',
    'openInterestChM15': 'Open Interest 15m',
    'openInterestChM30': 'Open Interest 30m',
    'openInterestCh1': 'Open Interest 1h',
    'openInterestCh4': 'Open Interest 4h',
    'openInterestCh24': 'Open Interest 24h',
    'openInterestCh2D': 'Open Interest 2d',
    'openInterestCh3D': 'Open Interest 3d',
    'openInterestCh7D': 'Open Interest 7d',
    'longRatio': 'Long Ratio',
    'shortRatio': 'Short Ratio',
    'longShortRatio': 'Long vs Short Real Time',
    'fundingRate': 'Funding Rate',
    'longShortPerson': 'Long Short Ratio',
    'lsPersonChg5m': 'LSR 5m',
    'lsPersonChg15m': 'LSR 15m',
    'lsPersonChg30m': 'LSR 30m',
    'lsPersonChg1h': 'LSR 1h',
    'lsPersonChg4h': 'LSR 4h',
    'longShortPosition': 'Top Trader LSR Position',
    'longShortAccount': 'Top Trader LSR Account',
    'turnoverChg24h': 'Volume Change 24h'
}

def processar_dados(instrument_list):
    df_instr = pd.DataFrame(instrument_list)
    df_instr.rename(columns=colunas_renomear, inplace=True)
    df_instr['baseCoin'] = df_instr['baseCoin'].replace(to_replace=r'1000', value='', regex=True)
    df_instr = df_instr.dropna(axis=1, how='all')
    df_instr['baseCoin'] = df_instr['baseCoin'].str.replace('1000', '')

    colunas_numericas = df_instr.select_dtypes(include='number').columns
    colunas_texto = df_instr.select_dtypes(include='object').columns
    df_instr[colunas_numericas] = df_instr[colunas_numericas].apply(pd.to_numeric, errors='coerce')

    colunas_soma = [
        colunas_renomear.get(col, col) for col in [
            'openInterest','liquidationH1','liquidationH1Long','liquidationH1Short',
            'liquidationH4','liquidationH4Long','liquidationH4Short','liquidationH12',
            'liquidationH12Long','liquidationH12Short','liquidationH24','liquidationH24Long',
            'liquidationH24Short','buyTradeTurnover','sellTradeTurnover','buy24h','sell24h',
            'buy12h','sell12h','buy8h','sell8h','buy6h','sell6h','buy4h','sell4h','buy2h',
            'sell2h','buy1h','sell1h','buy30m','sell30m','buy15m','sell15m','buy5m','sell5m','turnover24h']]
    
    # colunas_media = [
    #     colunas_renomear.get(col, col) for col in [
    #         'priceChangeH24', 'priceChangeM5', 'priceChangeM15', 'priceChangeM30', 'priceChangeH1', 'priceChangeH2',
    #         'priceChangeH4', 'priceChangeH6', 'priceChangeH8', 'priceChangeH12','openInterestChM5', 'openInterestChM15', 
    #         'openInterestChM30', 'openInterestCh1', 'openInterestCh4','openInterestCh24', 'openInterestCh2D',
    #         'openInterestCh3D',  'openInterestCh7D', 'longRatio', 'shortRatio','longShortRatio', 'fundingRate']]

    df_agregado = df_instr.groupby('baseCoin')[colunas_soma].sum()
    df_agregado[colunas_numericas] = df_instr.groupby('baseCoin')[colunas_numericas].first()
    df_agregado[colunas_texto] = df_instr.groupby('baseCoin')[colunas_texto].first()
    df_agregado['price'] = df_instr.groupby('baseCoin')['price'].first()
    df_agregado['symbol'] = df_agregado['symbol'].str.replace(r'-SWAP$', '').str.replace(r'-', '')



    df_agregado.reset_index(inplace=True, drop=True)
    return df_agregado
