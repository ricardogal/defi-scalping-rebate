import sqlite3
from datetime import datetime

class DatabaseRepository:    
    def __init__(self, db_path="/home/tiozinho-gamer/domains/defi-scalping/data/scalping.db"):
        print(f"[DB] Iniciando conexão com {db_path}")
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    side TEXT,
                    price REAL,
                    quantity REAL,
                    rebate REAL,
                    pnl REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_evento TEXT,
                    par TEXT,
                    mensagem TEXT,
                    detalhe_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_trade(self, symbol, side, price, quantity, rebate, pnl):
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            self.conn.execute("""
                INSERT INTO trades (symbol, side, price, quantity, rebate, pnl, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (symbol, side, price, quantity, rebate, pnl, timestamp))

    def save_log(self, level, message):
        with self.conn:
            self.conn.execute("""
                INSERT INTO logs (level, message) VALUES (?, ?)
            """, (level, message))

    def fetch_trades(self, symbol=None):
        cursor = self.conn.cursor()
        if symbol:
            cursor.execute("SELECT * FROM trades WHERE symbol = ?", (symbol,))
        else:
            cursor.execute("SELECT * FROM trades")
        return cursor.fetchall()

    def listar_ordens_abertas(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM ordens_abertas").fetchall()

    def remover_ordem_aberta(self, ordem_id):
        with self.conn:
            self.conn.execute("DELETE FROM ordens_abertas WHERE id = ?", (ordem_id,))

    def salvar_ordem_aberta(self, ordem_id, symbol, side, price, quantity):
        with self.conn:
            self.conn.execute("""
                INSERT INTO ordens_abertas (id, symbol, side, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (ordem_id, symbol, side, price, quantity))

    def registrar_evento(self, tipo_evento, par, mensagem, detalhe=None):
        import json
        detalhe_str = json.dumps(detalhe) if detalhe else None
        with self.conn:
            self.conn.execute("""
                INSERT INTO eventos (tipo_evento, par, mensagem, detalhe_json)
                VALUES (?, ?, ?, ?)
            """, (tipo_evento, par, mensagem, detalhe_str))


    def close(self):
        self.conn.close()
