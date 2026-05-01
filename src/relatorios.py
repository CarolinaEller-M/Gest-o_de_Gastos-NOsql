from datetime import datetime
from bson import ObjectId
from src.db import get_db


# ════════════════════════════════════════════════════════════════════════════
# RELATÓRIO 1 — Extrato Detalhado com $lookup e $unwind
# Objetivo: listar transações mostrando os dados completos da conta
# ════════════════════════════════════════════════════════════════════════════
def extrato_detalhado_por_mes(usuario_id, ano: int, mes: int):
    db = get_db()

    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)

    pipeline = [
        # ESTÁGIO 1 — $match: filtra somente as transações do usuário no mês
        {
            "$match": {
                "usuario_id": ObjectId(str(usuario_id)),
                "data": {"$gte": inicio, "$lt": fim},
            }
        },

        # ESTÁGIO 2 — $lookup: faz o JOIN com a coleção "contas"
        # Busca o documento da conta cujo _id bate com o conta_id da transação
        {
            "$lookup": {
                "from": "contas",           # coleção de destino
                "localField": "conta_id",   # campo na transação
                "foreignField": "_id",      # campo na conta
                "as": "dados_conta",        # nome do array resultante
            }
        },

        # ESTÁGIO 3 — $unwind: desmonta o array dados_conta (que tem apenas 1 item)
        # Transforma de array para campo normal, facilitando o acesso
        {
            "$unwind": "$dados_conta"
        },

        # ESTÁGIO 4 — $project: formata o documento final
        {
            "$project": {
                "_id": 1,
                "descricao": 1,
                "valor": 1,
                "tipo": 1,
                "data": 1,
                "categoria.nome": 1,
                "categoria.icone": 1,
                "conta_nome": "$dados_conta.nome",
                "conta_tipo": "$dados_conta.tipo",
            }
        },

        # ESTÁGIO 5 — $sort: do mais recente para o mais antigo
        {"$sort": {"data": -1}},
    ]

    return list(db["transacoes"].aggregate(pipeline))


# ════════════════════════════════════════════════════════════════════════════
# RELATÓRIO 2 — Dashboard Financeiro com $facet
# Objetivo: várias análises em uma única consulta (total gasto, total recebido,
#           ranking por categoria, maior transação do mês)
# ════════════════════════════════════════════════════════════════════════════
def dashboard_mensal(usuario_id, ano: int, mes: int):
    db = get_db()

    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)

    pipeline = [
        # ESTÁGIO 1 — $match: filtra as transações do mês/usuário
        {
            "$match": {
                "usuario_id": ObjectId(str(usuario_id)),
                "data": {"$gte": inicio, "$lt": fim},
            }
        },

        # ESTÁGIO 2 — $facet: executa múltiplos sub-pipelines em paralelo
        # Cada chave é um "painel" independente do dashboard
        {
            "$facet": {

                # PAINEL A — Total de saídas no mês
                "total_gasto": [
                    {"$match": {"tipo": "saida"}},
                    {"$group": {"_id": None, "total": {"$sum": "$valor"}}},
                    {"$project": {"_id": 0, "total": 1}},
                ],

                # PAINEL B — Total de entradas no mês
                "total_recebido": [
                    {"$match": {"tipo": "entrada"}},
                    {"$group": {"_id": None, "total": {"$sum": "$valor"}}},
                    {"$project": {"_id": 0, "total": 1}},
                ],

                # PAINEL C — Ranking de gastos por categoria (top 5)
                "gasto_por_categoria": [
                    {"$match": {"tipo": "saida"}},
                    {
                        "$group": {
                            "_id": "$categoria.nome",
                            "icone": {"$first": "$categoria.icone"},
                            "total": {"$sum": "$valor"},
                            "quantidade": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total": -1}},
                    {"$limit": 5},
                    {
                        "$project": {
                            "_id": 0,
                            "categoria": "$_id",
                            "icone": 1,
                            "total": 1,
                            "quantidade": 1,
                        }
                    },
                ],

                # PAINEL D — Maior transação do mês
                "maior_transacao": [
                    {"$sort": {"valor": -1}},
                    {"$limit": 1},
                    {
                        "$project": {
                            "_id": 0,
                            "descricao": 1,
                            "valor": 1,
                            "tipo": 1,
                            "data": 1,
                            "categoria.nome": 1,
                        }
                    },
                ],

                # PAINEL E — Quantidade de transações por tipo
                "resumo_quantidade": [
                    {
                        "$group": {
                            "_id": "$tipo",
                            "quantidade": {"$sum": 1},
                        }
                    }
                ],
            }
        },
    ]

    resultado = list(db["transacoes"].aggregate(pipeline))
    return resultado[0] if resultado else {}
