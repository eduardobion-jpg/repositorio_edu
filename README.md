# Painel Operacional - Loja (Flask + SQLite)

Aplicação web que consolida dados de vendas, estoque e logística em um dashboard interativo.

## 📋 Requisitos

- Python 3.13+
- pip (gerenciador de pacotes)
- Virtualenv (recomendado)

## 🚀 Instalação e Execução

### 1. Ativar Virtualenv (Windows PowerShell)

```powershell
# Navegar até o diretório do projeto
cd "D:\Python\estudo_de_aplicativos\analise_de_dados_flask\analise_de_dados_flask"

# Ativar a virtualenv
.\env\Scripts\Activate.ps1

# Ou executar Python da virtualenv diretamente
& '.\env\Scripts\python.exe' app.py
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

Dependências:
- **Flask 3.0.3** - Framework web
- **SQLAlchemy 2.0.32** - ORM e acesso ao banco de dados
- **pandas 2.2.2** - Manipulação e agregação de dados

### 3. Criar/Atualizar Banco de Dados

```bash
python setup_db.py
```

Este script cria ou atualiza `loja.db` a partir dos CSVs em `data/`.

### 4. Executar o Servidor

```bash
python app.py
```

O servidor iniciará em: **http://127.0.0.1:5050**

## 📊 Funcionalidades

### Dashboard (/)
- KPIs consolidados (receita, pedidos, estoque, entregas)
- Gráfico de receita por produto (top 5)
- Gráfico de pedidos por status
- Evolução mensal de receita

### Vendas (/vendas)
- Lista de todas as vendas
- Filtro por status (todas, concluída, pendente, cancelada)
- Informações: produto, cliente, data, quantidade, valor

### Estoque (/estoque)
- Inventário de produtos
- Identificação de produtos críticos (abaixo do mínimo)
- Valor de estoque por categoria
- Ordenação por categoria e nome

### Logística (/logistica)
- Rastreamento de envios
- Status de entrega (entregue, em trânsito, cancelada)
- Ranking de transportadoras por atraso médio
- Localização e datas de despacho/entrega

## 🗂️ Estrutura do Projeto

```
analise_de_dados_flask/
├── app.py                  # Aplicação Flask (rotas, lógica de negócio)
├── setup_db.py             # Script para criar/popular banco de dados
├── requirements.txt        # Dependências Python
├── loja.db                 # Banco SQLite (gerado por setup_db.py)
├── env/                    # Virtualenv (criado automaticamente)
├── data/                   # CSVs de origem
│   ├── vendas.csv
│   ├── estoque.csv
│   └── logistica.csv
├── templates/              # Templates Jinja2
│   ├── base.html           # Layout base (sidebar + main)
│   ├── dashboard.html      # Dashboard
│   ├── vendas.html         # Página de vendas
│   ├── estoque.html        # Página de estoque
│   └── logistica.html      # Página de logística
└── static/                 # Arquivos estáticos
	└── css/
		└── style.css       # Folha de estilos
```

## 🔧 Configuração

### Host e Porta

No final de `app.py`:

```python
app.run(debug=True, host="127.0.0.1", port=5050, use_reloader=False)
```

- **host**: `127.0.0.1` (apenas localhost) ou `0.0.0.0` (acessível na rede)
- **port**: `5050` (pode ser alterado para outro valor disponível)
- **debug**: `True` (modo desenvolvimento) ou `False` (produção)
- **use_reloader**: `False` (evita recarregamento duplo)

### Acesso Remoto

Para acessar de outro computador, altere o host para `0.0.0.0`:

```python
app.run(debug=True, host="0.0.0.0", port=5050, use_reloader=False)
```

Então acesse de outro PC via: `http://<IP_DO_SERVIDOR>:5050`

## ⚠️ Notas Importantes

### Problema Conhecido: Deadlock com pd.to_datetime()

A função `pd.to_datetime()` pode causar deadlock dentro do contexto Flask em alguns ambientes. Por isso:
- ✅ Agregação mensal é feita diretamente no SQL (não em pandas)
- ✅ Use `pd.Period()` com strings "YYYY-MM" em vez de datetime completo quando necessário

### Desenvolvimento vs. Produção

**Desenvolvimento:**
- Use `python app.py` com `debug=True`
- Acesse via localhost (`127.0.0.1:5050`)

**Produção:**
- Use um servidor WSGI (Gunicorn, uWSGI, etc.)
- Configure `debug=False`
- Use host `0.0.0.0` ou IP específico

## 🐛 Solução de Problemas

### Servidor não inicia
```bash
# Verificar se loja.db existe
Test-Path loja.db

# Se não existir, criar:
python setup_db.py
```

### Porta 5050 já está em uso
Altere em `app.py`:
```python
app.run(debug=True, host="127.0.0.1", port=5051, use_reloader=False)
```

### ModuleNotFoundError: No module named 'flask'
```bash
pip install -r requirements.txt
```

## 📝 Licença

Projeto educacional para análise de dados.
