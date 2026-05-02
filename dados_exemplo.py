"""
dados_exemplo.py — Popula o banco com dados de exemplo para demonstração.
Execute este arquivo antes do main.py se quiser dados pré-carregados.
"""

from datetime import datetime, timedelta
import random
from conexao import conectar, fechar_conexao
from categorias import inserir_categorias_padrao
from usuarios import inserir_usuario
from contas import inserir_conta
from transacoes import inserir_transacao


def popular_banco():
    db = conectar()

    print("\n🗑️  Limpando coleções anteriores...")
    db.usuarios.drop()
    db.contas.drop()
    db.transacoes.drop()
    db.categorias.drop()

    print("\n📦 Inserindo categorias padrão...")
    inserir_categorias_padrao()

    print("\n👤 Inserindo usuários...")
    uid1 = inserir_usuario("Ana Silva",    "ana@email.com",    saldo_total=0)
    uid2 = inserir_usuario("Bruno Costa",  "bruno@email.com",  saldo_total=0)

    print("\n🏦 Inserindo contas bancárias...")
    cid_ana_corrente  = inserir_conta(uid1, "Nubank Corrente", "corrente",  saldo=0)
    cid_ana_poupanca  = inserir_conta(uid1, "Itaú Poupança",   "poupança",  saldo=0)
    cid_bruno_corrente = inserir_conta(uid2, "Bradesco Corrente","corrente", saldo=0)

    print("\n💳 Inserindo transações (maio 2025)...")

    hoje = datetime(2025, 5, 15)

    # Entradas — Ana
    inserir_transacao(uid1, cid_ana_corrente, 5500.00, "entrada", "Salário maio",         "Salário",       "💼", hoje - timedelta(days=14))
    inserir_transacao(uid1, cid_ana_poupanca,  800.00, "entrada", "Renda extra freela",   "Outros",        "💰", hoje - timedelta(days=10))

    # Saídas — Ana
    inserir_transacao(uid1, cid_ana_corrente,  320.00, "saída",  "Supermercado Pão de Açúcar", "Alimentação", "🍔", hoje - timedelta(days=13))
    inserir_transacao(uid1, cid_ana_corrente,   85.50, "saída",  "iFood - Jantar",              "Alimentação", "🍔", hoje - timedelta(days=11))
    inserir_transacao(uid1, cid_ana_corrente,  150.00, "saída",  "Uber mensal",                 "Transporte",  "🚗", hoje - timedelta(days=9))
    inserir_transacao(uid1, cid_ana_corrente,   45.00, "saída",  "Netflix + Spotify",           "Lazer",       "🎉", hoje - timedelta(days=8))
    inserir_transacao(uid1, cid_ana_corrente,  200.00, "saída",  "Academia SmartFit",           "Saúde",       "💊", hoje - timedelta(days=7))
    inserir_transacao(uid1, cid_ana_corrente,  120.00, "saída",  "Curso Python Udemy",          "Educação",    "📚", hoje - timedelta(days=5))
    inserir_transacao(uid1, cid_ana_corrente, 1200.00, "saída",  "Aluguel",                     "Moradia",     "🏠", hoje - timedelta(days=4))
    inserir_transacao(uid1, cid_ana_corrente,   75.00, "saída",  "Farmácia",                    "Saúde",       "💊", hoje - timedelta(days=2))
    inserir_transacao(uid1, cid_ana_corrente,   60.00, "saída",  "Cinema e pipoca",             "Lazer",       "🎉", hoje - timedelta(days=1))

    # Entradas — Bruno
    inserir_transacao(uid2, cid_bruno_corrente, 4200.00, "entrada", "Salário maio",        "Salário",   "💼", hoje - timedelta(days=14))
    inserir_transacao(uid2, cid_bruno_corrente,  500.00, "entrada", "Dividendos ações",    "Investimentos","📈", hoje - timedelta(days=5))

    # Saídas — Bruno
    inserir_transacao(uid2, cid_bruno_corrente,  280.00, "saída", "Mercado",               "Alimentação","🍔", hoje - timedelta(days=12))
    inserir_transacao(uid2, cid_bruno_corrente,  900.00, "saída", "Aluguel",               "Moradia",   "🏠", hoje - timedelta(days=3))
    inserir_transacao(uid2, cid_bruno_corrente,   90.00, "saída", "Gasolina",              "Transporte","🚗", hoje - timedelta(days=6))

    fechar_conexao()
    print("\n✅ Banco populado com sucesso!")
    print("   Agora execute:  python main.py")


if __name__ == "__main__":
    popular_banco()
