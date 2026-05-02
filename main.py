"""
main.py — Arquivo principal / demonstração do sistema financeiro
Conecta ao MongoDB, executa CRUD, operadores avançados e relatórios.
"""

import sys
from datetime import datetime
from bson import ObjectId

from conexao import conectar, fechar_conexao
from categorias import inserir_categorias_padrao, buscar_todas_categorias
from usuarios import (
    inserir_usuario, buscar_usuario_por_id, buscar_todos_usuarios,
    adicionar_meta_mensal, remover_meta_mensal, atualizar_email_usuario,
    deletar_usuario,
)
from contas import (
    inserir_conta, buscar_contas_por_usuario, buscar_conta_por_id,
    atualizar_saldo_conta, deletar_conta,
)
from transacoes import (
    inserir_transacao, buscar_transacoes_por_usuario,
    buscar_transacoes_por_mes, deletar_transacao,
    atualizar_descricao_transacao,
)
from relatorios import (
    relatorio_extrato_detalhado, imprimir_extrato,
    relatorio_dashboard, imprimir_dashboard,
)

# ─────────────────────────────────────────────────────────────
#  Helpers de exibição
# ─────────────────────────────────────────────────────────────

SEP = "─" * 60


def secao(titulo: str):
    print(f"\n{'═'*60}")
    print(f"  🔷  {titulo}")
    print(f"{'═'*60}")


def pausa():
    input("\n  [ Pressione ENTER para continuar... ]\n")


# ─────────────────────────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────

def menu_principal():
    opcoes = {
        "1": ("👤 CRUD de Usuários",       menu_usuarios),
        "2": ("🏦 CRUD de Contas",          menu_contas),
        "3": ("💳 CRUD de Transações",      menu_transacoes),
        "4": ("📄 Relatório: Extrato ($lookup + $unwind)", menu_extrato),
        "5": ("📊 Relatório: Dashboard ($facet)",          menu_dashboard),
        "6": ("🚀 Demonstração Completa (automática)",     demo_automatica),
        "0": ("❌ Sair",                    None),
    }

    while True:
        print("\n" + "═"*60)
        print("  💰  SISTEMA FINANCEIRO PESSOAL — MongoDB + Python")
        print("═"*60)
        for k, (label, _) in opcoes.items():
            print(f"  [{k}] {label}")
        print(SEP)
        escolha = input("  Escolha: ").strip()

        if escolha == "0":
            fechar_conexao()
            print("  👋 Até logo!")
            sys.exit(0)
        elif escolha in opcoes:
            _, fn = opcoes[escolha]
            fn()
        else:
            print("  ⚠️  Opção inválida.")


# ─────────────────────────────────────────────────────────────
#  SUB-MENUS
# ─────────────────────────────────────────────────────────────

def _selecionar_usuario() -> ObjectId | None:
    usuarios = buscar_todos_usuarios()
    if not usuarios:
        print("  ⚠️  Nenhum usuário cadastrado.")
        return None
    print("\n  Usuários disponíveis:")
    for u in usuarios:
        print(f"    [{u['_id']}]  {u['nome']}  — Saldo: R${u['saldo_total']:.2f}")
    uid_str = input("  ID do usuário: ").strip()
    try:
        return ObjectId(uid_str)
    except Exception:
        print("  ⚠️  ID inválido.")
        return None


def _selecionar_conta(usuario_id: ObjectId) -> ObjectId | None:
    contas = buscar_contas_por_usuario(usuario_id)
    if not contas:
        print("  ⚠️  Nenhuma conta cadastrada para este usuário.")
        return None
    print("\n  Contas disponíveis:")
    for c in contas:
        print(f"    [{c['_id']}]  {c['nome']} ({c['tipo']})  — Saldo: R${c['saldo']:.2f}")
    cid_str = input("  ID da conta: ").strip()
    try:
        return ObjectId(cid_str)
    except Exception:
        print("  ⚠️  ID inválido.")
        return None


# ── USUÁRIOS ──────────────────────────────────────────────────

def menu_usuarios():
    while True:
        secao("CRUD DE USUÁRIOS")
        print("  [1] Inserir usuário")
        print("  [2] Listar todos os usuários")
        print("  [3] Ver metas mensais")
        print("  [4] Adicionar meta mensal  ($push)")
        print("  [5] Remover meta mensal    ($pull)")
        print("  [6] Atualizar email")
        print("  [7] Deletar usuário")
        print("  [0] Voltar")
        op = input("  Escolha: ").strip()

        if op == "0":
            break
        elif op == "1":
            nome  = input("  Nome: ")
            email = input("  Email: ")
            saldo = float(input("  Saldo inicial (R$): ") or "0")
            inserir_usuario(nome, email, saldo)

        elif op == "2":
            usuarios = buscar_todos_usuarios()
            print(f"\n  Total: {len(usuarios)} usuário(s)")
            for u in usuarios:
                print(f"    • {u['nome']} | {u['email']} | Saldo R${u['saldo_total']:.2f}")
                if u.get("metas_mensais"):
                    for m in u["metas_mensais"]:
                        print(f"        ↳ Meta {m['categoria']}: R${m['valor_limite']:.2f} {m['mes']:02d}/{m['ano']}")

        elif op == "3":
            uid = _selecionar_usuario()
            if uid:
                u = buscar_usuario_por_id(uid)
                print(f"\n  Metas de {u['nome']}:")
                for m in u.get("metas_mensais", []):
                    print(f"    • {m['categoria']}: R${m['valor_limite']:.2f}  {m['mes']:02d}/{m['ano']}")

        elif op == "4":
            uid = _selecionar_usuario()
            if uid:
                cat   = input("  Categoria: ")
                valor = float(input("  Valor limite (R$): "))
                mes   = int(input("  Mês (1-12): "))
                ano   = int(input("  Ano: "))
                adicionar_meta_mensal(uid, cat, valor, mes, ano)

        elif op == "5":
            uid = _selecionar_usuario()
            if uid:
                cat = input("  Categoria da meta a remover: ")
                mes = int(input("  Mês: "))
                ano = int(input("  Ano: "))
                remover_meta_mensal(uid, cat, mes, ano)

        elif op == "6":
            uid = _selecionar_usuario()
            if uid:
                novo = input("  Novo email: ")
                atualizar_email_usuario(uid, novo)

        elif op == "7":
            uid = _selecionar_usuario()
            if uid:
                conf = input("  Confirma exclusão? (s/N): ")
                if conf.lower() == "s":
                    deletar_usuario(uid)


# ── CONTAS ────────────────────────────────────────────────────

def menu_contas():
    while True:
        secao("CRUD DE CONTAS")
        print("  [1] Inserir conta")
        print("  [2] Listar contas de um usuário")
        print("  [3] Ajustar saldo manualmente  ($inc)")
        print("  [4] Deletar conta")
        print("  [0] Voltar")
        op = input("  Escolha: ").strip()

        if op == "0":
            break
        elif op == "1":
            uid = _selecionar_usuario()
            if uid:
                nome  = input("  Nome da conta: ")
                tipo  = input("  Tipo (corrente/poupança/cartão): ")
                saldo = float(input("  Saldo inicial (R$): ") or "0")
                inserir_conta(uid, nome, tipo, saldo)

        elif op == "2":
            uid = _selecionar_usuario()
            if uid:
                contas = buscar_contas_por_usuario(uid)
                for c in contas:
                    print(f"    • {c['nome']} ({c['tipo']})  R${c['saldo']:.2f}  id={c['_id']}")

        elif op == "3":
            uid = _selecionar_usuario()
            if uid:
                cid = _selecionar_conta(uid)
                if cid:
                    valor = float(input("  Valor (+entrada / -saída): "))
                    atualizar_saldo_conta(cid, valor)

        elif op == "4":
            uid = _selecionar_usuario()
            if uid:
                cid = _selecionar_conta(uid)
                if cid:
                    conf = input("  Confirma exclusão? (s/N): ")
                    if conf.lower() == "s":
                        deletar_conta(cid)


# ── TRANSAÇÕES ────────────────────────────────────────────────

def menu_transacoes():
    while True:
        secao("CRUD DE TRANSAÇÕES")
        print("  [1] Registrar transação")
        print("  [2] Listar transações de um usuário")
        print("  [3] Listar transações por mês")
        print("  [4] Atualizar descrição")
        print("  [5] Deletar transação")
        print("  [0] Voltar")
        op = input("  Escolha: ").strip()

        if op == "0":
            break
        elif op == "1":
            uid = _selecionar_usuario()
            if uid:
                cid = _selecionar_conta(uid)
                if cid:
                    valor     = float(input("  Valor (R$): "))
                    tipo      = input("  Tipo (entrada/saída): ").lower()
                    descricao = input("  Descrição: ")
                    categoria = input("  Categoria (ex: Alimentação): ")
                    icone     = input("  Ícone (ex: 🍔) [padrão 💰]: ") or "💰"
                    inserir_transacao(uid, cid, valor, tipo, descricao, categoria, icone)

        elif op == "2":
            uid = _selecionar_usuario()
            if uid:
                txs = buscar_transacoes_por_usuario(uid)
                print(f"\n  {len(txs)} transação(ões):")
                for t in txs:
                    sinal = "+" if t["tipo"] == "entrada" else "-"
                    print(f"    {t['categoria']['icone']} {t['data'].strftime('%d/%m/%Y')}  "
                          f"{t['descricao']:<30} {sinal}R${t['valor']:.2f}")

        elif op == "3":
            uid = _selecionar_usuario()
            if uid:
                mes = int(input("  Mês (1-12): "))
                ano = int(input("  Ano: "))
                txs = buscar_transacoes_por_mes(uid, mes, ano)
                print(f"\n  {len(txs)} transação(ões) em {mes:02d}/{ano}:")
                for t in txs:
                    sinal = "+" if t["tipo"] == "entrada" else "-"
                    print(f"    {t['categoria']['icone']} {t['data'].strftime('%d/%m/%Y')}  "
                          f"{t['descricao']:<30} {sinal}R${t['valor']:.2f}")

        elif op == "4":
            uid = _selecionar_usuario()
            if uid:
                txs = buscar_transacoes_por_usuario(uid)
                for t in txs:
                    print(f"  [{t['_id']}]  {t['descricao']}")
                tid_str = input("  ID da transação: ").strip()
                try:
                    tid = ObjectId(tid_str)
                    nova = input("  Nova descrição: ")
                    atualizar_descricao_transacao(tid, nova)
                except Exception:
                    print("  ⚠️  ID inválido.")

        elif op == "5":
            uid = _selecionar_usuario()
            if uid:
                txs = buscar_transacoes_por_usuario(uid)
                for t in txs:
                    print(f"  [{t['_id']}]  {t['descricao']}  R${t['valor']:.2f}")
                tid_str = input("  ID da transação a deletar: ").strip()
                try:
                    tid = ObjectId(tid_str)
                    conf = input("  Confirma exclusão? (s/N): ")
                    if conf.lower() == "s":
                        deletar_transacao(tid)
                except Exception:
                    print("  ⚠️  ID inválido.")


# ── RELATÓRIOS ────────────────────────────────────────────────

def menu_extrato():
    secao("RELATÓRIO 1 — EXTRATO DETALHADO ($lookup + $unwind)")
    uid = _selecionar_usuario()
    if not uid:
        return
    filtrar = input("  Filtrar por mês? (s/N): ").lower()
    mes = ano = None
    if filtrar == "s":
        mes = int(input("  Mês (1-12): "))
        ano = int(input("  Ano: "))
    registros = relatorio_extrato_detalhado(uid, mes, ano)
    imprimir_extrato(registros)
    pausa()


def menu_dashboard():
    secao("RELATÓRIO 2 — DASHBOARD FINANCEIRO ($facet)")
    uid = _selecionar_usuario()
    if not uid:
        return
    mes = int(input("  Mês (1-12): "))
    ano = int(input("  Ano: "))
    dados = relatorio_dashboard(uid, mes, ano)
    imprimir_dashboard(dados, mes, ano)
    pausa()


# ─────────────────────────────────────────────────────────────
#  DEMONSTRAÇÃO AUTOMÁTICA (sem interação do usuário)
# ─────────────────────────────────────────────────────────────

def demo_automatica():
    db = conectar.__module__  # só para confirmar que estamos conectados
    secao("DEMONSTRAÇÃO AUTOMÁTICA — SISTEMA COMPLETO")

    print("\n📦 1. Inserindo categorias padrão...")
    inserir_categorias_padrao()

    print(f"\n👤 2. Criando usuário...")
    uid = inserir_usuario("Maria Demo", "maria@demo.com", 0)

    print(f"\n🏦 3. Criando contas bancárias...")
    cid_corrente = inserir_conta(uid, "Nubank Corrente", "corrente", 0)
    cid_poupanca = inserir_conta(uid, "Caixa Poupança",  "poupança",  0)

    print(f"\n💳 4. Registrando transações (usam $inc internamente)...")
    inserir_transacao(uid, cid_corrente, 6000.00, "entrada", "Salário",                "Salário",     "💼", datetime(2025, 5, 1))
    t1 = inserir_transacao(uid, cid_corrente,  450.00, "saída",  "Supermercado",          "Alimentação", "🍔", datetime(2025, 5, 5))
    inserir_transacao(uid, cid_corrente,  180.00, "saída",  "Uber / 99",             "Transporte",  "🚗", datetime(2025, 5, 8))
    inserir_transacao(uid, cid_corrente, 1100.00, "saída",  "Aluguel",               "Moradia",     "🏠", datetime(2025, 5, 10))
    inserir_transacao(uid, cid_corrente,   90.00, "saída",  "Streaming + internet",  "Lazer",       "🎉", datetime(2025, 5, 12))
    inserir_transacao(uid, cid_poupanca,  500.00, "entrada", "Rendimento poupança",  "Investimentos","📈", datetime(2025, 5, 15))
    inserir_transacao(uid, cid_corrente,  220.00, "saída",  "Consulta médica",       "Saúde",       "💊", datetime(2025, 5, 18))

    print(f"\n📌 5. Adicionando metas mensais via $push...")
    adicionar_meta_mensal(uid, "Alimentação", 400.00, 5, 2025)
    adicionar_meta_mensal(uid, "Lazer",       100.00, 5, 2025)
    adicionar_meta_mensal(uid, "Transporte",  200.00, 5, 2025)

    u = buscar_usuario_por_id(uid)
    print(f"\n  Metas cadastradas para {u['nome']}:")
    for m in u.get("metas_mensais", []):
        print(f"    • {m['categoria']}: R${m['valor_limite']:.2f}  {m['mes']:02d}/{m['ano']}")

    print(f"\n🗑️  6. Removendo meta de 'Lazer' via $pull...")
    remover_meta_mensal(uid, "Lazer", 5, 2025)
    u = buscar_usuario_por_id(uid)
    print(f"  Metas restantes: {[m['categoria'] for m in u.get('metas_mensais', [])]}")

    print(f"\n✏️  7. Atualizando descrição de uma transação...")
    atualizar_descricao_transacao(t1, "Supermercado Extra (atualizado)")

    print(f"\n🗑️  8. Deletando a transação de R$450 (Supermercado)...")
    deletar_transacao(t1)

    print(f"\n📄 9. RELATÓRIO 1 — Extrato detalhado ($lookup + $unwind):")
    registros = relatorio_extrato_detalhado(uid, mes=5, ano=2025)
    imprimir_extrato(registros)

    print(f"\n📊 10. RELATÓRIO 2 — Dashboard ($facet):")
    dados = relatorio_dashboard(uid, mes=5, ano=2025)
    imprimir_dashboard(dados, mes=5, ano=2025)

    print(f"\n✅ Demonstração concluída!")
    print(f"   Usuário demo criado com id={uid}")
    pausa()


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    conectar()
    menu_principal()
