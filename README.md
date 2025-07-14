# 🤖 Bot Scalping Rebate - DeFi

Bot de trading autônomo que lucra com rebates (maker fee positiva) e micro-spreads no mercado spot da Binance. Desenvolvido com arquitetura modular, painel CLI dinâmico, controle de capital por par e registro completo de eventos e trades em banco SQLite.

---

## 🚀 Funcionalidades

* Envia ordens limit (maker) para tentar lucrar com o rebate da Binance
* Opera apenas quando há spread suficiente (0.3%+) e liquidez real
* Executa microtrades automáticos com controle de capital por par
* Painel CLI ao vivo com P&L e rebates acumulados
* Sistema de logs e eventos auditáveis para replay
* Totalmente configurável via `config.json`
* Modo dry_run para testes seguros
* Cancelamento automático de ordens pendentes

---

## 🧱 Estrutura de Pastas

```
defi-scalping/
├── config.json              # Parâmetros gerais de execução
├── .env                     # Chaves da API Binance
├── data/                    # Banco SQLite persistente
├── run.py                   # Script principal de execução
├── stop_bot.py              # Script para parar o bot
├── src/
│   ├── main.py              # Loop principal
│   ├── start_bot.py         # Inicialização do bot
│   ├── simulate_one.py      # Executa 1 ciclo isolado (dry run)
│   ├── painel/
│   │   ├── painel_live.py   # Painel dinâmico com Rich
│   │   └── replay_cli.py    # Visualiza eventos passados
│   ├── core/
│   │   ├── trade_engine.py  # Lógica principal de decisão
│   │   └── order_tracker.py # Execução real protegida
│   ├── controle/
│   │   ├── capital_manager.py
│   │   └── cancelador_ordens.py
│   ├── repository/
│   │   └── database_repository.py
│   ├── scanners/
│   │   └── spread_scanner.py
│   ├── services/
│   │   ├── log_service.py
│   │   ├── event_logger.py
│   │   └── exchange_executor.py
│   └── utils/
│       └── config_loader.py
```

---

## ⚙️ Instalação

1. **Clone o projeto**:

```bash
git clone https://github.com/seu-usuario/defi-scalping.git
cd defi-scalping
```

2. **Crie o ambiente virtual**:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instale dependências**:

```bash
pip install python-binance python-dotenv rich sqlite3
```

4. **Configure a API da Binance** no `.env`:

```
BINANCE_API_KEY="sua_key"
BINANCE_API_SECRET="seu_secret"
```

5. **Configure o `config.json`** com:

* Pares que deseja operar
* Capital por par
* Spread alvo (0.3% recomendado)
* Quantidade por trade
* Modo dry_run (true para testes)

---

## ▶️ Execução

### Rodar o bot principal:

```bash
python run.py main
```

### Parar o bot e cancelar ordens:

```bash
python run.py stop
```

### Cancelar ordens pendentes:

```bash
python run.py cancelador
```

### Ver painel dinâmico:

```bash
python run.py painel
```

### Executar apenas 1 ciclo (dry run):

```bash
python src/simulate_one.py
```

---

## 🧠 Funcionamento Interno

* **main.py** roda ciclos de execução buscando pares com spread ideal
* O **TradeEngine** decide se deve operar baseado no spread alvo
* Se `dry_run = false`, o **ExchangeExecutor** executa a operação real com:

  * ordem de compra limit
  * aguardo de execução
  * ordem de venda limit
  * cálculo de rebate real
  * registro de lucro no banco
* Logs e eventos são registrados para posterior replay ou auditoria

---

## 🔐 Cuidados e Segurança

### ❗ Caso o bot falhe:

* **Verifique a API** na Binance: pode estar suspensa ou limitada
* Veja o painel/replay para descobrir onde parou
* Ordens abertas podem ser vistas na própria Binance Spot
* Rode `python run.py stop` para encerrar pendências automaticamente

### ⚠️ Cuidados:

* **Não rode o bot em conta com fundos grandes sem antes testar com dry_run=true**
* Mantenha as chaves `.env` seguras (sem subir no GitHub)
* Tenha saldo em USDT e ative permissão para Spot Trade na API da Binance
* Monitore o painel e os logs periodicamente
* Configure spreads realistas (0.3%+) para garantir lucro

---

## 📊 Configuração Recomendada

Para saldo de ~$20 USD:

```json
{
  "spread_alvo": 0.003,
  "capital_por_par": 2.0,
  "quantidades_personalizadas": {
    "BTC/USDT": 0.0001,
    "ETH/USDT": 0.001,
    "SOL/USDT": 0.01,
    "XRP/USDT": 10,
    "DOGE/USDT": 100,
    "ADA/USDT": 10,
    "LTC/USDT": 0.1
  }
}
```

---

## 📌 Diagnóstico Rápido

| Problema               | Onde olhar                           | Solução                    |
| ---------------------- | ------------------------------------ | -------------------------- |
| Bot não entra em trade | Painel, ver spread                   | `python run.py painel`     |
| Ordem nunca executa    | Timeout no `exchange_executor.py`    | Ajustar slippage           |
| Erro de capital        | `capital_manager.py`                 | Aumentar capital_por_par  |
| Lucro negativo         | Ver P&L + rebate                    | Aumentar spread_alvo       |
| Evento inesperado      | `replay_cli.py` e `event_logger.py`  | Ver logs                   |
| Ordem ficou presa      | Banco: `ordens_abertas` + cancelador | `python run.py stop`       |

---

## ✅ Status Atual

O bot está **100% funcional** em modo real, com:

✅ Conexão com API Binance  
✅ Scanner de spreads funcionando  
✅ Controle de capital por par  
✅ Execução real de ordens  
✅ Logs detalhados  
✅ Painel em tempo real  
✅ Cancelamento automático  
✅ Configuração flexível  

**Pronto para operar com spreads de 0.3%+ para garantir lucro.**

---

*Desenvolvido com foco em performance, controle e autonomia total. Sem promessa de lucro, mas com garantia de rastreabilidade.*
