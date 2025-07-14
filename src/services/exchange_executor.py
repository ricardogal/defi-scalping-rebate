import ccxt
from datetime import datetime

class ExchangeExecutor:
    def __init__(self, api_key, secret, exchange_name='binance'):
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'rateLimit': 100,  # Reduzido para melhor performance
            'timeout': 10000,  # Timeout de 10 segundos
            'options': {
                'defaultType': 'spot',  # Especifica tipo de mercado
                'adjustForTimeDifference': True,
                'warnOnFetchOpenOrdersWithoutSymbol': False,  # Suprime aviso de rate limiting
            }
        })

    def place_limit_order(self, symbol, side, price, quantity):
        if side.lower() == "buy":
            return self.exchange.create_limit_buy_order(symbol, quantity, price)
        elif side.lower() == "sell":
            return self.exchange.create_limit_sell_order(symbol, quantity, price)
        else:
            raise ValueError("Side must be 'buy' or 'sell'")

    def cancel_order(self, order_id, symbol):
        return self.exchange.cancel_order(order_id, symbol)

    def fetch_order_status(self, order_id, symbol):
        return self.exchange.fetch_order(order_id, symbol)

    def get_balance(self, asset=None):
        balance = self.exchange.fetch_balance()
        if asset:
            return balance['free'].get(asset, 0)
        return balance['free']

    def get_fee_info(self):
        return self.exchange.fetch_trading_fee()

    def fetch_order_fills(self, order_id, symbol):
        """Retorna as informações detalhadas de preenchimento da ordem (rebate, fee, etc)"""
        order = self.exchange.fetch_order(order_id, symbol)
        return order.get("trades", []) or order.get("fills", [])

    def listar_ordens_abertas(self):
        """Lista ordens abertas na conta"""
        try:
            return self.exchange.fetch_open_orders()
        except Exception as e:
            print(f"[ERRO] Falha ao listar ordens abertas: {e}")
            return []

    def ajustar_quantidade_para_venda(self, amount, free_balance, market, current_price):
        """
        Ajusta o valor de venda respeitando o saldo disponível, stepSize, minQty, minNotional e precision.
        """
        from math import floor

        limits = market.get('limits', {})
        amount_limit = limits.get('amount', {})
        cost_limit = limits.get('cost', {})
        precision = market.get('precision', {}).get('amount', 8)

        step_size = amount_limit.get('step', 10 ** -precision)
        min_qty = amount_limit.get('min', 0)
        min_cost = cost_limit.get('min', 0)

        amount = min(amount, free_balance)
        amount = floor(amount / step_size) * step_size
        amount = float(f"{amount:.{precision}f}")

        if amount < min_qty:
            raise ValueError(f"Quantidade ajustada {amount} abaixo do mínimo permitido: {min_qty}")

        order_value = amount * current_price
        if min_cost and order_value < min_cost:
            raise ValueError(f"Valor da ordem {order_value:.2f} abaixo do mínimo permitido: {min_cost:.2f}")

        return amount

    def execute_buy(self, crypto, investment, quote='USDT', strategy='scalping'):
        """
        Executa uma ordem de compra genérica.
        - Verifica mínimos da exchange
        - Executa a ordem
        - Registra a posição
        - Retorna os dados reais da compra ou None
        """
        try:
            # 1. Busca informações do mercado
            symbol = f"{crypto}/{quote}"
            market = self.exchange.market(symbol)
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            print(f"[BUY] {crypto}: Preço atual: {current_price}")

            # 2. Verifica valor mínimo da exchange
            min_cost = market['limits']['cost'].get('min', 0)
            if min_cost and investment < min_cost:
                print(f"❌ [BUY] {crypto}: Investimento {quote} {investment:.2f} abaixo do mínimo da Binance {quote} {min_cost:.2f}")
                return None

            # 3. Calcula quantidade a comprar, respeitando precisão
            amount = investment / current_price
            precision = market['precision']['amount']
            amount = float(('{:.' + str(precision) + 'f}').format(amount))
            print(f"[BUY] {crypto}: Quantidade calculada: {amount}")

            # 4. Executa ordem de compra
            try:
                order = self.exchange.create_market_buy_order(symbol, amount, {'recvWindow': 60000})
                filled = order.get('filled', 0)
                avg_price = order.get('average', current_price)
                print(f"[BUY] {crypto}: Ordem executada. Filled: {filled}, Preço médio: {avg_price}")
                
                if filled > 0:
                    print(f"✅ [BUY] {crypto}: COMPRA EFETIVADA | Qtd: {filled:.6f} | Preço: {avg_price:.6f}")
                    
                    return {
                        'symbol': symbol,
                        'amount': filled,
                        'price': avg_price,
                        'order_id': order.get('id'),
                        'time': datetime.now()
                    }
                else:
                    print(f"❌ [BUY] {crypto}: Ordem de compra não executada (filled=0)")
                    return None
                    
            except Exception as e:
                # Trata erro de valor abaixo do mínimo (NOTIONAL)
                if 'notional' in str(e).lower() or 'filter failure' in str(e).lower():
                    print(f"❌ [BUY] {crypto}: Valor abaixo do mínimo permitido para compra ({quote}). Erro: {e}")
                    return None
                print(f"[BUY] {crypto}: Erro ao executar ordem de compra: {e}")
                return None
                
        except Exception as e:
            print(f"[BUY] {crypto}: Erro geral na execução de compra: {e}")
            return None

    def execute_sell(self, crypto, amount, quote='USDT', entry_price=None, strategy='scalping'):
        """
        Executa uma ordem de venda genérica.
        - Ajusta quantidade para limites da exchange
        - Executa a ordem
        - Calcula P&L se entry_price fornecido
        - Retorna os dados da venda ou None
        """
        try:
            symbol = f"{crypto}/{quote}"
            market = self.exchange.market(symbol)
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            print(f"[SELL] {crypto}: Preço atual: {current_price}")

            balance = self.exchange.fetch_balance({'recvWindow': 60000})
            free_balance = balance.get('free', {})
            free_available = float(free_balance.get(crypto, 0))

            try:
                amount = self.ajustar_quantidade_para_venda(amount, free_available, market, current_price)
            except ValueError as ve:
                print(f"❌ [SELL] {crypto}: {ve}")
                return None

            print(f"[SELL] {crypto}: Quantidade final ajustada: {amount}")

            order = self.exchange.create_market_sell_order(symbol, amount, {'recvWindow': 60000})
            filled = order.get('filled', 0)
            avg_price = order.get('average', current_price)
            print(f"[SELL] {crypto}: Ordem executada. Filled: {filled}, Preço médio: {avg_price}")

            if filled > 0:
                pnl_info = ""
                pnl_percent = None
                pnl_value = None
                if entry_price:
                    pnl_percent = ((avg_price / entry_price) - 1) * 100
                    pnl_value = (avg_price - entry_price) * filled
                    pnl_info = f" | P&L: {pnl_percent:+.2f}% ({quote} {pnl_value:+.2f})"

                print(f"✅ [SELL] {crypto}: VENDA EFETIVADA | Qtd: {filled:.6f} | Preço: {avg_price:.6f}{pnl_info}")

                return {
                    'symbol': symbol,
                    'amount': filled,
                    'price': avg_price,
                    'order_id': order.get('id'),
                    'time': datetime.now(),
                    'pnl_percent': pnl_percent if entry_price else None,
                    'pnl_value': pnl_value if entry_price else None
                }
            else:
                print(f"❌ [SELL] {crypto}: Ordem de venda não executada (filled=0)")
                return None

        except Exception as e:
            print(f"[SELL] {crypto}: Erro geral na execução de venda: {e}")
            return None
   