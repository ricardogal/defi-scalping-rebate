import time
import os
from repository.database_repository import DatabaseRepository
from services.log_service import LogService
from services.exchange_executor import ExchangeExecutor
from core.trade_engine import TradeEngine
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Pares a operar (pode ler isso de um arquivo externo futuramente)
PAIRS = ["BTC/USDT", "ETH/USDT"]
QUANTIDADE = 0.001  # Ex: 0.001 BTC, 0.01 ETH — ajuste conforme o ativo


def main():
    # Instanciando os módulos principais

    capital_limits = {
        "BTC/USDT": 20,
        "ETH/USDT": 15,
        "SOL/USDT": 10,
    }
    from controle.capital_manager import CapitalManager
    db = DatabaseRepository()
    logger = LogService(db)
    executor = ExchangeExecutor(API_KEY, API_SECRET)
    capital_manager = CapitalManager(capital_limits)
    engine = TradeEngine(
        executor=executor,
        db_repo=db,
        logger=logger,
        dry_run=True,
        slippage_tolerance=0.01,
        capital_manager=capital_manager
    )

    logger.info("🔁 Iniciando loop principal do bot Scalping Rebate...")

    try:
        while True:
            for par in PAIRS:
                logger.info(f"🔍 Executando ciclo para: {par}")
                engine.executar_ciclo(par, QUANTIDADE)
                time.sleep(1)  # Pausa entre os pares
            time.sleep(10)  # Pausa entre ciclos completos

    except KeyboardInterrupt:
        logger.warn("⛔ Execução interrompida pelo usuário (CTRL+C).")

    finally:
        db.close()
        logger.info("✅ Banco de dados fechado com sucesso.")

if __name__ == "__main__":
    main()
