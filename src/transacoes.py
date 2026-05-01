from datetime import datetime
from bson import ObjectId
from src.db import get_db
from src.contas import atualizar_saldo_conta
from src.usuarios import atualizar_saldo_usuario


# ─── INSERIR ───────────────────────────────────────────────────────────────
def inserir_transacao(
    usuario_id,
    conta_id,
    valor: float,
    tipo: str,          # "entrada" | "saida"
    descricao: str,
    categoria: dict,    # DOCUMENTO ANINHADO: {"nome": "Alimentação", "icone": "🍔"}
    data: datetime = None,
):
    db = get_db()

    doc = {
        "usuario_id": ObjectId(str(usuario_id)),
        "conta_id": ObjectId(str(conta_id)),    # REFERÊNCIA à coleção contas
        "valor": valor,
        "tipo": tipo,
        "descricao": descricao,
        "data": data or datetime.now(),
        # categoria aninhada: ao listar transações já temos nome e ícone prontos
        "categoria": {
            "nome": categoria["nome"],
            "icone": categoria.get("icone", "💰"),
        },
    }

    result = db["transacoes"].insert_one(doc)

    # Atualiza saldo da conta e do usuário com $inc
    delta = valor if tipo == "entrada" else -valor
    atualizar_saldo_conta(conta_id, delta)
    atualizar_saldo_usuario(usuario_id, delta)

    print(f'📝 Transação "{descricao}" (R${valor:.2f} / {tipo}) registrada.')
    return result.inserted_id


# ─── BUSCAR ────────────────────────────────────────────────────────────────
def buscar_transacoes_por_mes(usuario_id, ano: int, mes: int):
    db = get_db()
    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)

    return list(
        db["transacoes"]
        .find({
            "usuario_id": ObjectId(str(usuario_id)),
            "data": {"$gte": inicio, "$lt": fim},
        })
        .sort("data", -1)
    )


def buscar_transacoes_por_categoria(usuario_id, nome_categoria: str):
    db = get_db()
    return list(
        db["transacoes"]
        .find({
            "usuario_id": ObjectId(str(usuario_id)),
            "categoria.nome": nome_categoria,
        })
        .sort("data", -1)
    )


def buscar_transacao_por_id(transacao_id):
    return get_db()["transacoes"].find_one({"_id": ObjectId(str(transacao_id))})


# ─── ATUALIZAR ─────────────────────────────────────────────────────────────
def atualizar_descricao_transacao(transacao_id, nova_descricao: str):
    db = get_db()
    return db["transacoes"].update_one(
        {"_id": ObjectId(str(transacao_id))},
        {"$set": {"descricao": nova_descricao}}
    )


# ─── DELETAR ───────────────────────────────────────────────────────────────
def deletar_transacao(transacao_id):
    db = get_db()

    # Reverte o saldo antes de deletar
    tx = buscar_transacao_por_id(transacao_id)
    if tx:
        delta = -tx["valor"] if tx["tipo"] == "entrada" else tx["valor"]
        atualizar_saldo_conta(str(tx["conta_id"]), delta)
        atualizar_saldo_usuario(str(tx["usuario_id"]), delta)

    result = db["transacoes"].delete_one({"_id": ObjectId(str(transacao_id))})
    print(f"🗑️  Transação deletada (deleted: {result.deleted_count})")
    return result
