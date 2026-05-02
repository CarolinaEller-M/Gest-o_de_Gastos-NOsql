"""
transacoes.py — CRUD da coleção 'transacoes'
A categoria fica embutida (documento aninhado) dentro de cada transação.
Referencia usuario_id e conta_id por ObjectId.
"""

from datetime import datetime
from bson import ObjectId
from conexao import obter_db
from contas import atualizar_saldo_conta
from usuarios import atualizar_saldo_usuario


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────

def inserir_transacao(
    usuario_id: ObjectId,
    conta_id: ObjectId,
    valor: float,
    tipo: str,          # 'entrada' ou 'saída'
    descricao: str,
    categoria_nome: str,
    categoria_icone: str = "💰",
    data: datetime = None,
) -> ObjectId:
    """
    Registra uma transação.
    - categoria é embutida (doc aninhado): sem necessidade de busca extra ao listar.
    - Atualiza automaticamente o saldo da conta via $inc.
    """
    db = obter_db()
    data = data or datetime.utcnow()

    doc = {
        "usuario_id": usuario_id,   # referência lógica
        "conta_id": conta_id,        # referência lógica
        "valor": valor,
        "tipo": tipo,
        "descricao": descricao,
        "data": data,
        "categoria": {               # documento aninhado — evita JOIN só para listar
            "nome": categoria_nome,
            "icone": categoria_icone,
        },
    }
    resultado = db.transacoes.insert_one(doc)

    # Atualiza saldo: entrada = +valor, saída = -valor
    incremento = valor if tipo == "entrada" else -valor
    atualizar_saldo_conta(conta_id, incremento)
    atualizar_saldo_usuario(usuario_id, incremento)

    print(f"  ✔ Transação registrada '{descricao}' R${valor:.2f} ({tipo}) | id={resultado.inserted_id}")
    return resultado.inserted_id


# ──────────────────────────────────────────────
# READ
# ──────────────────────────────────────────────

def buscar_transacao_por_id(transacao_id: ObjectId) -> dict | None:
    db = obter_db()
    return db.transacoes.find_one({"_id": transacao_id})


def buscar_transacoes_por_usuario(usuario_id: ObjectId) -> list:
    db = obter_db()
    return list(db.transacoes.find({"usuario_id": usuario_id}).sort("data", -1))


def buscar_transacoes_por_mes(usuario_id: ObjectId, mes: int, ano: int) -> list:
    """Filtra transações de um mês/ano específico para o usuário."""
    db = obter_db()
    inicio = datetime(ano, mes, 1)
    # último dia do mês
    if mes == 12:
        fim = datetime(ano + 1, 1, 1)
    else:
        fim = datetime(ano, mes + 1, 1)

    return list(
        db.transacoes.find({
            "usuario_id": usuario_id,
            "data": {"$gte": inicio, "$lt": fim},
        }).sort("data", -1)
    )


def buscar_transacoes_por_categoria(usuario_id: ObjectId, categoria: str) -> list:
    db = obter_db()
    return list(
        db.transacoes.find({
            "usuario_id": usuario_id,
            "categoria.nome": categoria,
        }).sort("data", -1)
    )


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

def atualizar_descricao_transacao(transacao_id: ObjectId, nova_descricao: str):
    db = obter_db()
    db.transacoes.update_one(
        {"_id": transacao_id},
        {"$set": {"descricao": nova_descricao}}
    )
    print(f"  ✔ Descrição atualizada para '{nova_descricao}'")


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def deletar_transacao(transacao_id: ObjectId) -> int:
    """
    Remove a transação. Não reverte o saldo automaticamente
    (decisão de negócio: registre estorno como nova transação).
    """
    db = obter_db()
    resultado = db.transacoes.delete_one({"_id": transacao_id})
    print(f"  ✔ Transação deletada | documentos removidos={resultado.deleted_count}")
    return resultado.deleted_count


def deletar_transacoes_por_usuario(usuario_id: ObjectId) -> int:
    db = obter_db()
    resultado = db.transacoes.delete_many({"usuario_id": usuario_id})
    return resultado.deleted_count
