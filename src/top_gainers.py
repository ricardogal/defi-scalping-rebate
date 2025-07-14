#!/usr/bin/env python3
"""
📈 TOP GAINERS SIMPLES COM CACHE (Binance + SQLite)
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple
import os
from ccxt import binance

# Logger padrão do bot
logger = logging.getLogger("top_gainers")
logger.setLevel(logging.INFO)

DB_PATH = os.getenv("DB_PATH", "/home/tiozinho-gamer/domains/defi-scalping/data/top_gainers.db")
QUOTE = os.getenv("QUOTE", "USDT")
CACHE_TTL_MINUTES = 30

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS top_gainers_cache (
            symbol TEXT,
            change_percent REAL,
            quote TEXT,
            expires_at DATETIME
        )
    """)
    conn.commit()
    conn.close()

def get_cache() -> List[Tuple[str, float]]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            SELECT symbol, change_percent FROM top_gainers_cache
            WHERE quote = ? AND expires_at > datetime('now')
            ORDER BY change_percent DESC
        """, (QUOTE,))
        results = cursor.fetchall()
        conn.close()
        if results:
            logger.info(f"✅ Cache válido encontrado ({len(results)} ativos)")
        return results
    except Exception as e:
        logger.warning(f"⚠️ Falha ao ler cache: {e}")
        return []

def update_cache(data: List[Tuple[str, float]]):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM top_gainers_cache WHERE quote = ?", (QUOTE,))
        expires_at = datetime.utcnow() + timedelta(minutes=CACHE_TTL_MINUTES)
        for symbol, change in data:
            conn.execute("""
                INSERT INTO top_gainers_cache (symbol, change_percent, quote, expires_at)
                VALUES (?, ?, ?, ?)
            """, (symbol, change, QUOTE, expires_at))
        conn.commit()
        conn.close()
        logger.info(f"💾 Cache atualizado com {len(data)} top gainers")
    except Exception as e:
        logger.warning(f"❌ Falha ao atualizar cache: {e}")

def fetch_from_binance(n=20) -> List[Tuple[str, float]]:
    try:
        logger.info("🔄 Buscando top gainers da Binance...")
        exchange = binance({'enableRateLimit': True})
        markets = exchange.load_markets()
        quote_pairs = [
            symbol for symbol in markets
            if symbol.endswith(f"/{QUOTE}") and
            not any(stable in symbol for stable in ['BUSD', 'USDC', 'DAI']) and
            not symbol.startswith(f"{QUOTE}/")
        ]
        changes = []
        for symbol in quote_pairs:
            try:
                ticker = exchange.fetch_ticker(symbol)
                pct = ticker.get("percentage", None)
                if pct is not None:
                    try:
                        pct_float = float(pct)
                        if pct_float > 0:
                            changes.append((symbol, pct_float))
                    except (ValueError, TypeError):
                        continue
            except Exception:
                continue

        sorted_changes = sorted(changes, key=lambda x: x[1], reverse=True)[:n]
        logger.info(f"✅ Encontrados {len(sorted_changes)} top gainers da Binance")
        return sorted_changes
    except Exception as e:
        logger.error(f"❌ Erro na Binance: {e}")
        return []

def get_top_gainers(n=20) -> List[Tuple[str, float]]:
    init_db()
    cached = get_cache()
    if cached:
        return cached
    fresh = fetch_from_binance(n=n)
    if fresh:
        update_cache(fresh)
        return fresh
    return []

# Teste simples (executando direto)
if __name__ == "__main__":
    top = get_top_gainers()
    for symbol, change in top:
        print(f"{symbol} | +{change:.2f}%")
