"""
setup_db.py
-----------
Responsável por ler os três arquivos CSV com pandas e
popular as tabelas de um banco SQL relacional (SQLite por padrão).
Execute este módulo UMA vez antes de rodar os exercícios.

Pré-requisitos:
    pip install pandas sqlalchemy

Por que SQLite?
    Não exige servidor instalado — o banco fica em um único arquivo
    (loja.db) na pasta do projeto. Para usar PostgreSQL ou MySQL,
    basta trocar a DATABASE_URL abaixo (ex.:
    "postgresql+psycopg2://user:senha@localhost/loja_db") — todo o
    resto do código (aqui e em exercicios.py) continua igual, pois
    o SQLAlchemy abstrai o dialeto do banco.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

# ── Configuração ──────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(BASE_DIR, "data")
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'loja.db')}"


# ── Helpers ───────────────────────────────────────────────

def converter_datas(df: pd.DataFrame, colunas: list) -> pd.DataFrame:
    """Converte colunas de texto para datetime, ignorando valores inválidos."""
    for col in colunas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def limpar_e_inserir(engine, df: pd.DataFrame, tabela: str, chave_unica: str) -> None:
    """
    Recria a tabela a partir do zero e insere os registros.
    Usar if_exists='replace' aqui garante que rodar o setup
    múltiplas vezes não duplique dados — equivalente ao
    colecao.drop() da versão MongoDB.
    """
    df.to_sql(tabela, engine, if_exists="replace", index=False)

    # Cria um índice único, equivalente ao create_index() do MongoDB
    with engine.begin() as conn:
        conn.execute(text(
            f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{tabela}_{chave_unica} "
            f"ON {tabela} ({chave_unica})"
        ))

    print(f"  ✔ {tabela}: {len(df)} registros inseridos.")


# ── Função principal ──────────────────────────────────────

def setup(database_url: str = DATABASE_URL):
    """
    Lê os CSVs, trata os dados com pandas e popula o banco SQL.
    Retorna o engine do SQLAlchemy para reuso opcional.
    """
    engine = create_engine(database_url)

    print("=" * 50)
    print("  Configurando banco de dados:", database_url)
    print("=" * 50)

    # ── 1. ESTOQUE ────────────────────────────────────────
    df_estoque = pd.read_csv(os.path.join(DATA_DIR, "estoque.csv"))
    df_estoque["quantidade_estoque"] = df_estoque["quantidade_estoque"].astype(int)
    df_estoque["estoque_minimo"]     = df_estoque["estoque_minimo"].astype(int)
    df_estoque["custo_unitario"]     = df_estoque["custo_unitario"].astype(float)
    limpar_e_inserir(engine, df_estoque, "estoque", "produto_id")

    # ── 2. VENDAS ─────────────────────────────────────────
    df_vendas = pd.read_csv(os.path.join(DATA_DIR, "vendas.csv"))
    df_vendas = converter_datas(df_vendas, ["data_venda"])
    df_vendas["quantidade"]     = df_vendas["quantidade"].astype(int)
    df_vendas["preco_unitario"] = df_vendas["preco_unitario"].astype(float)
    # Campo calculado: valor total da venda
    df_vendas["valor_total"] = df_vendas["quantidade"] * df_vendas["preco_unitario"]
    limpar_e_inserir(engine, df_vendas, "vendas", "venda_id")

    # ── 3. LOGÍSTICA ──────────────────────────────────────
    df_log = pd.read_csv(os.path.join(DATA_DIR, "logistica.csv"))
    df_log = converter_datas(
        df_log,
        ["data_despacho", "data_entrega_prevista", "data_entrega_real"]
    )
    # Campo calculado: atraso em dias (positivo = atrasou)
    df_log["atraso_dias"] = (
        df_log["data_entrega_real"] - df_log["data_entrega_prevista"]
    ).dt.days
    limpar_e_inserir(engine, df_log, "logistica", "logistica_id")

    print("\n  Banco pronto! Tabelas criadas: estoque, vendas, logistica")
    print("=" * 50)
    return engine


# ── Execução direta ───────────────────────────────────────
if __name__ == "__main__":
    setup()
