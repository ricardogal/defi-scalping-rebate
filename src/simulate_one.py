import os
from repository.database_repository import DatabaseRepository
from services.log_service import LogService
from services.exchange_executor import ExchangeExecutor
from core.trade_engine import TradeEngine
from controle.capital_manager import CapitalManager
from utils.config_loader import carregar_config
from services.event_logger import EventLogger
cfg = carregar_config()

def simular_ciclo_unico():
    db = DatabaseRepository()
    logger = LogService(db)
    executor = ExchangeExecutor(
        api_key=os.getenv("API_KEY"),
        secret=os.getenv("API_SECRET")
    )
    capital = CapitalManager(cfg["limites_capital"])
    event_logger = EventLogger(db)
    engine = TradeEngine(
        executor=executor,
        db_repo=db,
        logger=logger,
        dry_run=cfg["dry_run"],
        slippage_tolerance=cfg["slippage_tolerancia"],
        capital_manager=capital,
        event_logger=event_logger
    )

    symbol = cfg["pares"][0]  # roda o primeiro par do config
    engine.executar_ciclo(symbol, cfg["quantidade_padrao"], cfg["spread_alvo"])
    logger.info("✅ Simulação concluída.")
    db.close()

if __name__ == "__main__":
    simular_ciclo_unico()
