import time
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from repository.database_repository import DatabaseRepository
from services.log_service import LogService
from services.exchange_executor import ExchangeExecutor

TEMPO_MAXIMO = 60  # segundos

def cancelar_ordens_pendentes():
    DATA_DIR = os.getenv("DATA_DIR", "./data")  # Valor padrão se não estiver definido
    db = DatabaseRepository(f"{DATA_DIR}/scalping.db")
    log = LogService(db)
    executor = ExchangeExecutor(
        api_key=os.getenv("BINANCE_API_KEY"),
        secret=os.getenv("BINANCE_API_SECRET")
    )

    ordens = db.listar_ordens_abertas()

    agora = datetime.utcnow()
    for ordem in ordens:
        ordem_id, symbol, side, price, quantity, created_at = ordem
        tempo = agora - datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

        if tempo.total_seconds() > TEMPO_MAXIMO:
            try:
                status = executor.fetch_order_status(ordem_id, symbol)
                if status["status"] == "open":
                    executor.cancel_order(ordem_id, symbol)
                    log.warn(f"🛑 Ordem {ordem_id} cancelada por timeout ({symbol})")
                else:
                    log.info(f"✅ Ordem {ordem_id} já executada")

            except Exception as e:
                log.error(f"Erro ao cancelar {ordem_id}: {e}")

            db.remover_ordem_aberta(ordem_id)   
    else:
        print("Nenhuma ordem pendente") 

    db.close()
