# table_formatters.py
from st_aggrid import JsCode

# Defina as colunas para cada tipo de formatação
colunas_dolar = [
    'Open Interest', 'Liquidation 1h', 'Liquidation Long 1h', 'Liquidation Short 1h',
    'Liquidation 4h', 'Liquidation Long 4h', 'Liquidation Short 4h', 'Liquidation 12h',
    'Liquidation Long 12h', 'Liquidation Short 12h', 'Liquidation 24h', 'Liquidation Long 24h',
    'Liquidation Short 24h', 'Buy Trades 24h', 'Sell Trades 24h', 'Buy Volume 24h',
    'Sell Volume 24h', 'Buy Volume 12h', 'Sell Volume 12h', 'Buy Volume 8h', 'Sell Volume 8h',
    'Buy Volume 6h', 'Sell Volume 6h', 'Buy Volume 4h', 'Sell Volume 4h', 'Buy Volume 2h',
    'Sell Volume 2h', 'Buy Volume 1h', 'Sell Volume 1h', 'Buy Volume 30m', 'Sell Volume 30m',
    'Buy Volume 15m', 'Sell Volume 15m', 'Buy Volume 5m', 'Sell Volume 5m', 'Volume 24h'
]

colunas_percentual = [
    'Volume Change 24h', 'Open Interest 5m', 'Open Interest 15m', 'Open Interest 30m',
    'Open Interest 1h', 'Open Interest 4h', 'Open Interest 24h', 'Open Interest 2d',
    'Open Interest 3d', 'Open Interest 7d', 'Long Ratio', 'Short Ratio',
    'Long vs Short Real Time', 'Funding Rate', 'Long Short Ratio', 'LSR 5m',
    'LSR 15m', 'LSR 30m', 'LSR 1h', 'LSR 4h'
]
# Funções de formatação em JavaScript
dollar_formatter = JsCode("""
function(params) {
    if (params.value != null) {
        return '$' + params.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    } else {
        return null;
    }
}
""")

percent_formatter = JsCode("""
function(params) {
    if (params.value != null) {
        return (params.value * 100).toFixed(2) + '%';
    } else {
        return null;
    }
}
""")

