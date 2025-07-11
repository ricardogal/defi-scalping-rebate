class CapitalManager:
    def __init__(self, limite_por_par):
        """
        limite_por_par = {
            "BTC/USDT": 10,
            "ETH/USDT": 20
        }
        """
        self.limite_por_par = limite_por_par
        self.capital_em_uso = {}  # Ex: {"BTC/USDT": 10.0}

    def pode_usar_capital(self, par, valor):
        """Verifica se há saldo liberado para usar no par"""
        usado = self.capital_em_uso.get(par, 0)
        limite = self.limite_por_par.get(par, 0)
        return (usado + valor) <= limite

    def reservar_capital(self, par, valor):
        """Reserva parte do capital no par"""
        if par not in self.capital_em_uso:
            self.capital_em_uso[par] = 0
        self.capital_em_uso[par] += valor

    def liberar_capital(self, par, valor):
        """Libera o capital quando a posição se encerra"""
        if par in self.capital_em_uso:
            self.capital_em_uso[par] -= valor
            if self.capital_em_uso[par] < 0:
                self.capital_em_uso[par] = 0
