class TradeEngine:
    def __init__(self, executor, db_repo, logger, dry_run=True, slippage_tolerance=0.01, capital_manager=None):
        self.executor = executor
        self.db = db_repo
        self.log = logger
        self.dry_run = dry_run
        self.slippage_tolerance = slippage_tolerance
        self.capital_manager = capital_manager

    def executar_ciclo(self, symbol, quantidade, spread_alvo=0.02):
        try:
            book = self.executor.exchange.fetch_order_book(symbol)
            ask = book['asks'][0][0]
            bid = book['bids'][0][0]
            spread = (ask - bid) / bid

            self.log.info(f"{symbol} | Spread: {spread:.5f} | Bid: {bid} | Ask: {ask}")

            if spread < spread_alvo:
                self.log.warn(f"{symbol} | Spread insuficiente ({spread:.5f})")
                return

            preco_compra = bid + (self.slippage_tolerance / 2)
            preco_venda = ask - (self.slippage_tolerance / 2)
            custo_total = preco_compra * quantidade

            # ⚠️ Verificar capital antes de seguir
            if self.capital_manager and not self.capital_manager.pode_usar_capital(symbol, custo_total):
                self.log.warn(f"{symbol} | Sem capital disponível para nova entrada.")
                return

            # Reservar capital
            if self.capital_manager:
                self.capital_manager.reservar_capital(symbol, custo_total)

            if self.dry_run:
                self.log.info(f"[DRY RUN] {symbol} | Comprar a {preco_compra:.4f}, Vender a {preco_venda:.4f}")
                self.db.save_trade(symbol, "buy", preco_compra, quantidade, rebate=0, pnl=0)
                self.db.save_trade(symbol, "sell", preco_venda, quantidade, rebate=0, pnl=preco_venda - preco_compra)

                # Liberar capital imediatamente em dry_run
                if self.capital_manager:
                    self.capital_manager.liberar_capital(symbol, custo_total)

            else:
                order = self.executor.place_limit_order(symbol, "buy", preco_compra, quantidade)
                self.log.info(f"{symbol} | Ordem de compra enviada: {order['id']}")
                # Ordem real enviada — só libera capital após venda real
                # Isso será tratado em outro estágio do ciclo

        except Exception as e:
            self.log.error(f"Erro no ciclo de {symbol}: {str(e)}")

            # ⚠️ Em caso de erro, liberar capital reservado
            if self.capital_manager:
                self.capital_manager.liberar_capital(symbol, custo_total)
