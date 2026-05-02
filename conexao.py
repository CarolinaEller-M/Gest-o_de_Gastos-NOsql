"""
conexao.py — Responsável pela conexão com o MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys

_client = None
_db = None


def conectar(uri: str = "mongodb://localhost:27017", nome_banco: str = "financeiro_app"):
    """Estabelece conexão com o MongoDB e retorna o banco de dados."""
    global _client, _db

    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Testa a conexão
        _client.admin.command("ping")
        _db = _client[nome_banco]
        print(f"✅ Conectado ao MongoDB | Banco: '{nome_banco}'")
        return _db
    except ConnectionFailure as e:
        print(f"❌ Falha ao conectar ao MongoDB: {e}")
        sys.exit(1)


def obter_db():
    """Retorna a instância do banco de dados já conectado."""
    if _db is None:
        raise RuntimeError("Banco de dados não conectado. Chame conectar() primeiro.")
    return _db


def fechar_conexao():
    """Fecha a conexão com o MongoDB."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("🔌 Conexão com MongoDB encerrada.")
