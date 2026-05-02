"""
categorias.py — CRUD da coleção 'categorias'
Coleção independente para padronizar categorias do sistema.
"""

from bson import ObjectId
from conexao import obter_db


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────

def inserir_categoria(nome: str, icone: str = "📦", cor: str = "#888888") -> ObjectId:
    db = obter_db()
    # Evita duplicatas por nome
    existente = db.categorias.find_one({"nome": nome})
    if existente:
        return existente["_id"]

    doc = {"nome": nome, "icone": icone, "cor": cor}
    resultado = db.categorias.insert_one(doc)
    print(f"  ✔ Categoria inserida '{nome}' {icone}")
    return resultado.inserted_id


def inserir_categorias_padrao():
    """Insere as categorias padrão do sistema."""
    categorias = [
        ("Alimentação",   "🍔", "#FF6B6B"),
        ("Transporte",    "🚗", "#4ECDC4"),
        ("Lazer",         "🎉", "#FFE66D"),
        ("Saúde",         "💊", "#A8E6CF"),
        ("Educação",      "📚", "#88D8FF"),
        ("Moradia",       "🏠", "#C9B8FF"),
        ("Salário",       "💼", "#95E17D"),
        ("Investimentos", "📈", "#FFB347"),
        ("Outros",        "💰", "#D3D3D3"),
    ]
    for nome, icone, cor in categorias:
        inserir_categoria(nome, icone, cor)


# ──────────────────────────────────────────────
# READ
# ──────────────────────────────────────────────

def buscar_todas_categorias() -> list:
    db = obter_db()
    return list(db.categorias.find())


def buscar_categoria_por_nome(nome: str) -> dict | None:
    db = obter_db()
    return db.categorias.find_one({"nome": nome})


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

def atualizar_icone_categoria(nome: str, novo_icone: str):
    db = obter_db()
    db.categorias.update_one({"nome": nome}, {"$set": {"icone": novo_icone}})
    print(f"  ✔ Ícone de '{nome}' atualizado para '{novo_icone}'")


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def deletar_categoria(nome: str) -> int:
    db = obter_db()
    resultado = db.categorias.delete_one({"nome": nome})
    print(f"  ✔ Categoria '{nome}' deletada")
    return resultado.deleted_count
