import time
from datetime import datetime

class OrderTracker:
    def __init__(self, executor, logger, db_repo, capital_manager=None, tempo_max_espera=15):
        self.executor = executor
        self.log = logger
        self.db = db_repo
        self.capital_manager = capital_manager
        self.timeout = tempo_max_espera

    def executar_ordem_completa(self, symbol, quantidade, preco_compra, preco_venda):
        try:
            # Enviar ordem limit de compra
            ordem = self.executor.place_limit_order(symbol, "buy", preco_compra, quantidade)
            ordem_id = ordem["id"]
            self.log.info(f"{symbol} | Ordem de compra enviada: {ordem_id}")
            self.db.salvar_ordem_aberta(ordem_id, symbol, "buy", preco_compra, quantidade)

            # Esperar execução
            executada = self._aguardar_execucao(ordem_id, symbol)
            if not executada:
                self.executor.cancel_order(ordem_id, symbol)
                self.log.warn(f"{symbol} | Ordem {ordem_id} cancelada por timeout")
                self.db.remover_ordem_aberta(ordem_id)
                if self.capital_manager:
                    self.capital_manager.liberar_capital(symbol, preco_compra * quantidade)
                return

            # Buscar rebate real
            rebate = 0
            try:
                fills = self.executor.fetch_order_fills(ordem_id, symbol)
                for fill in fills:
                    if "commission" in fill:
                        rebate += float(fill["commission"])
            except Exception as e:
                self.log.warn(f"{symbol} | Falha ao obter rebate da ordem {ordem_id}: {str(e)}")

            # Enviar ordem de venda
            ordem_venda = self.executor.place_limit_order(symbol, "sell", preco_venda, quantidade)
            venda_id = ordem_venda["id"]
            self.log.info(f"{symbol} | Ordem de venda enviada: {venda_id}")
            self.db.salvar_ordem_aberta(venda_id, symbol, "sell", preco_venda, quantidade)
            self.db.registrar_evento(
                tipo_evento="ordem_enviada",
                par=symbol,
                mensagem=f"Compra enviada: {ordem_id} a {preco_compra}",
                detalhe={"preco": preco_compra, "quantidade": quantidade}
            )


            # Esperar execução da venda
            venda_executada = self._aguardar_execucao(venda_id, symbol)
            if not venda_executada:
                self.executor.cancel_order(venda_id, symbol)
                self.log.warn(f"{symbol} | Venda {venda_id} cancelada por timeout")
                self.db.remover_ordem_aberta(venda_id)
                return

            # Salvar no banco
            pnl = preco_venda - preco_compra + rebate
            self.db.save_trade(symbol, "buy", preco_compra, quantidade, rebate=rebate, pnl=0)
            self.db.save_trade(symbol, "sell", preco_venda, quantidade, rebate=0, pnl=pnl)

            if self.capital_manager:
                self.capital_manager.liberar_capital(symbol, preco_compra * quantidade)

            self.log.info(f"{symbol} | Trade finalizado. P&L: {pnl:.5f} | 🎁 Rebate: {rebate:.5f}")

        except Exception as e:
            self.log.error(f"{symbol} | Erro geral na execução da ordem: {str(e)}")
            if self.capital_manager:
                self.capital_manager.liberar_capital(symbol, preco_compra * quantidade)

    def _aguardar_execucao(self, ordem_id, symbol):
        inicio = datetime.utcnow()
        while (datetime.utcnow() - inicio).total_seconds() < self.timeout:
            status = self.executor.fetch_order_status(ordem_id, symbol)
            if status["status"] == "closed":
                self.log.info(f"{symbol} | Ordem {ordem_id} executada.")
                self.db.remover_ordem_aberta(ordem_id)
                return True
            time.sleep(1)
        return False
