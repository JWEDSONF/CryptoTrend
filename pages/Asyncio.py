import asyncio
import aiohttp
import streamlit as st

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

async def main():
    async with aiohttp.ClientSession() as session:
        symbols = await get_binance_symbols(session)
        # Faça algo com os símbolos obtidos, como exibir ou processá-los
        print(symbols)

# Para executar a função principal
if __name__ == "__main__":
    asyncio.run(main())
