"""
usuarios.py — CRUD da coleção 'usuarios'
Cada usuário contém metas mensais embutidas (documento aninhado).
"""

from datetime import datetime
from bson import ObjectId
from conexao import obter_db


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────

def inserir_usuario(nome: str, email: str, saldo_total: float = 0.0) -> ObjectId:
    """Cria um novo usuário com lista de metas vazia."""
    db = obter_db()
    doc = {
        "nome": nome,
        "email": email,
        "saldo_total": saldo_total,
        "metas_mensais": [],          # lista embutida – documento aninhado
        "criado_em": datetime.utcnow(),
    }
    resultado = db.usuarios.insert_one(doc)
    print(f"  ✔ Usuário inserido | id={resultado.inserted_id}")
    return resultado.inserted_id


# ──────────────────────────────────────────────
# READ
# ──────────────────────────────────────────────

def buscar_usuario_por_id(usuario_id: ObjectId) -> dict | None:
    db = obter_db()
    return db.usuarios.find_one({"_id": usuario_id})


def buscar_todos_usuarios() -> list:
    db = obter_db()
    return list(db.usuarios.find())


# ──────────────────────────────────────────────
# UPDATE — $inc, $push, $pull
# ──────────────────────────────────────────────

def atualizar_saldo_usuario(usuario_id: ObjectId, valor: float):
    """
    Usa $inc para incrementar ou decrementar o saldo total do usuário.
    valor positivo = entrada, negativo = saída.
    """
    db = obter_db()
    db.usuarios.update_one(
        {"_id": usuario_id},
        {"$inc": {"saldo_total": valor}}
    )
    sinal = "+" if valor >= 0 else ""
    print(f"  ✔ Saldo do usuário atualizado ({sinal}R${valor:.2f}) via $inc")


def adicionar_meta_mensal(usuario_id: ObjectId, categoria: str, valor_limite: float, mes: int, ano: int):
    """
    Usa $push para adicionar uma meta mensal dentro do array embutido no usuário.
    Exemplo: limite de R$500 em Alimentação para maio/2025.
    """
    db = obter_db()
    meta = {
        "categoria": categoria,
        "valor_limite": valor_limite,
        "mes": mes,
        "ano": ano,
    }
    db.usuarios.update_one(
        {"_id": usuario_id},
        {"$push": {"metas_mensais": meta}}
    )
    print(f"  ✔ Meta adicionada ({categoria} R${valor_limite:.2f} {mes:02d}/{ano}) via $push")


def remover_meta_mensal(usuario_id: ObjectId, categoria: str, mes: int, ano: int):
    """
    Usa $pull para remover uma meta específica do array embutido.
    """
    db = obter_db()
    db.usuarios.update_one(
        {"_id": usuario_id},
        {"$pull": {"metas_mensais": {"categoria": categoria, "mes": mes, "ano": ano}}}
    )
    print(f"  ✔ Meta removida ({categoria} {mes:02d}/{ano}) via $pull")


def atualizar_email_usuario(usuario_id: ObjectId, novo_email: str):
    db = obter_db()
    db.usuarios.update_one({"_id": usuario_id}, {"$set": {"email": novo_email}})
    print(f"  ✔ Email atualizado para '{novo_email}'")


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def deletar_usuario(usuario_id: ObjectId) -> int:
    db = obter_db()
    resultado = db.usuarios.delete_one({"_id": usuario_id})
    print(f"  ✔ Usuário deletado | documentos removidos={resultado.deleted_count}")
    return resultado.deleted_count
