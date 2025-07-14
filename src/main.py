import time
import os
from dotenv import load_dotenv
from src.repository.database_repository import DatabaseRepository
from src.services.log_service import LogService
from src.services.exchange_executor import ExchangeExecutor
from src.services.event_logger import EventLogger
from src.core.trade_engine import TradeEngine
from src.controle.capital_manager import CapitalManager
from src.scanners.spread_scanner import escanear_spreads
from src.utils.config_loader import carregar_config

load_dotenv()



API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def main():
    # Carrega config.json
    DATA_DIR = os.getenv("DATA_DIR", "./data")  # Valor padrão se não estiver definido
    config = carregar_config()
    #PAIRS = config["pares"]
    QUANTIDADE = config["quantidade_padrao"]
    SPREAD_ALVO = config["spread_alvo"]
    SLIPPAGE = config["slippage_tolerancia"]
    INTERVALO = config["intervalo_execucao"]
    LIMITES = config["limites_capital"]
    DRY_RUN = config["dry_run"]
    db = DatabaseRepository(f"{DATA_DIR}/scalping.db")
    logger = LogService(db, f"{DATA_DIR}/bot_scalping.log")
    event_logger = EventLogger(db)
    executor = ExchangeExecutor(API_KEY, API_SECRET)
    capital_manager = CapitalManager(LIMITES)

    from src.top_gainers import get_top_gainers

    # 🔥 Busca dinâmicamente os top gainers
    top_pares = get_top_gainers(n=10)
    symbols = [s for s, _ in top_pares]

    if not symbols:
        print("⚠️ Nenhum par identificado como top gainer. Usando fallback do config.json")
        symbols = config["pares"]

    PAIRS = symbols

    engine = TradeEngine(
        executor=executor,
        db_repo=db,
        logger=logger,
        dry_run=DRY_RUN,
        slippage_tolerance=SLIPPAGE,
        capital_manager=capital_manager,
        event_logger=event_logger
    )

    logger.info("🚀 Bot Scalping Rebate iniciado com inteligência de pares.")
    logger.info(f"📊 Monitorando {len(PAIRS)} pares | Spread alvo: {SPREAD_ALVO:.6%}")

    try:
        while True:
            inicio_ciclo = time.time()
            logger.info("🔍 Escaneando pares com spread suficiente...")
            
            #oportunidades = escanear_spreads(executor.exchange, PAIRS, SPREAD_ALVO, verbose=True)
            oportunidades = escanear_spreads(
                executor.exchange,
                PAIRS,
                SPREAD_ALVO,
                verbose=True,
                modo_flexivel=True  # <- Ativa modo de testes
            )

            if oportunidades:
                logger.info(f"💡 Encontradas {len(oportunidades)} oportunidades")
                quantidades_personalizadas = config.get("quantidades_personalizadas", {})
                
                for symbol, op in oportunidades.items():
                    quantidade = quantidades_personalizadas.get(symbol, QUANTIDADE)
                    book_data = {
                        "bid": op["bid"],
                        "ask": op["ask"],
                        "spread": op["spread"]
                    }

                    logger.info(f"⚡ Executando ciclo para: {symbol} (Spread: {op['spread']:.3%})")
                    event_logger.log_evento("ciclo_iniciado", symbol, f"Iniciando ciclo para {symbol}")
                    engine.executar_ciclo(symbol, quantidade, book_data, SPREAD_ALVO)

                    time.sleep(0.5)  # pausa reduzida entre execuções
            else:
                logger.info("⏳ Nenhuma oportunidade encontrada neste ciclo")

            tempo_ciclo = time.time() - inicio_ciclo
            logger.info(f"⏱️ Ciclo concluído em {tempo_ciclo:.2f}s | Aguardando {INTERVALO}s...")
            time.sleep(INTERVALO)

    except KeyboardInterrupt:
        logger.warn("⛔ Execução interrompida pelo usuário (CTRL+C).")

    finally:
        db.close()
        logger.info("✅ Banco de dados fechado com sucesso.")

if __name__ == "__main__":
    main()
