"""
main.py — Demonstração completa do sistema financeiro
Rode com: python main.py
"""

from datetime import datetime
from src.db import conectar, desconectar
from src.usuarios import (
    inserir_usuario, buscar_usuario_por_email,
    adicionar_meta, remover_meta,
)
from src.contas import inserir_conta, buscar_contas_por_usuario
from src.transacoes import (
    inserir_transacao, buscar_transacoes_por_mes, deletar_transacao,
)
from src.categorias import inserir_categoria, listar_categorias
from src.relatorios import extrato_detalhado_por_mes, dashboard_mensal

ANO = 2025
MES = 5  # maio


# ─── Utilitários de exibição ──────────────────────────────────────────────
def titulo(texto: str):
    print("\n" + "═" * 60)
    print(f"  {texto}")
    print("═" * 60)


def moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_data(data) -> str:
    return data.strftime("%d/%m/%Y") if isinstance(data, datetime) else str(data)


# ─── MAIN ─────────────────────────────────────────────────────────────────
def main():
    conectar()

    # ─────────────────────────────────────────────────────────────────────
    titulo("ETAPA 1 — Inserindo Categorias")
    # ─────────────────────────────────────────────────────────────────────

    cats_existentes = listar_categorias()
    categorias = {}

    if not cats_existentes:
        dados_cats = [
            ("Alimentação", "🍔", "saida"),
            ("Transporte",  "🚗", "saida"),
            ("Lazer",       "🎮", "saida"),
            ("Saúde",       "💊", "saida"),
            ("Moradia",     "🏠", "saida"),
            ("Salário",     "💵", "entrada"),
            ("Freelance",   "💻", "entrada"),
        ]
        for nome, icone, tipo in dados_cats:
            inserir_categoria(nome, icone, tipo)
        print(f"✅ {len(dados_cats)} categorias criadas.")
    else:
        print(f"ℹ️  {len(cats_existentes)} categorias já existem. Pulando inserção.")

    for c in listar_categorias():
        categorias[c["nome"]] = c

    # ─────────────────────────────────────────────────────────────────────
    titulo("ETAPA 2 — Inserindo Usuário")
    # ─────────────────────────────────────────────────────────────────────

    usuario = buscar_usuario_por_email("maria@email.com")

    if not usuario:
        inserir_usuario(
            nome="Maria Silva",
            email="maria@email.com",
            saldo_total=0,
            metas=[
                {"categoria": "Alimentação", "valor_limite": 800},
                {"categoria": "Lazer",       "valor_limite": 300},
            ],
        )
        usuario = buscar_usuario_por_email("maria@email.com")
        print(f"✅ Usuário criado: {usuario['nome']}")
    else:
        print(f"ℹ️  Usuário já existe: {usuario['nome']}")

    usuario_id = str(usuario["_id"])

    # ─────────────────────────────────────────────────────────────────────
    titulo("ETAPA 3 — $push e $pull (metas do usuário)")
    # ─────────────────────────────────────────────────────────────────────

    print("Adicionando meta de Transporte com $push...")
    adicionar_meta(usuario_id, {"categoria": "Transporte", "valor_limite": 400})

    print("Removendo meta de Lazer com $pull...")
    remover_meta(usuario_id, "Lazer")

    # ─────────────────────────────────────────────────────────────────────
    titulo("ETAPA 4 — Inserindo Contas Bancárias")
    # ─────────────────────────────────────────────────────────────────────

    contas = buscar_contas_por_usuario(usuario_id)

    if not contas:
        conta_corrente_id = str(inserir_conta(
            usuario_id, "Conta Corrente Nubank", "corrente", saldo=0
        ))
        poupanca_id = str(inserir_conta(
            usuario_id, "Poupança Caixa", "poupanca", saldo=0
        ))
        print("✅ 2 contas criadas.")
    else:
        conta_corrente_id = str(contas[0]["_id"])
        poupanca_id = str(contas[1]["_id"]) if len(contas) > 1 else conta_corrente_id
        print(f"ℹ️  {len(contas)} contas já existem.")

    # ─────────────────────────────────────────────────────────────────────
    titulo("ETAPA 5 — Inserindo Transações (com $inc automático no saldo)")
    # ─────────────────────────────────────────────────────────────────────

    txs = buscar_transacoes_por_mes(usuario_id, ANO, MES)

    if not txs:
        transacoes_para_inserir = [
            (conta_corrente_id, 4500.00,  "entrada", "Salário maio",        datetime(ANO, MES, 5),  "Salário"),
            (conta_corrente_id, 150.90,   "saida",   "Supermercado Extra",   datetime(ANO, MES, 8),  "Alimentação"),
            (conta_corrente_id, 89.90,    "saida",   "Uber - semana 1",      datetime(ANO, MES, 10), "Transporte"),
            (poupanca_id,       1200.00,  "entrada", "Freelance app mobile", datetime(ANO, MES, 12), "Freelance"),
            (conta_corrente_id, 1500.00,  "saida",   "Aluguel maio",         datetime(ANO, MES, 15), "Moradia"),
            (conta_corrente_id, 320.00,   "saida",   "Consulta + exames",    datetime(ANO, MES, 18), "Saúde"),
            (conta_corrente_id, 85.00,    "saida",   "Cinema + jantar",      datetime(ANO, MES, 22), "Lazer"),
        ]
        for conta_id, valor, tipo, descricao, data, cat_nome in transacoes_para_inserir:
            cat = categorias.get(cat_nome, {"nome": cat_nome, "icone": "💰"})
            inserir_transacao(usuario_id, conta_id, valor, tipo, descricao, cat, data)
        print(f"✅ {len(transacoes_para_inserir)} transações inseridas.")
    else:
        print(f"ℹ️  {len(txs)} transações já existem.")

    # ─────────────────────────────────────────────────────────────────────
    titulo("ETAPA 6 — Deletando uma Transação (reverte $inc no saldo)")
    # ─────────────────────────────────────────────────────────────────────

    txs_mes = buscar_transacoes_por_mes(usuario_id, ANO, MES)
    tx_para_deletar = next((t for t in txs_mes if t["descricao"] == "Cinema + jantar"), None)

    if tx_para_deletar:
        print(f'Deletando: "{tx_para_deletar["descricao"]}" ({moeda(tx_para_deletar["valor"])})')
        deletar_transacao(str(tx_para_deletar["_id"]))
        print("✅ Transação deletada e saldo revertido.")
    else:
        print("ℹ️  Transação de teste já foi deletada anteriormente.")

    # ─────────────────────────────────────────────────────────────────────
    titulo("RELATÓRIO 1 — Extrato Detalhado ($lookup + $unwind)")
    # ─────────────────────────────────────────────────────────────────────

    extrato = extrato_detalhado_por_mes(usuario_id, ANO, MES)

    if not extrato:
        print("Nenhuma transação encontrada para este período.")
    else:
        print(f"\n📋 Extrato de {str(MES).zfill(2)}/{ANO}\n")
        print(
            f"{'Data':<12}{'Descrição':<28}{'Categoria':<16}"
            f"{'Conta':<24}{'Tipo':<10}{'Valor'}"
        )
        print("─" * 100)
        for tx in extrato:
            cat = tx.get("categoria", {})
            icone = cat.get("icone", "")
            nome_cat = cat.get("nome", "")
            sinal = "+" if tx["tipo"] == "entrada" else "-"
            print(
                f"{fmt_data(tx['data']):<12}"
                f"{tx['descricao'][:26]:<28}"
                f"{(icone + ' ' + nome_cat)[:14]:<16}"
                f"{str(tx.get('conta_nome', '—'))[:22]:<24}"
                f"{tx['tipo']:<10}"
                f"{sinal}{moeda(tx['valor'])}"
            )

    # ─────────────────────────────────────────────────────────────────────
    titulo("RELATÓRIO 2 — Dashboard Financeiro ($facet)")
    # ─────────────────────────────────────────────────────────────────────

    dash = dashboard_mensal(usuario_id, ANO, MES)

    total_gasto    = dash.get("total_gasto",    [{}])[0].get("total", 0)
    total_recebido = dash.get("total_recebido", [{}])[0].get("total", 0)
    saldo_mes      = total_recebido - total_gasto
    maior_tx       = dash.get("maior_transacao", [None])[0]

    print(f"\n📊 Dashboard — {str(MES).zfill(2)}/{ANO}")
    print(f"\n  💚 Total recebido : {moeda(total_recebido)}")
    print(f"  🔴 Total gasto    : {moeda(total_gasto)}")
    print(f"  📈 Saldo do mês   : {moeda(saldo_mes)}")

    if maior_tx:
        print(f'\n  🏆 Maior transação: "{maior_tx["descricao"]}" — {moeda(maior_tx["valor"])}')

    cats_rank = dash.get("gasto_por_categoria", [])
    if cats_rank:
        print("\n  📂 Ranking de gastos por categoria:")
        for i, cat in enumerate(cats_rank, 1):
            barras = int((cat["total"] / total_gasto) * 20) if total_gasto else 0
            barra = "█" * barras
            print(
                f"    {i}. {cat['icone']} {cat['categoria']:<14} "
                f"{barra:<20} {moeda(cat['total'])} ({cat['quantidade']}x)"
            )

    print("\n  📦 Quantidade de transações:")
    for r in dash.get("resumo_quantidade", []):
        print(f"     • {r['_id']}: {r['quantidade']} transação(ões)")

    # ─────────────────────────────────────────────────────────────────────
    titulo("FIM DA DEMONSTRAÇÃO")
    # ─────────────────────────────────────────────────────────────────────

    desconectar()


if __name__ == "__main__":
    main()
