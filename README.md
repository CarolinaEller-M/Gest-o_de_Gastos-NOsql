# 💰 Sistema de Finanças Pessoais — MongoDB + Python

Projeto acadêmico de banco de dados NoSQL com MongoDB e Python (pymongo).

---

## 📁 Estrutura de Arquivos

```
financas-mongodb-py/
├── main.py                  → Arquivo principal (demonstração completa)
├── requirements.txt         → Dependências Python
├── data/
│   └── dados_exemplo.json   → Dados de exemplo
└── src/
    ├── __init__.py
    ├── db.py                → Conexão com MongoDB
    ├── usuarios.py          → CRUD + $push, $pull, $inc
    ├── contas.py            → CRUD de contas + $inc
    ├── transacoes.py        → CRUD de transações
    ├── categorias.py        → CRUD de categorias
    └── relatorios.py        → Aggregations ($lookup, $unwind, $facet)
```

---

## ✅ Pré-requisitos

- **Python 3.8+** → https://www.python.org/downloads/
- **MongoDB Community** rodando na porta 27017 → https://www.mongodb.com/try/download/community

---

## 🚀 Como Rodar

### 1. Criar ambiente virtual (recomendado)
```bash
cd financas-mongodb-py
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate

# Ativar no Mac/Linux:
source venv/bin/activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Garantir que o MongoDB está rodando
```bash
# Windows (se instalado como serviço):
net start MongoDB

# Mac (Homebrew):
brew services start mongodb-community

# Linux:
sudo systemctl start mongod
```

### 4. Rodar o projeto
```bash
python main.py
```

---

## ☁️ Usando MongoDB Atlas (sem instalação local)

1. Crie conta gratuita em https://cloud.mongodb.com
2. Crie um cluster M0 (gratuito)
3. Copie a connection string
4. Rode passando a URI como variável de ambiente:

```bash
# Windows (PowerShell):
$env:MONGO_URI="mongodb+srv://usuario:senha@cluster.mongodb.net"
python main.py

# Mac/Linux:
MONGO_URI="mongodb+srv://usuario:senha@cluster.mongodb.net" python main.py
```

---

## 📋 Decisões de Modelagem

| Situação | Escolha | Motivo |
|---|---|---|
| Metas do usuário | **Documento aninhado** | Sempre carregadas junto com o usuário |
| Categoria na transação | **Documento aninhado** | Evita JOIN ao listar transações |
| Transação → Conta | **Referência (ObjectId)** | Conta é entidade independente |
| Transação → Usuário | **Referência (ObjectId)** | Usuário é entidade independente |

---

## 🔧 Operadores MongoDB Utilizados

| Operador | Onde | O que faz |
|---|---|---|
| `$inc` | `usuarios.py`, `contas.py` | Atualiza saldo ao registrar transação |
| `$push` | `usuarios.py` | Adiciona nova meta ao usuário |
| `$pull` | `usuarios.py` | Remove meta específica do usuário |
| `$lookup` | `relatorios.py` | JOIN entre transações e contas |
| `$unwind` | `relatorios.py` | Desmonta array do $lookup |
| `$facet` | `relatorios.py` | 5 análises em uma única consulta |
| `$group` | `relatorios.py` | Agrupa por categoria/tipo |
| `$match` | `relatorios.py` | Filtra por período e usuário |
