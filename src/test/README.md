# Testes Unitários

Esta pasta contém todos os testes unitários do projeto DeFi Scalping.

## Como Executar os Testes

### Executar todos os testes
```bash
cd src
python3 -m unittest discover test -v
```

### Executar um teste específico
```bash
cd src
python3 -m unittest test.test_cancelador_ordens.TestCanceladorOrdens.test_cancelar_ordens_pendentes_sem_ordens -v
```

### Executar com cobertura (se tiver coverage instalado)
```bash
pip install coverage
cd src
coverage run -m unittest discover test
coverage report
coverage html  # Gera relatório HTML
```

## Testes Disponíveis

### `test_cancelador_ordens.py`
Testes para o módulo `cancelador_ordens.py` que gerencia o cancelamento automático de ordens pendentes.

#### Casos de Teste:

1. **`test_cancelar_ordens_pendentes_sem_ordens`**
   - **Cenário**: Não há ordens pendentes no banco de dados
   - **Verificação**: Confirma que nenhuma operação de cancelamento é executada

2. **`test_cancelar_ordens_pendentes_com_ordem_timeout`**
   - **Cenário**: Ordem com mais de 60 segundos (TEMPO_MAXIMO)
   - **Verificação**: Confirma que a ordem é cancelada e logado o aviso

3. **`test_cancelar_ordens_pendentes_ordem_ja_executada`**
   - **Cenário**: Ordem antiga mas já executada (status "filled")
   - **Verificação**: Confirma que não tenta cancelar e loga informação

4. **`test_cancelar_ordens_pendentes_erro_na_api`**
   - **Cenário**: Erro na API da exchange
   - **Verificação**: Confirma que o erro é logado e a ordem é removida do banco

5. **`test_cancelar_ordens_pendentes_ordem_recente`**
   - **Cenário**: Ordem recente (menos de 60 segundos)
   - **Verificação**: Confirma que a ordem não é processada

6. **`test_cancelar_ordens_pendentes_multiplas_ordens`**
   - **Cenário**: Múltiplas ordens com diferentes status
   - **Verificação**: Confirma que apenas ordens "open" são canceladas

7. **`test_tempo_maximo_constante`**
   - **Cenário**: Verificação da constante TEMPO_MAXIMO
   - **Verificação**: Confirma que o valor é 60 segundos

## Mocks Utilizados

Os testes utilizam mocks para isolar o código testado das dependências externas:

- **DatabaseRepository**: Mock do banco de dados
- **LogService**: Mock do serviço de logs
- **ExchangeExecutor**: Mock da API da exchange
- **datetime**: Mock para controlar o tempo nos testes
- **os.getenv**: Mock das variáveis de ambiente

## Estrutura dos Testes

Cada teste segue o padrão AAA (Arrange, Act, Assert):

1. **Arrange**: Configuração dos mocks e dados de teste
2. **Act**: Execução da função testada
3. **Assert**: Verificação das chamadas aos mocks e comportamento esperado

## Dependências

Os testes não requerem dependências externas além das bibliotecas padrão do Python:
- `unittest`
- `unittest.mock`
- `datetime`

## Observações

- Os testes são independentes e podem ser executados em qualquer ordem
- Cada teste configura seus próprios mocks no `setUp()`
- O arquivo de teste inclui o diretório pai no `sys.path` para importar os módulos
- Todos os testes passaram com sucesso ✅ 