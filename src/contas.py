from datetime import datetime
from bson import ObjectId
from src.db import get_db


# ─── INSERIR ───────────────────────────────────────────────────────────────
def inserir_conta(usuario_id, nome: str, tipo: str, saldo: float = 0):
    # usuario_id é uma REFERÊNCIA (ObjectId) — conta e usuário são entidades independentes
    db = get_db()
    doc = {
        "usuario_id": ObjectId(str(usuario_id)),
        "nome": nome,   # ex: "Conta Corrente Nubank"
        "tipo": tipo,   # "corrente" | "poupanca" | "cartao"
        "saldo": saldo,
        "criada_em": datetime.now(),
    }
    result = db["contas"].insert_one(doc)
    print(f"🏦 Conta inserida: {nome} ({result.inserted_id})")
    return result.inserted_id


# ─── BUSCAR ────────────────────────────────────────────────────────────────
def buscar_contas_por_usuario(usuario_id):
    db = get_db()
    return list(db["contas"].find({"usuario_id": ObjectId(str(usuario_id))}))


def buscar_conta_por_id(conta_id):
    return get_db()["contas"].find_one({"_id": ObjectId(str(conta_id))})


# ─── ATUALIZAR ─────────────────────────────────────────────────────────────
def atualizar_saldo_conta(conta_id, valor: float):
    # $inc — incrementa ou decrementa o saldo da conta (operador obrigatório)
    db = get_db()
    result = db["contas"].update_one(
        {"_id": ObjectId(str(conta_id))},
        {"$inc": {"saldo": valor}}
    )
    print(f"💳 Saldo da conta {conta_id} atualizado em R${valor:.2f}")
    return result


def renomear_conta(conta_id, novo_nome: str):
    db = get_db()
    return db["contas"].update_one(
        {"_id": ObjectId(str(conta_id))},
        {"$set": {"nome": novo_nome}}
    )


# ─── DELETAR ───────────────────────────────────────────────────────────────
def deletar_conta(conta_id):
    db = get_db()
    result = db["contas"].delete_one({"_id": ObjectId(str(conta_id))})
    print(f"❌ Conta deletada (deleted: {result.deleted_count})")
    return result
