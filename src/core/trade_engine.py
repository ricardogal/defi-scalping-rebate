from src.core.order_tracker import OrderTracker

class TradeEngine:
    def __init__(self, executor, db_repo, logger, dry_run=True, slippage_tolerance=0.01, capital_manager=None, event_logger=None):
        self.executor = executor
        self.db = db_repo
        self.log = logger
        self.dry_run = dry_run
        self.slippage_tolerance = slippage_tolerance
        self.capital_manager = capital_manager
        if event_logger is None:
            raise ValueError("event_logger não pode ser None")
        self.event_logger = event_logger

    def executar_ciclo(self, symbol, quantidade, book_data, spread_alvo=0.02):
        try:
            ask = book_data["ask"]
            bid = book_data["bid"]
            spread = book_data["spread"]

            self.log.info(f"[CICLO] {symbol} | bid={bid:.4f} | ask={ask:.4f} | spread={spread:.5f} | spread_alvo={spread_alvo:.5f} | dry_run={self.dry_run}")

            if not self.dry_run and spread < spread_alvo:
                self.log.warn(f"{symbol} | Spread insuficiente ({spread:.5f})")
                return
            elif self.dry_run and spread < spread_alvo:
                self.log.info(f"[DRY RUN] {symbol} | Simulando com spread baixo ({spread:.5f}) para teste")

            # Usa quantidade personalizada se disponível, senão usa a padrão
            from src.utils.config_loader import carregar_config
            config = carregar_config()
            quantidades_personalizadas = config.get("quantidades_personalizadas", {})
            quantidade_real = float(quantidades_personalizadas.get(symbol, quantidade))
            
            self.log.info(f"[CICLO] {symbol} | Quantidade: {quantidade_real} (padrão: {quantidade})")

            preco_compra = bid + (self.slippage_tolerance / 2)
            preco_venda = ask - (self.slippage_tolerance / 2)
            custo_total = preco_compra * quantidade_real

            if self.capital_manager and not self.capital_manager.pode_usar_capital(symbol, custo_total):
                self.log.warn(f"{symbol} | Sem capital disponível para nova entrada.")
                return

            if self.capital_manager:
                self.capital_manager.reservar_capital(symbol, custo_total)

            if self.dry_run:
                rebate_estimado = quantidade_real * 0.0001
                pnl_estimado = (preco_venda - preco_compra) * quantidade_real + rebate_estimado

                self.log.info(f"[DRY RUN] {symbol} | Comprar a {preco_compra:.4f}, Vender a {preco_venda:.4f} | Qtd: {quantidade_real}")
                
                self.log.info(f"[DB] Salvar BUY | Preço: {preco_compra:.4f} | Qtd: {quantidade_real:.4f} | Rebate: 0.0000 | PnL: 0.0000")
                self.db.save_trade(symbol, "buy", preco_compra, quantidade_real, rebate=0, pnl=0)
                self.event_logger.log_evento("buy", symbol, f"Comprar a {preco_compra:.4f}")

                self.log.info(f"[DB] Salvar SELL | Preço: {preco_venda:.4f} | Qtd: {quantidade_real:.4f} | Rebate: {rebate_estimado:.6f} | PnL: {pnl_estimado:.6f}")
                self.db.save_trade(symbol, "sell", preco_venda, quantidade_real, rebate=rebate_estimado, pnl=pnl_estimado)
                self.event_logger.log_evento("sell", symbol, f"Vender a {preco_venda:.4f} | P&L: {pnl_estimado:.6f}")


                if self.capital_manager:
                    self.capital_manager.liberar_capital(symbol, custo_total)

            else:
                # Execução real usando os novos métodos
                investment = quantidade_real * preco_compra
                
                # Executa compra
                crypto = symbol.split('/')[0]
                buy_result = self.executor.execute_buy(crypto, investment)
                
                if buy_result:
                    self.log.info(f"✅ Compra executada: {buy_result}")
                    
                    # Salva trade de compra
                    self.db.save_trade(symbol, "buy", buy_result['price'], buy_result['amount'], rebate=0, pnl=0)
                    self.event_logger.log_evento("buy", symbol, f"Compra executada a {buy_result['price']:.4f}")
                    
                    # Executa venda
                    sell_result = self.executor.execute_sell(crypto, buy_result['amount'], entry_price=buy_result['price'])
                    
                    if sell_result:
                        self.log.info(f"✅ Venda executada: {sell_result}")
                        
                        # Calcula P&L e rebate
                        pnl = sell_result.get('pnl_value', 0)
                        rebate = buy_result['amount'] * 0.0001  # Rebate estimado
                        
                        # Salva trade de venda
                        self.db.save_trade(symbol, "sell", sell_result['price'], sell_result['amount'], rebate=rebate, pnl=pnl)
                        self.event_logger.log_evento("sell", symbol, f"Venda executada a {sell_result['price']:.4f} | P&L: {pnl:.6f}")
                    else:
                        self.log.error(f"❌ Falha na venda de {symbol}")
                else:
                    self.log.error(f"❌ Falha na compra de {symbol}")
                
                # Libera capital
                if self.capital_manager:
                    self.capital_manager.liberar_capital(symbol, custo_total)

        except Exception as e:
            self.log.error(f"Erro no ciclo de {symbol}: {str(e)}")
            if self.capital_manager:
                try:
                    self.capital_manager.liberar_capital(symbol, float(preco_compra) * quantidade_real)
                except:
                    pass
