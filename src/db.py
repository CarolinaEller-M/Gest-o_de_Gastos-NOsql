import os
from pymongo import MongoClient

URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "financas_pessoais"

_client = None
_db = None


def conectar():
    global _client, _db
    if _db is not None:
        return _db
    _client = MongoClient(URI)
    _db = _client[DB_NAME]
    print(f'✅ Conectado ao MongoDB — banco: "{DB_NAME}"')
    return _db


def desconectar():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("🔌 Conexão encerrada.")


def get_db():
    if _db is None:
        raise RuntimeError("Banco não conectado. Chame conectar() primeiro.")
    return _db
