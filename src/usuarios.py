from datetime import datetime
from bson import ObjectId
from src.db import get_db


# ─── INSERIR ───────────────────────────────────────────────────────────────
def inserir_usuario(nome: str, email: str, saldo_total: float = 0, metas: list = None):
    db = get_db()
    doc = {
        "nome": nome,
        "email": email,
        "saldo_total": saldo_total,
        # metas é DOCUMENTO ANINHADO: fica dentro do usuário para carregamento rápido
        "metas": metas or [],  # ex: [{"categoria": "Alimentação", "valor_limite": 800}]
        "criado_em": datetime.now(),
    }
    result = db["usuarios"].insert_one(doc)
    print(f"👤 Usuário inserido: {nome} ({result.inserted_id})")
    return result.inserted_id


# ─── BUSCAR ────────────────────────────────────────────────────────────────
def buscar_usuario_por_email(email: str):
    return get_db()["usuarios"].find_one({"email": email})


def buscar_usuario_por_id(usuario_id):
    return get_db()["usuarios"].find_one({"_id": ObjectId(str(usuario_id))})


def listar_usuarios():
    return list(get_db()["usuarios"].find())


# ─── ATUALIZAR ─────────────────────────────────────────────────────────────
def atualizar_saldo_usuario(usuario_id, valor: float):
    # $inc — incrementa (positivo) ou decrementa (negativo) o saldo
    db = get_db()
    result = db["usuarios"].update_one(
        {"_id": ObjectId(str(usuario_id))},
        {"$inc": {"saldo_total": valor}}
    )
    print(f"💰 Saldo do usuário atualizado em R${valor:.2f} (matched: {result.matched_count})")
    return result


def adicionar_meta(usuario_id, meta: dict):
    # $push — adiciona um item na lista de metas sem reescrever tudo
    db = get_db()
    result = db["usuarios"].update_one(
        {"_id": ObjectId(str(usuario_id))},
        {"$push": {"metas": meta}}
    )
    print(f"🎯 Meta adicionada para usuário {usuario_id}")
    return result


def remover_meta(usuario_id, categoria: str):
    # $pull — remove da lista o item que bate com a condição
    db = get_db()
    result = db["usuarios"].update_one(
        {"_id": ObjectId(str(usuario_id))},
        {"$pull": {"metas": {"categoria": categoria}}}
    )
    print(f'🗑️  Meta "{categoria}" removida do usuário {usuario_id}')
    return result


# ─── DELETAR ───────────────────────────────────────────────────────────────
def deletar_usuario(usuario_id):
    db = get_db()
    result = db["usuarios"].delete_one({"_id": ObjectId(str(usuario_id))})
    print(f"❌ Usuário deletado (deleted: {result.deleted_count})")
    return result
