"""Acesso ao DuckDB usado pelo pipeline.

Esta camada expõe somente o caminho Bronze e as operações de conexão, schema
e gravação. Essa separação mantém leitura de CSV, regras de negócio e saída
fora do módulo de banco (D2). Os caminhos são relativos a este arquivo, não
ao diretório corrente, para que executar o pipeline de outra pasta não use
arquivos incorretos (D1).

``conectar`` devolve uma conexão aberta e não a mantém globalmente; quem a
utiliza deve fechá-la (D4). ``gravar`` substitui a tabela e consulta no banco
a contagem resultante, evitando acumulação e retornando o dado efetivamente
persistido (D3).
"""

from pathlib import Path as _Path

import duckdb as _duckdb
import pandas as _pd

PASTA_BRONZE = _Path(__file__).resolve().parent.parent / "bronze"


def conectar() -> _duckdb.DuckDBPyConnection:
    """Abre o arquivo DuckDB ao lado da pasta Bronze, criando-o se necessário."""
    caminho_banco = _Path(__file__).resolve().parent.parent / "football.duckdb"
    return _duckdb.connect(str(caminho_banco))


def criar_schema(con: _duckdb.DuckDBPyConnection, nome: str) -> None:
    """Cria o schema caso ainda não exista."""
    identificador = nome.replace('"', '""')
    con.execute(f'CREATE SCHEMA IF NOT EXISTS "{identificador}"')


def gravar(
    con: _duckdb.DuckDBPyConnection,
    df: _pd.DataFrame,
    schema: str,
    tabela: str,
) -> int:
    """Substitui a tabela pelo DataFrame e devolve a contagem consultada no banco."""
    schema_sql = schema.replace('"', '""')
    tabela_sql = tabela.replace('"', '""')
    con.register("_dataframe_ingestao", df)
    try:
        con.execute(
            f'CREATE OR REPLACE TABLE "{schema_sql}"."{tabela_sql}" '
            "AS SELECT * FROM _dataframe_ingestao"
        ).fetchall()
    finally:
        con.unregister("_dataframe_ingestao")

    resultado = con.execute(
        f'SELECT COUNT(*) FROM "{schema_sql}"."{tabela_sql}"'
    ).fetchall()
    return int(resultado[0][0])
