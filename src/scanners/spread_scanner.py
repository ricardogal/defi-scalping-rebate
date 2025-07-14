from typing import List, Dict
import time
from services.exchange_executor import ExchangeExecutor
from utils.config_loader import carregar_config

def escanear_spreads(exchange, pares, spread_minimo, verbose=False, modo_flexivel=False):
    """
    Escaneia spreads de forma otimizada.
    Se modo_flexivel=True, retorna todos os pares com dados, independente do spread.
    """
    oportunidades = {}

    if verbose:
        print(f"[SCANNER] Iniciando escaneamento de {len(pares)} pares...")

    for i, par in enumerate(pares):
        try:
            if i > 0:
                time.sleep(0.1)

            book = exchange.fetch_order_book(par, limit=5)
            if not book['bids'] or not book['asks']:
                if verbose:
                    print(f"[SCANNER] {par} | Sem dados suficientes no order book")
                continue

            bid = book['bids'][0][0]
            ask = book['asks'][0][0]
            spread = (ask - bid) / bid

            if verbose:
                print(f"[SCANNER] {par} | Bid: {bid:.8f} | Ask: {ask:.8f} | Spread: {spread:.5%}")

            if spread >= spread_minimo or modo_flexivel:
                oportunidades[par] = {
                    "bid": bid,
                    "ask": ask,
                    "spread": spread
                }
                if verbose and spread < spread_minimo and modo_flexivel:
                    print(f"[SCANNER] ⚠️ {par} | Spread {spread:.5%} < alvo, mas incluso por modo_flexivel")

        except Exception as e:
            if verbose:
                print(f"[SCANNER] ❌ Erro ao escanear {par}: {str(e)}")
            continue

    if verbose:
        print(f"[SCANNER] Encontradas {len(oportunidades)} oportunidades")

    return oportunidades
