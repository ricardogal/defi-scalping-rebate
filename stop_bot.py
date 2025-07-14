#!/usr/bin/env python3
"""
Script para parar o bot e cancelar ordens pendentes
"""

import os
import sys
from pathlib import Path

# Adiciona src/ ao PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
load_dotenv()

def stop_bot():
    """Cancela ordens pendentes e para o bot"""
    try:
        from services.exchange_executor import ExchangeExecutor
        
        api_key = os.getenv("BINANCE_API_KEY")
        secret = os.getenv("BINANCE_API_SECRET")
        
        if not api_key or not secret:
            print("❌ API_KEY e API_SECRET não configurados no .env")
            return
            
        executor = ExchangeExecutor(api_key, secret)
        
        print("🛑 Buscando ordens abertas...")
        ordens_abertas = executor.listar_ordens_abertas()
        
        if not ordens_abertas:
            print("✅ Nenhuma ordem aberta encontrada.")
            return
            
        print(f"⚠️ Encontradas {len(ordens_abertas)} ordem(s) aberta(s)")
        
        for ordem in ordens_abertas:
            try:
                order_id = ordem['id']
                symbol = ordem['symbol']
                side = ordem['side']
                price = ordem['price']
                amount = ordem['amount']
                
                print(f"🛑 Cancelando: {symbol} | {side} | {price} | {amount}")
                executor.cancel_order(order_id, symbol)
                print(f"✅ Ordem {order_id} cancelada com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao cancelar ordem {ordem.get('id')}: {e}")
                
        print("🧹 Todas as ordens foram canceladas!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    stop_bot()
