from bson import ObjectId
from src.db import get_db


def inserir_categoria(nome: str, icone: str, tipo: str):
    # tipo: "entrada" | "saida" | "ambos"
    db = get_db()
    result = db["categorias"].insert_one({"nome": nome, "icone": icone, "tipo": tipo})
    print(f"🏷️  Categoria inserida: {icone} {nome}")
    return result.inserted_id


def listar_categorias():
    return list(get_db()["categorias"].find().sort("nome", 1))


def buscar_categoria_por_nome(nome: str):
    return get_db()["categorias"].find_one({"nome": nome})


def deletar_categoria(categoria_id):
    return get_db()["categorias"].delete_one({"_id": ObjectId(str(categoria_id))})
