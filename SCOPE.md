# Smart Fiscal Auditor - Escopo do Projeto

## 1. Visão Geral

Sistema de automação de processamento de notas fiscais brasileiras usando RPA + IA + ETL + SQL.

**Problema:** Escritórios de contabilidade no Brasil processam centenas de notas fiscais mensalmente, inserindo dados manualmente (CNPJ, datas, valores). Este processo é lento, propenso a erros e caro.

**Solução:** Pipeline automatizado de 4 estágios que transforma arquivos de texto em registros estruturados no banco de dados.

## 2. Arquitetura

```
┌─────────────────┐
│  /inbox folder  │  ← Arquivo .txt chega
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RPA Watchdog  │  ← Detecta novo arquivo
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Extractor   │  ← Lê texto, chama Minimax
│                 │     Retorna JSON estruturado
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ETL Transform  │  ← Limpa CNPJ, formata datas,
│                 │     converte valores para float
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Database   │  ← Salva na tabela notas_fiscais
│                 │     Move arquivo para /processed/
└─────────────────┘
```

## 3. Estágios do Pipeline

### 3.1 RPA - Monitor (Watchdog)
- **Arquivo:** `src/monitor.py`
- **Função:** Monitora pasta `data/inbox/` e detecta novos arquivos .txt
- **Trigger:** Evento `on_created` para novos arquivos
- **Saída:** Callback com caminho do arquivo para processamento

### 3.2 AI - Extractor (Minimax API)
- **Arquivo:** `src/extractor.py`
- **Função:** Extrai dados estruturados do texto da nota fiscal
- **Entrada:** Texto bruto da nota fiscal
- **Saída:** JSON com campos: `cnpj`, `fornecedor`, `data_emissao`, `valor`
- **API:** Minimax Chat Completion API

### 3.3 ETL - Transformer
- **Arquivo:** `src/transformer.py`
- **Função:** Limpa, valida e padroniza dados
- **Transformações:**
  - CNPJ: Remove formatação (pontos, barras, hífens)
  - CNPJ: Validação via algoritmo de dígitos verificadores
  - Data: Conversão de DD/MM/YYYY para datetime
  - Valor: Conversão de formato brasileiro (R$ 1.234,56) para float
- **Validações:** CNPJ válido, campos obrigatórios, valores positivos

### 3.4 SQL - Database (SQLite + SQLAlchemy)
- **Arquivo:** `src/database.py`
- **Banco:** `data/fiscal.db` (SQLite)
- **Tabela:** `notas_fiscais`
- **Campos:**
  - `id` (INTEGER, PK, autoincrement)
  - `cnpj` (VARCHAR(14), indexado)
  - `fornecedor` (VARCHAR(255))
  - `data_emissao` (DATE)
  - `valor` (FLOAT)
  - `arquivo_origem` (VARCHAR(255))
  - `data_processamento` (DATETIME)

## 4. Formato das Notas Fiscais

O sistema processa notas fiscais em texto simples (.txt) com os seguintes campos:

```
NOTA FISCAL DE SERVIÇOS ELETRÔNICA

Fornecedor: [nome da empresa]
CNPJ: [CNPJ com ou sem formatação]
Data de Emissão: [DD/MM/YYYY]
Valor Total: R$ [valor em reais]
```

**Exemplo:**
```
Fornecedor: Tech Solutions Ltda
CNPJ: 44.852.175/0001-00
Data de Emissão: 17/09/2024
Valor Total: R$ 2.500,00
```

## 5. Validação de CNPJ

O CNPJ é validado usando o algoritmo oficial de dígitos verificadores:

1. **Primeiro dígito:** Multiplicação por pesos 5,4,3,2,9,8,7,6,5,4,3,2 e soma
2. **Segundo dígito:** Multiplicação por pesos 6,5,4,3,2,9,8,7,6,5,4,3,2 e soma
3. **Verificação:** Dígitos calculados devem coincidir com os digits 13 e 14

## 6. Testes

### 6.1 Testes Unitários
- **Local:** `tests/`
- **Frameworks:** pytest
- **Cobertura:**
  - `test_transformer.py`: 17 testes (validação CNPJ, parsing de data/valor, transformações)
  - `test_database.py`: 4 testes (CRUD de notas fiscais)

### 6.2 Testes de Integração
- Pipeline completo processando arquivos em `data/inbox/`
- Verificação de registros no banco SQLite

## 7. Estrutura de Diretórios

```
smart-fiscal-auditor/
├── src/
│   ├── __init__.py
│   ├── main.py           # Orquestrador do pipeline
│   ├── monitor.py        # RPA - Watchdog
│   ├── extractor.py      # AI - Minimax API
│   ├── transformer.py    # ETL - Limpeza/validação
│   └── database.py       # SQL - SQLite/SQLAlchemy
├── data/
│   ├── inbox/            # Entrada de notas fiscais
│   ├── processed/        # Notas fiscais processadas
│   └── fiscal.db        # Banco de dados SQLite
├── samples/              # Notas fiscais de exemplo
├── tests/                # Testes unitários
├── .env                 # Variáveis de ambiente (API key)
├── .env.example         # Template de .env
├── requirements.txt     # Dependências Python
├── README.md            # Documentação geral
└── SCOPE.md            # Este arquivo
```

## 8. Configuração

### Variáveis de Ambiente (.env)
```
MINIMAX_API_KEY=sua_chave_aqui
```

### Dependências (requirements.txt)
```
httpx>=0.25.0        # Cliente HTTP
watchdog>=3.0.0     # Monitor de arquivos
sqlalchemy>=2.0.0    # ORM do banco
python-dotenv>=1.0.0 # Variáveis de ambiente
pytest>=7.4.0        # Testes
```

## 9. Fluxo de Execução

1. **Inicialização:**
   ```bash
   python src/main.py
   ```

2. **Monitoramento:**
   - Watchdog observa `data/inbox/`
   - Qualquer arquivo .txt novo dispara o processamento

3. **Processamento (por arquivo):**
   - Leitura do arquivo
   - Extração via Minimax API
   - Transformação/validação
   - Persistência no banco
   - Movimentação para `data/processed/`

4. **Consulta:**
   ```bash
   sqlite3 data/fiscal.db "SELECT * FROM notas_fiscais;"
   ```

## 10. Métricas de Resultado

| Métrica | Alvo | Real |
|---------|------|------|
| Automação | 100% | ✅ |
| Tempo por nota | < 2 seg | ✅ |
| Entrada manual | 0 | ✅ |
| Rastreabilidade | Sim | ✅ |

## 11. Limitações

- Formato de entrada: apenas .txt com estrutura específica
- Não processa PDF ou imagens (sem OCR)
- Não valida CNPJ contra Receita Federal
- Um arquivo por vez (processamento sequencial)

## 12. Melhorias Futuras

- [ ] Suporte OCR para PDF/imagens
- [ ] Validação real de CNPJ contra API da Receita Federal
- [ ] Dashboard web com Streamlit
- [ ] Notificações por email
- [ ] Suporte multi-formato (XML, PDF, TXT)
- [ ] Containerização Docker
- [ ] Relatórios mensais automatizados

---

**Autor:** Portfólio - Junior AI/RPA Developer  
**Tecnologias:** Python, RPA, AI, ETL, SQL, Minimax API
