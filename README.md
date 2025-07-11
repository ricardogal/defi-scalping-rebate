# DeFi Scalping Bot

Bot automatizado para scalping em exchanges DeFi com estratégias de arbitragem e execução de ordens.

## 🚀 Configuração Inicial

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd defi-scalping
```

### 2. Configure o ambiente
```bash
# Copie o arquivo de configuração de exemplo
cp config.json.example config.json

# Edite o config.json com suas configurações
nano config.json
```

### 3. Configure as variáveis de ambiente
```bash
# Crie um arquivo .env (opcional)
export BINANCE_API_KEY="sua_api_key_aqui"
export BINANCE_API_SECRET="sua_api_secret_aqui"
```

## 📁 Estrutura do Projeto

```
defi-scalping/
├── config.json.example    # Template de configuração
├── config.json           # Configuração real (ignorada pelo git)
├── data/                 # Banco de dados SQLite
├── src/                  # Código fonte
│   ├── controle/         # Controles de ordens
│   ├── core/            # Lógica principal
│   ├── painel/          # Interface de monitoramento
│   ├── repository/      # Acesso ao banco de dados
│   ├── services/        # Serviços externos
│   ├── utils/           # Utilitários
│   └── test/            # Testes unitários
└── README.md
```

## ⚙️ Configuração

### config.json
```json
{
  "dry_run": true,                    // Modo de teste (não executa ordens reais)
  "quantidade_padrao": 0.001,         // Quantidade padrão por ordem
  "spread_alvo": 0.015,              // Spread mínimo para execução
  "slippage_tolerancia": 0.01,        // Tolerância de slippage
  "intervalo_execucao": 10,           // Intervalo entre execuções (segundos)
  "limites_capital": {                // Limites por par de trading
    "BTC/USDT": 20,
    "ETH/USDT": 15,
    "SOL/USDT": 10
  },
  "pares": ["BTC/USDT", "ETH/USDT", "SOL/USDT"]  // Pares para trading
}
```

## 🧪 Testes

### Executar todos os testes
```bash
cd src
python3 -m unittest discover test -v
```

### Executar testes específicos
```bash
python3 -m unittest test.test_cancelador_ordens -v
```

## 🚨 Segurança

⚠️ **IMPORTANTE**: 
- Nunca commite o arquivo `config.json` real
- Mantenha suas chaves de API seguras
- Use sempre `dry_run: true` para testes
- O banco de dados `data/scalping.db` é ignorado pelo git

## 📊 Monitoramento

O bot inclui:
- Logs detalhados de todas as operações
- Painel de monitoramento em tempo real
- Cancelamento automático de ordens pendentes
- Controle de risco por par de trading

## 🔧 Desenvolvimento

### Estrutura de Testes
- Testes unitários em `src/test/`
- Mocks para todas as dependências externas
- Cobertura completa dos cenários principais

### Adicionando Novos Pares
1. Adicione o par em `config.json`
2. Configure o limite de capital
3. Teste com `dry_run: true`

## 📝 Logs

Os logs são salvos no banco de dados e também exibidos no console:
- `[INFO]` - Informações gerais
- `[WARN]` - Avisos importantes
- `[ERROR]` - Erros que precisam atenção
- `[CRITICAL]` - Erros críticos

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Adicione testes para novas funcionalidades
4. Execute os testes antes de commitar
5. Faça um pull request

## 📄 Licença

Este projeto é para uso educacional e de desenvolvimento. Use por sua conta e risco. 