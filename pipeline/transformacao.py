"""Transformação de tipos das tabelas Bronze para Silver.

Esta etapa lê somente ``football.bronze.brasileirao`` e
``football.bronze.times`` e recria suas cópias em ``football.silver``. A
separação por camada preserva a Bronze como origem e mantém Gold fora do
escopo.

As tabelas de entrada são verificadas antes de qualquer gravação para evitar
uma execução parcial causada por origem ausente. A Bronze mantém todas as
colunas como texto; esta etapa define explicitamente os tipos Silver já
observados: ``BIGINT`` para temporadas, posições, estatísticas e ano de
fundação, e ``VARCHAR`` para os demais campos. Os aliases preservam os nomes
e a ordem das colunas. A conversão mantém linhas, duplicatas e nulos; valores
que não possam ser convertidos causam erro em vez de serem corrigidos ou
descartados. Não há JOIN nem regras de negócio. ``CREATE OR REPLACE TABLE``
substitui a saída em cada execução, em vez de acumular linhas. As contagens
de origem e saída são consultadas no banco e exibidas para informar o
resultado efetivamente processado.
"""

import sys

import duckdb

from . import db

CATALOGO = "football"
SCHEMA_ORIGEM = "bronze"
SCHEMA_DESTINO = "silver"
TABELAS = ("brasileirao", "times")
COLUNAS_SILVER = {
    "brasileirao": (
        ("temporada", "BIGINT"),
        ("posicao", "BIGINT"),
        ("time", "VARCHAR"),
        ("pontos", "BIGINT"),
        ("jogos_disputados", "BIGINT"),
        ("vitorias", "BIGINT"),
        ("empates", "BIGINT"),
        ("derrotas", "BIGINT"),
        ("gols", "BIGINT"),
        ("gols_sofridos", "BIGINT"),
        ("saldo_de_gols", "BIGINT"),
    ),
    "times": (
        ("time", "VARCHAR"),
        ("sigla", "VARCHAR"),
        ("nome_completo", "VARCHAR"),
        ("ano_fundacao", "BIGINT"),
        ("estadio", "VARCHAR"),
        ("cidade", "VARCHAR"),
        ("estado", "VARCHAR"),
        ("regiao", "VARCHAR"),
    ),
}


def _identificador_sql(valor: str) -> str:
    return '"' + valor.replace('"', '""') + '"'


def _selecao_tipagem(tabela: str) -> str:
    return ", ".join(
        f"CAST({_identificador_sql(coluna)} AS {tipo}) "
        f"AS {_identificador_sql(coluna)}"
        for coluna, tipo in COLUNAS_SILVER[tabela]
    )


def _contagem(
    con: duckdb.DuckDBPyConnection,
    catalogo: str,
    schema: str,
    tabela: str,
) -> int:
    referencia = ".".join(
        _identificador_sql(parte) for parte in (catalogo, schema, tabela)
    )
    resultado = con.execute(f"SELECT COUNT(*) FROM {referencia}").fetchone()
    return int(resultado[0])


def main() -> int:
    con = None
    codigo_saida = 0
    etapa = "conexão com o banco"

    try:
        con = db.conectar()
        tabelas_encontradas = {
            linha[0]
            for linha in con.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_catalog = ? AND table_schema = ? "
                "AND table_type = 'BASE TABLE' "
                "AND table_name IN (?, ?)",
                [CATALOGO, SCHEMA_ORIGEM, *TABELAS],
            ).fetchall()
        }
        tabelas_ausentes = [
            f"{CATALOGO}.{SCHEMA_ORIGEM}.{tabela}"
            for tabela in TABELAS
            if tabela not in tabelas_encontradas
        ]
        if tabelas_ausentes:
            print(
                "Tabelas de entrada não encontradas: "
                + ", ".join(tabelas_ausentes),
                file=sys.stderr,
            )
            return 1

        etapa = f"criação do schema {CATALOGO}.{SCHEMA_DESTINO}"
        db.criar_schema(con, SCHEMA_DESTINO)

        resultados: list[tuple[str, int, int]] = []
        for tabela in TABELAS:
            origem = ".".join(
                _identificador_sql(parte)
                for parte in (CATALOGO, SCHEMA_ORIGEM, tabela)
            )
            destino = ".".join(
                _identificador_sql(parte)
                for parte in (CATALOGO, SCHEMA_DESTINO, tabela)
            )

            etapa = f"contagem da origem {CATALOGO}.{SCHEMA_ORIGEM}.{tabela}"
            quantidade_origem = _contagem(
                con, CATALOGO, SCHEMA_ORIGEM, tabela
            )
            etapa = f"gravação de {CATALOGO}.{SCHEMA_DESTINO}.{tabela}"
            con.execute(
                f"CREATE OR REPLACE TABLE {destino} "
                f"AS SELECT {_selecao_tipagem(tabela)} FROM {origem}"
            ).fetchall()
            etapa = f"contagem do destino {CATALOGO}.{SCHEMA_DESTINO}.{tabela}"
            quantidade_destino = _contagem(
                con, CATALOGO, SCHEMA_DESTINO, tabela
            )
            resultados.append((tabela, quantidade_origem, quantidade_destino))

        for tabela, quantidade_origem, quantidade_destino in resultados:
            print(
                f"{CATALOGO}.{SCHEMA_ORIGEM}.{tabela} -> "
                f"{CATALOGO}.{SCHEMA_DESTINO}.{tabela}: concluído "
                f"(origem={quantidade_origem}, destino={quantidade_destino})"
            )
    except (duckdb.Error, OSError, TypeError, ValueError) as erro:
        print(f"Erro na etapa de {etapa}: {erro}", file=sys.stderr)
        codigo_saida = 1
    finally:
        if con is not None:
            try:
                con.close()
            except (duckdb.Error, OSError) as erro:
                print(f"Erro ao fechar a conexão DuckDB: {erro}", file=sys.stderr)
                codigo_saida = 1

    return codigo_saida


if __name__ == "__main__":
    raise SystemExit(main())
