"""Materialização das consultas analíticas SQL na camada Gold.

Esta etapa lê ``football.silver.brasileirao`` e ``football.silver.times`` e
materializa cada consulta de ``sql/gold/*.sql`` no schema ``football.gold``.
Bronze e Silver são fontes somente de leitura nesta etapa. Os arquivos SQL
são a fonte da verdade analítica; o Python valida nomes e executa seu
conteúdo, sem completar nem modificar a lógica das consultas.

Os arquivos são processados em ordem alfabética. Cada nome deve seguir
``NN_nome.sql``, com exatamente dois dígitos, para que o prefixo ordene as
consultas e o restante determine o nome previsível da tabela. Arquivos sem
esse padrão ou que gerem nomes duplicados são rejeitados antes de qualquer
consulta, evitando sobrescritas e execução parcial por erro de nomenclatura.

As duas tabelas Silver são verificadas antes da materialização, pois todas as
consultas Gold dependem delas. A pasta SQL também precisa existir e conter
arquivos SQL, para que uma execução sem definições não seja apresentada como
sucesso.

O schema Gold é apagado e recriado dentro de uma única transação. Cada arquivo
cria uma tabela com ``CREATE TABLE ... AS`` e a contagem é consultada no
DuckDB, não estimada a partir do SQL. Tabelas vazias causam erro porque podem
indicar uma consulta analítica inválida. Qualquer falha executa rollback,
preservando exatamente o último schema Gold bem-sucedido e evitando que
consumidores leiam resultados parciais. Reexecutar reconstrói o schema a
partir do conjunto atual de arquivos; assim, tabelas de arquivos removidos
também desaparecem após uma execução bem-sucedida.

A saída informa cada tabela e sua contagem real, além do número de tabelas e
da soma das linhas, com ponto como separador de milhar. O stdout é
reconfigurado para UTF-8 para exibir corretamente os caracteres da saída.
"""

import re
import sys
from pathlib import Path

import duckdb

from . import db

CATALOGO = "football"
SCHEMA_ENTRADA = "silver"
SCHEMA_SAIDA = "gold"
TABELAS_ENTRADA = ("brasileirao", "times")
PASTA_SQL = Path(__file__).resolve().parent.parent / "sql" / "gold"
PADRAO_ARQUIVO = re.compile(r"^\d{2}_(.+)\.sql$")


def _identificador_sql(valor: str) -> str:
    return '"' + valor.replace('"', '""') + '"'


def _descobrir_consultas() -> list[tuple[Path, str]]:
    if not PASTA_SQL.is_dir():
        print(f"Pasta de consultas não encontrada: {PASTA_SQL}", file=sys.stderr)
        raise SystemExit(1)

    arquivos = sorted(PASTA_SQL.glob("*.sql"), key=lambda caminho: caminho.name)
    if not arquivos:
        print(f"Nenhum arquivo .sql encontrado em {PASTA_SQL}", file=sys.stderr)
        raise SystemExit(1)

    consultas: list[tuple[Path, str]] = []
    arquivos_invalidos: list[str] = []
    tabelas_por_nome: dict[str, list[Path]] = {}

    for arquivo in arquivos:
        correspondencia = PADRAO_ARQUIVO.fullmatch(arquivo.name)
        if correspondencia is None:
            arquivos_invalidos.append(arquivo.name)
            continue

        nome_tabela = correspondencia.group(1)
        tabelas_por_nome.setdefault(nome_tabela, []).append(arquivo)
        consultas.append((arquivo, nome_tabela))

    if arquivos_invalidos:
        print(
            "Arquivos SQL fora do padrão NN_nome.sql: "
            + ", ".join(arquivos_invalidos),
            file=sys.stderr,
        )

    colisoes = {
        nome: caminhos
        for nome, caminhos in tabelas_por_nome.items()
        if len(caminhos) > 1
    }
    if colisoes:
        for nome, caminhos in sorted(colisoes.items()):
            print(
                f"Arquivos geram o mesmo nome de tabela "
                f"'{nome}': {', '.join(caminho.name for caminho in caminhos)}",
                file=sys.stderr,
            )

    if arquivos_invalidos or colisoes:
        raise SystemExit(1)

    return consultas


def _tabelas_silver_ausentes(con: duckdb.DuckDBPyConnection) -> list[str]:
    encontradas = {
        linha[0]
        for linha in con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_catalog = ? AND table_schema = ? "
            "AND table_type = 'BASE TABLE' AND table_name IN (?, ?)",
            [CATALOGO, SCHEMA_ENTRADA, *TABELAS_ENTRADA],
        ).fetchall()
    }
    return [
        f"{CATALOGO}.{SCHEMA_ENTRADA}.{tabela}"
        for tabela in TABELAS_ENTRADA
        if tabela not in encontradas
    ]


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


def _consultar_arquivo(arquivo: Path) -> str:
    consulta = arquivo.read_text(encoding="utf-8").strip()
    if consulta.endswith(";"):
        consulta = consulta[:-1].rstrip()
    return consulta


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    consultas = _descobrir_consultas()
    con = None
    transacao_iniciada = False
    arquivo_atual: Path | None = None

    try:
        con = db.conectar()
        tabelas_ausentes = _tabelas_silver_ausentes(con)
        if tabelas_ausentes:
            print(
                "Tabelas Silver não encontradas: "
                + ", ".join(tabelas_ausentes)
                + ". Execute `uv run python -m pipeline.transformacao`.",
                file=sys.stderr,
            )
            return 1

        con.execute("BEGIN TRANSACTION").fetchall()
        transacao_iniciada = True
        con.execute(
            f"DROP SCHEMA IF EXISTS "
            f"{_identificador_sql(CATALOGO)}.{_identificador_sql(SCHEMA_SAIDA)} "
            "CASCADE"
        ).fetchall()
        db.criar_schema(con, SCHEMA_SAIDA)

        resultados: list[tuple[str, int]] = []
        for arquivo, nome_tabela in consultas:
            arquivo_atual = arquivo
            consulta = _consultar_arquivo(arquivo)
            tabela_sql = ".".join(
                _identificador_sql(parte)
                for parte in (CATALOGO, SCHEMA_SAIDA, nome_tabela)
            )
            con.execute(
                f"CREATE TABLE {tabela_sql} AS {consulta}"
            ).fetchall()

            total_linhas = _contagem(
                con, CATALOGO, SCHEMA_SAIDA, nome_tabela
            )
            if total_linhas == 0:
                raise ValueError(
                    f"A tabela {CATALOGO}.{SCHEMA_SAIDA}.{nome_tabela} "
                    "foi criada sem registros."
                )
            resultados.append((nome_tabela, total_linhas))

        con.execute("COMMIT").fetchall()
        transacao_iniciada = False

        total_linhas = sum(quantidade for _, quantidade in resultados)
        for nome_tabela, quantidade in resultados:
            print(
                f"✓ {CATALOGO}.{SCHEMA_SAIDA}.{nome_tabela}    "
                f"{quantidade:,} linhas".replace(",", ".")
            )
        print(
            f"Tabelas Gold criadas: {len(resultados):,}".replace(",", ".")
        )
        print(f"Total de linhas: {total_linhas:,}".replace(",", "."))
        return 0
    except (duckdb.Error, OSError, UnicodeError, ValueError) as erro:
        if transacao_iniciada and con is not None:
            try:
                con.execute("ROLLBACK").fetchall()
            except duckdb.Error as erro_rollback:
                print(
                    f"Erro ao executar rollback: {erro_rollback}",
                    file=sys.stderr,
                )
        if arquivo_atual is not None:
            print(
                f"Erro no arquivo {arquivo_atual.name}: {erro}",
                file=sys.stderr,
            )
        else:
            print(f"Erro na materialização Gold: {erro}", file=sys.stderr)
        return 1
    finally:
        if con is not None:
            try:
                con.close()
            except duckdb.Error as erro:
                print(f"Erro ao fechar a conexão DuckDB: {erro}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
