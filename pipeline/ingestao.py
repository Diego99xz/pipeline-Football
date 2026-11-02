"""Ingestão dos CSVs de origem para a camada Bronze.

A ingestão usa somente ``brasileirao.csv`` e ``times.csv`` e grava,
respectivamente, em ``bronze.brasileirao`` e ``bronze.times``; os nomes
explícitos limitam o escopo e evitam tabelas adicionais. Os arquivos são
lidos da pasta Bronze definida pelo módulo de banco, que resolve o caminho
relativamente ao próprio código.

Os DataFrames são lidos sem transformação explícita: cabeçalhos e valores
seguem o comportamento padrão de ``pandas.read_csv``. Cada gravação substitui
a tabela, tornando reexecuções não cumulativas. A saída usa as contagens
consultadas pelo módulo de banco. Arquivos ausentes são detectados antes da
leitura e de qualquer gravação; falhas de cada etapa são informadas e causam
saída diferente de zero, com fechamento da conexão quando aberta.
"""

import sys

import duckdb
import pandas as pd

if __package__:
    from . import db
else:
    import db


ARQUIVOS = (
    ("brasileirao.csv", "brasileirao"),
    ("times.csv", "times"),
)


def main() -> int:
    caminhos = [(nome, tabela, db.PASTA_BRONZE / nome) for nome, tabela in ARQUIVOS]
    ausentes = [nome for nome, _, caminho in caminhos if not caminho.is_file()]
    if ausentes:
        for nome in ausentes:
            print(f"Arquivo necessário não encontrado: {nome}", file=sys.stderr)
        return 1

    dataframes: dict[str, pd.DataFrame] = {}
    for nome, _, caminho in caminhos:
        try:
            dataframes[nome] = pd.read_csv(caminho)
        except (OSError, ValueError) as erro:
            print(f"Erro na etapa de leitura de {nome}: {erro}", file=sys.stderr)
            return 1

    con = None
    codigo_saida = 0
    etapa = "conexão com o banco"
    try:
        con = db.conectar()
        etapa = "criação do schema bronze"
        db.criar_schema(con, "bronze")

        for nome, tabela, _ in caminhos:
            etapa = f"gravação de bronze.{tabela}"
            quantidade = db.gravar(con, dataframes[nome], "bronze", tabela)
            print(f"bronze.{tabela}: {quantidade}")
    except (duckdb.Error, OSError, TypeError, ValueError) as erro:
        print(f"Erro na etapa de {etapa}: {erro}", file=sys.stderr)
        codigo_saida = 1
    finally:
        if con is not None:
            try:
                con.close()
            except (duckdb.Error, OSError) as erro:
                print(f"Erro na etapa de fechamento da conexão: {erro}", file=sys.stderr)
                codigo_saida = 1

    return codigo_saida


if __name__ == "__main__":
    raise SystemExit(main())
