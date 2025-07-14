from main import main
from services.exchange_executor import ExchangeExecutor
from dotenv import load_dotenv
import os

load_dotenv()

def checar_ordens_abertas():
    executor = ExchangeExecutor(
        os.getenv("BINANCE_API_KEY"),
        os.getenv("BINANCE_API_SECRET")
    )
    ordens = executor.listar_ordens_abertas()
    if ordens:
        print(f"⚠️ ATENÇÃO: Há {len(ordens)} ordem(ns) aberta(s) na conta!")
        for o in ordens:
            print(f"- {o['symbol']} | {o['side']} | {o['price']}")
        print("Recomendo rodar `stop_bot.py` para limpar antes.")
        input("Pressione ENTER para continuar assim mesmo ou CTRL+C para abortar...")

if __name__ == "__main__":
    checar_ordens_abertas()
    main()
