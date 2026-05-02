"""
relatorios.py — Pipelines de Aggregation Framework

Relatório 1: Extrato detalhado com $lookup + $unwind
Relatório 2: Dashboard financeiro com $facet
"""

from datetime import datetime
from bson import ObjectId
from conexao import obter_db


# ════════════════════════════════════════════════════════════════════
# RELATÓRIO 1 — Extrato Detalhado ($lookup + $unwind)
# ════════════════════════════════════════════════════════════════════

def relatorio_extrato_detalhado(usuario_id: ObjectId, mes: int = None, ano: int = None) -> list:
    """
    Lista transações do usuário com os dados da conta bancária vinculada.

    Pipeline:
      1. $match  — filtra por usuário (e opcionalmente por mês/ano)
      2. $lookup — JOIN com a coleção 'contas' pelo campo conta_id
      3. $unwind — desmancha o array gerado pelo $lookup em campo simples
      4. $project — seleciona apenas os campos úteis para exibição
      5. $sort   — ordena por data decrescente
    """
    db = obter_db()

    # ── Filtro base
    filtro: dict = {"usuario_id": usuario_id}
    if mes and ano:
        inicio = datetime(ano, mes, 1)
        fim = datetime(ano + 1, 1, 1) if mes == 12 else datetime(ano, mes + 1, 1)
        filtro["data"] = {"$gte": inicio, "$lt": fim}

    pipeline = [
        # Etapa 1 — filtra as transações do usuário
        {"$match": filtro},

        # Etapa 2 — junta dados da conta (equivalente ao LEFT JOIN do SQL)
        {"$lookup": {
            "from": "contas",           # coleção de destino
            "localField": "conta_id",   # campo na transação
            "foreignField": "_id",      # campo na conta
            "as": "dados_conta",        # nome do array resultante
        }},

        # Etapa 3 — desmonta o array "dados_conta" em um único subdocumento
        {"$unwind": "$dados_conta"},

        # Etapa 4 — projeta somente o necessário para o extrato
        {"$project": {
            "_id": 1,
            "data": 1,
            "descricao": 1,
            "valor": 1,
            "tipo": 1,
            "categoria_nome": "$categoria.nome",
            "categoria_icone": "$categoria.icone",
            "conta_nome": "$dados_conta.nome",
            "conta_tipo": "$dados_conta.tipo",
        }},

        # Etapa 5 — ordena por data mais recente primeiro
        {"$sort": {"data": -1}},
    ]

    return list(db.transacoes.aggregate(pipeline))


def imprimir_extrato(registros: list):
    print("\n" + "═" * 72)
    print("  📄  EXTRATO DETALHADO")
    print("═" * 72)
    if not registros:
        print("  Nenhuma transação encontrada.")
        return
    for r in registros:
        sinal = "+" if r["tipo"] == "entrada" else "-"
        data_fmt = r["data"].strftime("%d/%m/%Y")
        print(
            f"  {r['categoria_icone']} {data_fmt}  "
            f"{r['descricao']:<28}  "
            f"{sinal}R${r['valor']:>8.2f}  "
            f"[{r['conta_nome']} - {r['conta_tipo']}]"
        )
    print("═" * 72)


# ════════════════════════════════════════════════════════════════════
# RELATÓRIO 2 — Dashboard Financeiro ($facet)
# ════════════════════════════════════════════════════════════════════

def relatorio_dashboard(usuario_id: ObjectId, mes: int, ano: int) -> dict:
    """
    Retorna 4 painéis do dashboard em uma única consulta usando $facet.

    Painéis:
      - total_saidas       → soma de todas as saídas do mês
      - total_entradas     → soma de todas as entradas do mês
      - ranking_categorias → gastos agrupados por categoria (top 5)
      - maior_transacao    → transação de maior valor no mês
    """
    db = obter_db()

    inicio = datetime(ano, mes, 1)
    fim = datetime(ano + 1, 1, 1) if mes == 12 else datetime(ano, mes + 1, 1)

    pipeline = [
        # Etapa 1 — filtra o mês/ano do usuário
        {"$match": {
            "usuario_id": usuario_id,
            "data": {"$gte": inicio, "$lt": fim},
        }},

        # Etapa 2 — $facet: múltiplos sub-pipelines em paralelo
        {"$facet": {

            # Painel A — total de saídas
            "total_saidas": [
                {"$match": {"tipo": "saída"}},
                {"$group": {"_id": None, "total": {"$sum": "$valor"}}},
                {"$project": {"_id": 0, "total": 1}},
            ],

            # Painel B — total de entradas
            "total_entradas": [
                {"$match": {"tipo": "entrada"}},
                {"$group": {"_id": None, "total": {"$sum": "$valor"}}},
                {"$project": {"_id": 0, "total": 1}},
            ],

            # Painel C — ranking de gastos por categoria (top 5)
            "ranking_categorias": [
                {"$match": {"tipo": "saída"}},
                {"$group": {
                    "_id": "$categoria.nome",
                    "icone": {"$first": "$categoria.icone"},
                    "total_gasto": {"$sum": "$valor"},
                    "qtd_transacoes": {"$sum": 1},
                }},
                {"$sort": {"total_gasto": -1}},
                {"$limit": 5},
            ],

            # Painel D — maior transação do mês
            "maior_transacao": [
                {"$sort": {"valor": -1}},
                {"$limit": 1},
                {"$project": {
                    "_id": 0,
                    "descricao": 1,
                    "valor": 1,
                    "tipo": 1,
                    "categoria_nome": "$categoria.nome",
                    "data": 1,
                }},
            ],
        }},
    ]

    resultado = list(db.transacoes.aggregate(pipeline))
    return resultado[0] if resultado else {}


def imprimir_dashboard(dados: dict, mes: int, ano: int):
    nomes_meses = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]
    print("\n" + "═" * 60)
    print(f"  📊  DASHBOARD FINANCEIRO — {nomes_meses[mes]}/{ano}")
    print("═" * 60)

    saidas = dados.get("total_saidas", [{}])
    entradas = dados.get("total_entradas", [{}])
    total_s = saidas[0].get("total", 0) if saidas else 0
    total_e = entradas[0].get("total", 0) if entradas else 0
    saldo_mes = total_e - total_s

    print(f"\n  💚 Total de Entradas  : R$ {total_e:>10.2f}")
    print(f"  ❤️  Total de Saídas    : R$ {total_s:>10.2f}")
    sinal = "+" if saldo_mes >= 0 else ""
    print(f"  💡 Saldo do Mês       : {sinal}R$ {saldo_mes:.2f}")

    print("\n  📌 Ranking de Gastos por Categoria:")
    ranking = dados.get("ranking_categorias", [])
    if ranking:
        for i, cat in enumerate(ranking, 1):
            print(
                f"     {i}. {cat['icone']} {cat['_id']:<18} "
                f"R${cat['total_gasto']:>8.2f}  ({cat['qtd_transacoes']}x)"
            )
    else:
        print("     Sem gastos registrados.")

    print("\n  🏆 Maior Transação do Mês:")
    maior = dados.get("maior_transacao", [])
    if maior:
        m = maior[0]
        print(
            f"     {m['descricao']}  R${m['valor']:.2f}  ({m['tipo']})  "
            f"[{m['categoria_nome']}]"
        )
    else:
        print("     Nenhuma transação.")

    print("═" * 60)
