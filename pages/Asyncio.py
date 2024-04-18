import aiohttp
import streamlit as st
import asyncio

async def get_binance_symbols(session):
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    try:
        async with session.get(url) as response:
            # Verifica se a solicitação foi bem-sucedida (código de status 2xx)
            if response.status == 200:
                data = await response.json()
                symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
                return symbols
            elif response.status == 451:
                st.error("Acesso ao recurso indisponível por motivos legais.")
            else:
                st.error(f"Erro ao buscar símbolos: Código de status {response.status}")
    except aiohttp.ClientError as e:
        # Se ocorrer um erro ao fazer a solicitação (por exemplo, conexão perdida)
        st.error(f"Erro de cliente ao buscar símbolos: {e}")
    except Exception as e:
        # Se ocorrer um erro inesperado
        st.error(f"Erro inesperado ao buscar símbolos: {e}")

    # Retorna uma lista vazia se ocorrer um erro
    return []

async def main():
    # Endereço do proxy
    proxy_url = "https://eu7.proxysite.com/process.php?d=oE6h%2B9sADhUQgaCSEuwI0rFSd%2F5CR0aehO4mWpUxQhl1m8Memqg2&b=1&f=norefer"
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.binance.com/api/v3/exchangeInfo', proxy=proxy_url) as response:
            symbols = await get_binance_symbols(session)
            if symbols:
                st.write(symbols)
            else:
                st.error("Nenhum símbolo encontrado.")

# Para executar a função principal
if __name__ == "__main__":
    asyncio.run(main())
