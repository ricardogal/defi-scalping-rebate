import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import os
import sys

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controle.cancelador_ordens import cancelar_ordens_pendentes, TEMPO_MAXIMO


class TestCanceladorOrdens(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.mock_db = Mock()
        self.mock_log = Mock()
        self.mock_executor = Mock()
        
    @patch('controle.cancelador_ordens.DatabaseRepository')
    @patch('controle.cancelador_ordens.LogService')
    @patch('controle.cancelador_ordens.ExchangeExecutor')
    @patch('controle.cancelador_ordens.os.getenv')
    def test_cancelar_ordens_pendentes_sem_ordens(self, mock_getenv, mock_exchange_executor, mock_log_service, mock_db_repo):
        """Testa quando não há ordens pendentes"""
        # Configurar mocks
        mock_getenv.side_effect = lambda x: "fake_key" if "API_KEY" in x else "fake_secret"
        mock_db_repo.return_value = self.mock_db
        mock_log_service.return_value = self.mock_log
        mock_exchange_executor.return_value = self.mock_executor
        
        # Configurar dados de teste
        self.mock_db.listar_ordens_abertas.return_value = []
        
        # Executar função
        cancelar_ordens_pendentes()
        
        # Verificações
        self.mock_db.listar_ordens_abertas.assert_called_once()
        self.mock_db.close.assert_called_once()
        self.mock_executor.fetch_order_status.assert_not_called()
        self.mock_executor.cancel_order.assert_not_called()

    @patch('controle.cancelador_ordens.DatabaseRepository')
    @patch('controle.cancelador_ordens.LogService')
    @patch('controle.cancelador_ordens.ExchangeExecutor')
    @patch('controle.cancelador_ordens.os.getenv')
    @patch('controle.cancelador_ordens.datetime')
    def test_cancelar_ordens_pendentes_com_ordem_timeout(self, mock_datetime, mock_getenv, mock_exchange_executor, mock_log_service, mock_db_repo):
        """Testa cancelamento de ordem com timeout"""
        # Configurar mocks
        mock_getenv.side_effect = lambda x: "fake_key" if "API_KEY" in x else "fake_secret"
        mock_db_repo.return_value = self.mock_db
        mock_log_service.return_value = self.mock_log
        mock_exchange_executor.return_value = self.mock_executor
        
        # Configurar datetime mock
        agora = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = agora
        mock_datetime.strptime.return_value = agora - timedelta(seconds=TEMPO_MAXIMO + 10)
        
        # Configurar dados de teste
        ordem_antiga = (123, "BTCUSDT", "BUY", 50000.0, 0.001, "2024-01-01 11:58:00")
        self.mock_db.listar_ordens_abertas.return_value = [ordem_antiga]
        
        # Mock do status da ordem
        self.mock_executor.fetch_order_status.return_value = {"status": "open"}
        
        # Executar função
        cancelar_ordens_pendentes()
        
        # Verificações
        self.mock_db.listar_ordens_abertas.assert_called_once()
        self.mock_executor.fetch_order_status.assert_called_once_with(123, "BTCUSDT")
        self.mock_executor.cancel_order.assert_called_once_with(123, "BTCUSDT")
        self.mock_log.warn.assert_called_once_with("🛑 Ordem 123 cancelada por timeout (BTCUSDT)")
        self.mock_db.remover_ordem_aberta.assert_called_once_with(123)
        self.mock_db.close.assert_called_once()

    @patch('controle.cancelador_ordens.DatabaseRepository')
    @patch('controle.cancelador_ordens.LogService')
    @patch('controle.cancelador_ordens.ExchangeExecutor')
    @patch('controle.cancelador_ordens.os.getenv')
    @patch('controle.cancelador_ordens.datetime')
    def test_cancelar_ordens_pendentes_ordem_ja_executada(self, mock_datetime, mock_getenv, mock_exchange_executor, mock_log_service, mock_db_repo):
        """Testa quando a ordem já foi executada"""
        # Configurar mocks
        mock_getenv.side_effect = lambda x: "fake_key" if "API_KEY" in x else "fake_secret"
        mock_db_repo.return_value = self.mock_db
        mock_log_service.return_value = self.mock_log
        mock_exchange_executor.return_value = self.mock_executor
        
        # Configurar datetime mock
        agora = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = agora
        mock_datetime.strptime.return_value = agora - timedelta(seconds=TEMPO_MAXIMO + 10)
        
        # Configurar dados de teste
        ordem_antiga = (123, "BTCUSDT", "BUY", 50000.0, 0.001, "2024-01-01 11:58:00")
        self.mock_db.listar_ordens_abertas.return_value = [ordem_antiga]
        
        # Mock do status da ordem como já executada
        self.mock_executor.fetch_order_status.return_value = {"status": "filled"}
        
        # Executar função
        cancelar_ordens_pendentes()
        
        # Verificações
        self.mock_executor.fetch_order_status.assert_called_once_with(123, "BTCUSDT")
        self.mock_executor.cancel_order.assert_not_called()
        self.mock_log.info.assert_called_once_with("✅ Ordem 123 já executada")
        self.mock_db.remover_ordem_aberta.assert_called_once_with(123)

    @patch('controle.cancelador_ordens.DatabaseRepository')
    @patch('controle.cancelador_ordens.LogService')
    @patch('controle.cancelador_ordens.ExchangeExecutor')
    @patch('controle.cancelador_ordens.os.getenv')
    @patch('controle.cancelador_ordens.datetime')
    def test_cancelar_ordens_pendentes_erro_na_api(self, mock_datetime, mock_getenv, mock_exchange_executor, mock_log_service, mock_db_repo):
        """Testa quando há erro na API da exchange"""
        # Configurar mocks
        mock_getenv.side_effect = lambda x: "fake_key" if "API_KEY" in x else "fake_secret"
        mock_db_repo.return_value = self.mock_db
        mock_log_service.return_value = self.mock_log
        mock_exchange_executor.return_value = self.mock_executor
        
        # Configurar datetime mock
        agora = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = agora
        mock_datetime.strptime.return_value = agora - timedelta(seconds=TEMPO_MAXIMO + 10)
        
        # Configurar dados de teste
        ordem_antiga = (123, "BTCUSDT", "BUY", 50000.0, 0.001, "2024-01-01 11:58:00")
        self.mock_db.listar_ordens_abertas.return_value = [ordem_antiga]
        
        # Mock de erro na API
        self.mock_executor.fetch_order_status.side_effect = Exception("API Error")
        
        # Executar função
        cancelar_ordens_pendentes()
        
        # Verificações
        self.mock_executor.fetch_order_status.assert_called_once_with(123, "BTCUSDT")
        self.mock_executor.cancel_order.assert_not_called()
        self.mock_log.error.assert_called_once_with("Erro ao cancelar 123: API Error")
        self.mock_db.remover_ordem_aberta.assert_called_once_with(123)

    @patch('controle.cancelador_ordens.DatabaseRepository')
    @patch('controle.cancelador_ordens.LogService')
    @patch('controle.cancelador_ordens.ExchangeExecutor')
    @patch('controle.cancelador_ordens.os.getenv')
    @patch('controle.cancelador_ordens.datetime')
    def test_cancelar_ordens_pendentes_ordem_recente(self, mock_datetime, mock_getenv, mock_exchange_executor, mock_log_service, mock_db_repo):
        """Testa quando a ordem é recente e não deve ser cancelada"""
        # Configurar mocks
        mock_getenv.side_effect = lambda x: "fake_key" if "API_KEY" in x else "fake_secret"
        mock_db_repo.return_value = self.mock_db
        mock_log_service.return_value = self.mock_log
        mock_exchange_executor.return_value = self.mock_executor
        
        # Configurar datetime mock
        agora = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = agora
        mock_datetime.strptime.return_value = agora - timedelta(seconds=30)  # Menos que TEMPO_MAXIMO
        
        # Configurar dados de teste
        ordem_recente = (123, "BTCUSDT", "BUY", 50000.0, 0.001, "2024-01-01 11:59:30")
        self.mock_db.listar_ordens_abertas.return_value = [ordem_recente]
        
        # Executar função
        cancelar_ordens_pendentes()
        
        # Verificações
        self.mock_db.listar_ordens_abertas.assert_called_once()
        self.mock_executor.fetch_order_status.assert_not_called()
        self.mock_executor.cancel_order.assert_not_called()
        self.mock_db.remover_ordem_aberta.assert_not_called()
        self.mock_db.close.assert_called_once()

    @patch('controle.cancelador_ordens.DatabaseRepository')
    @patch('controle.cancelador_ordens.LogService')
    @patch('controle.cancelador_ordens.ExchangeExecutor')
    @patch('controle.cancelador_ordens.os.getenv')
    @patch('controle.cancelador_ordens.datetime')
    def test_cancelar_ordens_pendentes_multiplas_ordens(self, mock_datetime, mock_getenv, mock_exchange_executor, mock_log_service, mock_db_repo):
        """Testa cancelamento de múltiplas ordens"""
        # Configurar mocks
        mock_getenv.side_effect = lambda x: "fake_key" if "API_KEY" in x else "fake_secret"
        mock_db_repo.return_value = self.mock_db
        mock_log_service.return_value = self.mock_log
        mock_exchange_executor.return_value = self.mock_executor
        
        # Configurar datetime mock
        agora = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = agora
        mock_datetime.strptime.return_value = agora - timedelta(seconds=TEMPO_MAXIMO + 10)
        
        # Configurar dados de teste - múltiplas ordens
        ordens = [
            (123, "BTCUSDT", "BUY", 50000.0, 0.001, "2024-01-01 11:58:00"),
            (124, "ETHUSDT", "SELL", 3000.0, 0.01, "2024-01-01 11:58:30"),
            (125, "ADAUSDT", "BUY", 0.5, 100.0, "2024-01-01 11:59:00")
        ]
        self.mock_db.listar_ordens_abertas.return_value = ordens
        
        # Mock do status das ordens
        self.mock_executor.fetch_order_status.side_effect = [
            {"status": "open"},
            {"status": "filled"},
            {"status": "open"}
        ]
        
        # Executar função
        cancelar_ordens_pendentes()
        
        # Verificações
        self.assertEqual(self.mock_executor.fetch_order_status.call_count, 3)
        self.assertEqual(self.mock_executor.cancel_order.call_count, 2)  # Apenas ordens com status "open"
        self.assertEqual(self.mock_log.warn.call_count, 2)
        self.assertEqual(self.mock_log.info.call_count, 1)
        self.assertEqual(self.mock_db.remover_ordem_aberta.call_count, 3)

    def test_tempo_maximo_constante(self):
        """Testa se a constante TEMPO_MAXIMO está definida corretamente"""
        self.assertEqual(TEMPO_MAXIMO, 60)


if __name__ == '__main__':
    unittest.main() 