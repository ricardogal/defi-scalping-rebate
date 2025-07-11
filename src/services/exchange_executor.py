import ccxt

class ExchangeExecutor:
    def __init__(self, api_key, secret, exchange_name='binance'):
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
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
