# 💰 Sistema Financeiro Pessoal — MongoDB + Python

Projeto de banco de dados NoSQL com MongoDB, implementado em Python puro com CLI interativa.

---

## 📁 Estrutura de Arquivos

```
financeiro_app/
├── conexao.py        → Conexão com o MongoDB
├── usuarios.py       → CRUD de usuários ($inc, $push, $pull)
├── contas.py         → CRUD de contas bancárias ($inc)
├── transacoes.py     → CRUD de transações (com doc. aninhado)
├── categorias.py     → CRUD de categorias do sistema
├── relatorios.py     → Aggregation: $lookup/$unwind + $facet
├── dados_exemplo.py  → Script para popular o banco com dados de demo
├── main.py           → Arquivo principal com menu CLI
└── requirements.txt  → Dependências Python
```

---

## ✅ Pré-requisitos

1. **Python 3.11+** instalado  
2. **MongoDB** instalado e rodando localmente

### Instalar MongoDB (caso não tenha)

- **Windows**: https://www.mongodb.com/try/download/community  
- **macOS**: `brew install mongodb-community`  
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt install -y mongodb
  sudo systemctl start mongodb
  ```

---

## 🚀 Como Rodar

### 1. Instale as dependências Python

```bash
pip install -r requirements.txt
```

### 2. Confirme que o MongoDB está rodando

```bash
# Linux/macOS
sudo systemctl status mongodb

# Ou tente conectar:
mongosh
```

### 3. (Opcional) Popule o banco com dados de exemplo

```bash
python dados_exemplo.py
```

Isso cria:
- 2 usuários (Ana Silva e Bruno Costa)
- 3 contas bancárias
- ~17 transações em maio/2025
- 9 categorias padrão

### 4. Execute o sistema

```bash
python main.py
```

---

## 🎯 Funcionalidades

### Menu Interativo (CLI)
- **[1] CRUD de Usuários** — inserir, listar, adicionar/remover metas
- **[2] CRUD de Contas** — inserir, listar, ajustar saldo
- **[3] CRUD de Transações** — registrar, listar por mês, deletar
- **[4] Extrato Detalhado** — usa `$lookup` + `$unwind`
- **[5] Dashboard** — usa `$facet` com 4 painéis simultâneos
- **[6] Demonstração Automática** — roda tudo sem precisar digitar

---

## 🗃️ Modelagem do Banco

### Coleção `usuarios`
```json
{
  "nome": "Ana Silva",
  "email": "ana@email.com",
  "saldo_total": 4550.00,
  "metas_mensais": [
    { "categoria": "Alimentação", "valor_limite": 400, "mes": 5, "ano": 2025 }
  ]
}
```
> 📌 `metas_mensais` é um **documento aninhado** — carregado junto sem JOIN extra.

### Coleção `contas`
```json
{
  "usuario_id": ObjectId("..."),
  "nome": "Nubank Corrente",
  "tipo": "corrente",
  "saldo": 2345.50
}
```
> 📌 `usuario_id` é uma **referência lógica** por ObjectId.

### Coleção `transacoes`
```json
{
  "usuario_id": ObjectId("..."),
  "conta_id": ObjectId("..."),
  "valor": 320.00,
  "tipo": "saída",
  "descricao": "Supermercado",
  "data": ISODate("2025-05-05"),
  "categoria": { "nome": "Alimentação", "icone": "🍔" }
}
```
> 📌 `categoria` é **documento aninhado** — nome e ícone disponíveis sem JOIN.

---

## 🔧 Operadores Avançados Usados

| Operador | Onde | O que faz |
|----------|------|-----------|
| `$inc`   | `contas.py`, `usuarios.py` | Incrementa/decrementa saldo automaticamente ao registrar transação |
| `$push`  | `usuarios.py` | Adiciona meta mensal ao array embutido |
| `$pull`  | `usuarios.py` | Remove meta mensal específica do array |
| `$lookup`| `relatorios.py` | JOIN entre transações e contas |
| `$unwind`| `relatorios.py` | Desmonta array do $lookup em campo simples |
| `$facet` | `relatorios.py` | 4 sub-pipelines em uma única query (dashboard) |

---

## 📊 Relatórios de Aggregation

### Relatório 1 — Extrato Detalhado
```
$match → $lookup → $unwind → $project → $sort
```
Mostra transações com dados da conta bancária vinculada em uma linha só.

### Relatório 2 — Dashboard com $facet
```
$match → $facet:
  ├── total_saidas       ($match saída → $group → $sum)
  ├── total_entradas     ($match entrada → $group → $sum)
  ├── ranking_categorias ($match saída → $group → $sort → $limit 5)
  └── maior_transacao    ($sort → $limit 1)
```
Quatro análises em uma única consulta ao banco.

---

## ⚙️ Configuração do MongoDB

Por padrão o sistema conecta em `mongodb://localhost:27017`.  
Para alterar, edite a linha em `main.py`:

```python
conectar(uri="mongodb://SEU_HOST:27017", nome_banco="financeiro_app")
```
