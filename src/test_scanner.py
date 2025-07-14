#!/usr/bin/env python3
"""
Script de teste para verificar a performance do scanner de spreads
"""

import time
import os
from dotenv import load_dotenv
from services.exchange_executor import ExchangeExecutor
from scanners.spread_scanner import escanear_spreads
from utils.config_loader import carregar_config

load_dotenv()

def test_scanner_performance():
    """Testa a performance do scanner de spreads"""
    
    # Carrega configuração
    config = carregar_config()
    PAIRS = config["pares"]
    SPREAD_ALVO = config["spread_alvo"]
    
    # Inicializa exchange
    API_KEY = os.getenv("BINANCE_API_KEY")
    API_SECRET = os.getenv("BINANCE_API_SECRET")
    
    if not API_KEY or not API_SECRET:
        print("❌ API_KEY e API_SECRET não configurados no .env")
        return
    
    executor = ExchangeExecutor(API_KEY, API_SECRET)
    
    print("🚀 Testando performance do scanner de spreads...")
    print(f"📊 Pares: {PAIRS}")
    print(f"🎯 Spread alvo: {SPREAD_ALVO:.3%}")
    print("-" * 50)
    
    # Testa múltiplos ciclos
    for i in range(3):
        print(f"\n🔄 Ciclo {i+1}/3")
        inicio = time.time()
        
        oportunidades = escanear_spreads(
            executor.exchange, 
            PAIRS, 
            SPREAD_ALVO, 
            verbose=True
        )
        
        tempo = time.time() - inicio
        print(f"⏱️ Tempo do ciclo: {tempo:.2f}s")
        print(f"💡 Oportunidades encontradas: {len(oportunidades)}")
        
        if oportunidades:
            for op in oportunidades:
                print(f"  ✅ {op['symbol']} | Spread: {op['spread']:.3%}")
        
        time.sleep(2)  # Pausa entre ciclos
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_scanner_performance() 