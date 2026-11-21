"""
app.py
------
Aplicação Flask que reproduz, como painel web, as três tabelas
originadas dos CSVs (estoque, vendas, logística), lidas de um
banco SQLite (loja.db) via SQLAlchemy + Pandas.

Como usar:
    1. pip install -r requirements.txt
    2. python setup_db.py       (cria/atualiza loja.db a partir de data/*.csv)
    3. python app.py            (sobe o servidor em http://127.0.0.1:5000)
"""

import os
import traceback
from datetime import date, datetime
import pandas as pd
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'loja.db')}"

app = Flask(__name__)
engine = create_engine(DATABASE_URL)


def consultar(sql: str, **params) -> pd.DataFrame:
    return pd.read_sql(text(sql), engine, params=params)


def escalar(sql: str, **params):
    with engine.connect() as conn:
        return conn.execute(text(sql), params).scalar()


def formatar_data(valor) -> str:
    if valor is None or valor == "":
        return ""

    if isinstance(valor, (datetime, date)):
        return valor.strftime("%d/%m/%Y")

    texto = str(valor).strip()
    if not texto:
        return ""

    data_texto = texto.split()[0].split("T")[0]
    partes = data_texto.split("-")
    if len(partes) == 3:
        ano, mes, dia = partes
        return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"

    return texto


STATUS_VENDA_BADGE = {
    "concluida": "ok",
    "pendente":  "warn",
    "cancelada": "bad",
}

STATUS_ENTREGA_BADGE = {
    "entregue":    "ok",
    "em_transito": "warn",
    "cancelada":   "bad",
}

# ── Dashboard ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    try:
        receita_total = escalar(
            "SELECT COALESCE(SUM(valor_total),0) FROM vendas WHERE status='concluida'"
        ) or 0
        pedidos_total     = escalar("SELECT COUNT(*) FROM vendas")
        pedidos_concluida = escalar("SELECT COUNT(*) FROM vendas WHERE status='concluida'")
        pedidos_cancelada = escalar("SELECT COUNT(*) FROM vendas WHERE status='cancelada'")

        valor_estoque = escalar(
            "SELECT COALESCE(SUM(quantidade_estoque*custo_unitario),0) FROM estoque"
        ) or 0
        produtos_criticos = escalar(
            "SELECT COUNT(*) FROM estoque WHERE quantidade_estoque < estoque_minimo"
        )

        entregues   = escalar("SELECT COUNT(*) FROM logistica WHERE status_entrega='entregue'")
        em_transito = escalar("SELECT COUNT(*) FROM logistica WHERE status_entrega='em_transito'")
        atraso_medio = escalar(
            "SELECT AVG(atraso_dias) FROM logistica WHERE atraso_dias IS NOT NULL"
        )
        atraso_medio = round(atraso_medio, 1) if atraso_medio is not None else None

        kpis = [
            {"label": "Receita (concluídas)", "value": f"R$ {receita_total:,.2f}", "accent": "teal"},
            {"label": "Pedidos totais",        "value": pedidos_total,             "accent": ""},
            {"label": "Capital em estoque",     "value": f"R$ {valor_estoque:,.2f}", "accent": ""},
            {"label": "Abaixo do mínimo",       "value": produtos_criticos,         "accent": "amber" if produtos_criticos else ""},
            {"label": "Entregas concluídas",    "value": entregues,                 "accent": "teal"},
            {"label": "Atraso médio (dias)",    "value": atraso_medio if atraso_medio is not None else "—", "accent": "amber" if (atraso_medio or 0) > 0 else ""},
        ]

        top_produtos = consultar("""
            SELECT e.nome, SUM(v.valor_total) AS receita
            FROM vendas v JOIN estoque e ON e.produto_id = v.produto_id
            WHERE v.status = 'concluida'
            GROUP BY e.nome ORDER BY receita DESC LIMIT 5
        """)
        max_receita = top_produtos["receita"].max() if not top_produtos.empty else 1
        barras_produtos = [
            {"label": r["nome"], "valor": f"R$ {r['receita']:,.2f}",
             "pct": round(r["receita"] / max_receita * 100, 1)}
            for _, r in top_produtos.iterrows()
        ]

        mensal = consultar("""
            SELECT 
                substr(data_venda, 1, 7) AS mes,
                SUM(valor_total) AS valor_total
            FROM vendas
            WHERE status='concluida'
            GROUP BY substr(data_venda, 1, 7)
            ORDER BY mes
        """)

        barras_mensal = []
        if not mensal.empty:
            max_mes = mensal["valor_total"].max()
            for _, row in mensal.iterrows():
                try:
                    # Converter "YYYY-MM" para formato legível
                    mes_str = row["mes"]
                    mes_obj = pd.Period(mes_str, freq="M")
                    label_mes = mes_obj.strftime("%b/%Y")
                except:
                    label_mes = row["mes"]

                barras_mensal.append({
                    "label": label_mes,
                    "valor": f"R$ {row['valor_total']:,.2f}",
                    "pct": round(row["valor_total"] / max_mes * 100, 1)
                })

        return render_template(
            "dashboard.html",
            kpis=kpis,
            barras_produtos=barras_produtos,
            barras_mensal=barras_mensal,
            pedidos_concluida=pedidos_concluida,
            pedidos_cancelada=pedidos_cancelada,
        )

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NA ROTA DASHBOARD():")
        print("="*60)
        traceback.print_exc()
        print("="*60 + "\n")
        return f"<h1>Erro no Dashboard</h1><pre>{str(e)}</pre>", 500


# ── Vendas ────────────────────────────────────────────────

@app.route("/vendas")
def vendas():
    status_filtro = request.args.get("status", "todas")

    sql = """
        SELECT v.venda_id, e.nome AS produto, v.cliente, v.data_venda,
               v.quantidade, v.preco_unitario, v.valor_total, v.status
        FROM vendas v
        JOIN estoque e ON e.produto_id = v.produto_id
    """
    params = {}
    if status_filtro != "todas":
        sql += " WHERE v.status = :status"
        params["status"] = status_filtro
    sql += " ORDER BY v.data_venda DESC"

    df = consultar(sql, **params)
    registros = df.to_dict("records")
    for r in registros:
        r["data_venda"] = formatar_data(r["data_venda"])
        r["badge"] = STATUS_VENDA_BADGE.get(r["status"], "neutral")

    return render_template(
        "vendas.html",
        vendas=registros,
        status_filtro=status_filtro,
    )


# ── Estoque ───────────────────────────────────────────────

@app.route("/estoque")
def estoque():
    df = consultar("""
        SELECT produto_id, nome, categoria, quantidade_estoque,
               estoque_minimo, fornecedor, custo_unitario
        FROM estoque ORDER BY categoria, nome
    """)
    df["critico"] = df["quantidade_estoque"] < df["estoque_minimo"]
    df["valor_estoque"] = df["quantidade_estoque"] * df["custo_unitario"]
    produtos = df.to_dict("records")

    df_cat = consultar("""
        SELECT categoria, SUM(quantidade_estoque*custo_unitario) AS valor
        FROM estoque GROUP BY categoria ORDER BY valor DESC
    """)
    max_valor = df_cat["valor"].max() if not df_cat.empty else 1
    categorias = [
        {"label": r["categoria"], "valor": f"R$ {r['valor']:,.2f}",
         "pct": round(r["valor"] / max_valor * 100, 1)}
        for _, r in df_cat.iterrows()
    ]

    return render_template("estoque.html", produtos=produtos, categorias=categorias)


# ── Logística ─────────────────────────────────────────────

@app.route("/logistica")
def logistica():
    df = consultar("""
        SELECT l.venda_id, e.nome AS produto, l.transportadora,
               l.data_despacho, l.data_entrega_prevista, l.data_entrega_real,
               l.status_entrega, l.cidade_destino, l.estado_destino, l.atraso_dias
        FROM logistica l
        JOIN vendas v  ON v.venda_id   = l.venda_id
        JOIN estoque e ON e.produto_id = v.produto_id
        ORDER BY l.data_despacho DESC
    """)
    envios = df.to_dict("records")
    for e in envios:
        e["data_despacho"] = formatar_data(e["data_despacho"])
        e["data_entrega_prevista"] = formatar_data(e["data_entrega_prevista"])
        e["data_entrega_real"] = formatar_data(e["data_entrega_real"])
        e["badge"] = STATUS_ENTREGA_BADGE.get(e["status_entrega"], "neutral")

    df_transp = consultar("""
        SELECT transportadora, COUNT(*) AS entregas,
               ROUND(AVG(atraso_dias), 2) AS atraso_medio
        FROM logistica
        WHERE status_entrega = 'entregue' AND atraso_dias IS NOT NULL
        GROUP BY transportadora ORDER BY atraso_medio ASC
    """)
    ranking = df_transp.to_dict("records")

    return render_template("logistica.html", envios=envios, ranking=ranking)


if __name__ == '__main__':
    DB_PATH = os.path.join(BASE_DIR, "loja.db")
    if not os.path.exists(DB_PATH):
        print("⚠ Banco de dados não encontrado!")
        print("  Execute primeiro: python setup_db.py")
        raise SystemExit(1)

    print("✓ Servidor iniciando em http://127.0.0.1:5050")
    # app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
    app.run(debug=True, host="127.0.0.1", port=5050, use_reloader=False)
