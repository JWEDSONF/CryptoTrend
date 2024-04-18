import asyncio
import aiohttp
import streamlit as st

async def get_binance_symbols(session):
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    try:
        async with session.get(url) as response:
            # Verifica se a solicitação foi bem-sucedida (código de status 2xx)
            if response.status == 200:
                data = await response.json()
                symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
                return symbols
            # Se a resposta for redirecionada (código de status 3xx), pode ser tratado aqui
            elif response.status == 301:
                # Lógica para lidar com redirecionamento
                pass
            # Se a resposta for um erro do cliente (código de status 4xx)
            elif response.status == 404:
                # Lógica para lidar com erro do cliente (por exemplo, recurso não encontrado)
                pass
            # Se a resposta for um erro do servidor (código de status 5xx)
            elif response.status == 500:
                # Lógica para lidar com erro do servidor
                pass
            else:
                # Lógica para lidar com outros códigos de status
                pass
    except aiohttp.ClientError as e:
        # Se ocorrer um erro ao fazer a solicitação (por exemplo, conexão perdida)
        print(f"Erro de cliente ao buscar símbolos: {e}")
    except Exception as e:
        # Se ocorrer um erro inesperado
        print(f"Erro inesperado ao buscar símbolos: {e}")

    # Retorna uma lista vazia se ocorrer um erro
    return []

async def main():
    async with aiohttp.ClientSession() as session:
        symbols = await get_binance_symbols(session)
        print(symbols)

# Para executar a função principal
if __name__ == "__main__":
    asyncio.run(main())
