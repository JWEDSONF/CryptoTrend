import aiohttp
import asyncio
import streamlit as st

async def get_binance_symbols(session):
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
                return symbols
            elif response.status == 451:
                st.error("Acesso ao recurso indisponível por motivos legais.")
            else:
                st.error(f"Erro ao buscar símbolos: Código de status {response.status}")
    except aiohttp.ClientError as e:
        st.error(f"Erro de cliente ao buscar símbolos: {e}")
    except Exception as e:
        st.error(f"Erro inesperado ao buscar símbolos: {e}")
    return []

async def main():
    # Endereço do proxy
    proxy_url = "https://de.hideproxy.me/go.php?u=16eHB1ohllrWmAzKs9ioKJBq%2F6l7FrHVFSji9V0jfJ3ZfZ55uiYh&b=5&f=norefer"

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.binance.com/api/v3/exchangeInfo', proxy=proxy_url) as response:
            symbols = await get_binance_symbols(session)
            if symbols:
                st.write(symbols)
            else:
                st.error("Nenhum símbolo encontrado.")

# Executa o loop de eventos do asyncio
if __name__ == "__main__":
    asyncio.run(main())
