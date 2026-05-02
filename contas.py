"""
contas.py — CRUD da coleção 'contas'
Cada conta referencia um usuário por ObjectId (referência lógica).
"""

from datetime import datetime
from bson import ObjectId
from conexao import obter_db


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────

def inserir_conta(usuario_id: ObjectId, nome: str, tipo: str, saldo: float = 0.0) -> ObjectId:
    """
    Cria uma conta bancária vinculada ao usuário.
    tipo: 'corrente' | 'poupança' | 'cartão'
    usuario_id é armazenado como referência (ObjectId).
    """
    db = obter_db()
    doc = {
        "usuario_id": usuario_id,   # referência lógica por ObjectId
        "nome": nome,
        "tipo": tipo,
        "saldo": saldo,
        "criado_em": datetime.utcnow(),
    }
    resultado = db.contas.insert_one(doc)
    print(f"  ✔ Conta inserida '{nome}' ({tipo}) | id={resultado.inserted_id}")
    return resultado.inserted_id


# ──────────────────────────────────────────────
# READ
# ──────────────────────────────────────────────

def buscar_conta_por_id(conta_id: ObjectId) -> dict | None:
    db = obter_db()
    return db.contas.find_one({"_id": conta_id})


def buscar_contas_por_usuario(usuario_id: ObjectId) -> list:
    db = obter_db()
    return list(db.contas.find({"usuario_id": usuario_id}))


# ──────────────────────────────────────────────
# UPDATE — $inc
# ──────────────────────────────────────────────

def atualizar_saldo_conta(conta_id: ObjectId, valor: float):
    """
    Usa $inc para incrementar (+) ou decrementar (-) o saldo da conta.
    Chamado automaticamente ao registrar uma transação.
    """
    db = obter_db()
    db.contas.update_one(
        {"_id": conta_id},
        {"$inc": {"saldo": valor}}
    )
    sinal = "+" if valor >= 0 else ""
    print(f"  ✔ Saldo da conta atualizado ({sinal}R${valor:.2f}) via $inc")


def renomear_conta(conta_id: ObjectId, novo_nome: str):
    db = obter_db()
    db.contas.update_one({"_id": conta_id}, {"$set": {"nome": novo_nome}})
    print(f"  ✔ Conta renomeada para '{novo_nome}'")


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def deletar_conta(conta_id: ObjectId) -> int:
    db = obter_db()
    resultado = db.contas.delete_one({"_id": conta_id})
    print(f"  ✔ Conta deletada | documentos removidos={resultado.deleted_count}")
    return resultado.deleted_count
