import json
from datetime import datetime

class EventLogger:
    def __init__(self, repository):
        self.repo = repository

    def log_evento(self, tipo, par, mensagem, detalhe=None):
        detalhe_str = json.dumps(detalhe) if detalhe else None
        print(f"[EVENTO] {datetime.now()} - [{tipo.upper()}] {par} -> {mensagem}")
        self.repo.registrar_evento(tipo, par, mensagem, detalhe)
