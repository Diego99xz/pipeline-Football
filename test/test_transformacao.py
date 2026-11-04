import duckdb

from pipeline import transformacao


def _criar_bronze(caminho, *, temporadas=("2024",), valor_pontos="6"):
    with duckdb.connect(str(caminho)) as conexao:
        conexao.execute("CREATE SCHEMA bronze")
        conexao.execute("CREATE SCHEMA silver")
        conexao.execute(
            """
            CREATE TABLE bronze.brasileirao (
                temporada VARCHAR, posicao VARCHAR, time VARCHAR, pontos VARCHAR,
                jogos_disputados VARCHAR, vitorias VARCHAR, empates VARCHAR,
                derrotas VARCHAR, gols VARCHAR, gols_sofridos VARCHAR,
                saldo_de_gols VARCHAR
            )
            """
        )
        for temporada in temporadas:
            conexao.execute(
                """
                INSERT INTO bronze.brasileirao VALUES
                    (?, '1', 'Clube A', ?, '2', '2', '0', '0', '4', '1', '3'),
                    (?, '2', 'Clube B', '0', '2', '0', '0', '2', '1', '4', '-3')
                """,
                [temporada, valor_pontos, temporada],
            )
        conexao.execute(
            """
            CREATE TABLE bronze.times (
                time VARCHAR, sigla VARCHAR, nome_completo VARCHAR,
                ano_fundacao VARCHAR, estadio VARCHAR, cidade VARCHAR,
                estado VARCHAR, regiao VARCHAR
            )
            """
        )
        conexao.execute(
            """
            INSERT INTO bronze.times VALUES
                ('Clube A', 'CA', 'Clube A Completo', '1900', 'Estádio A',
                 'Cidade A', 'SP', 'Sudeste'),
                ('Clube B', 'CB', 'Clube B Completo', NULL, NULL, 'Cidade B',
                 'RS', 'Sul')
            """
        )


def test_transformacao_converte_tipos_preserva_duplicatas_e_nulos(
    monkeypatch, tmp_path
):
    banco = tmp_path / "football.duckdb"
    _criar_bronze(banco, temporadas=("2024", "2024"))
    monkeypatch.setattr(
        transformacao.db, "conectar", lambda: duckdb.connect(str(banco))
    )

    assert transformacao.main() == 0
    with duckdb.connect(str(banco), read_only=True) as conexao:
        assert conexao.execute(
            "SELECT COUNT(*) FROM silver.brasileirao"
        ).fetchone() == (4,)
        assert conexao.execute(
            "SELECT temporada, pontos FROM silver.brasileirao "
            "WHERE time = 'Clube A' ORDER BY rowid"
        ).fetchall() == [(2024, 6), (2024, 6)]
        assert conexao.execute(
            "SELECT typeof(temporada), typeof(pontos) FROM silver.brasileirao LIMIT 1"
        ).fetchone() == ("BIGINT", "BIGINT")
        assert conexao.execute(
            "SELECT ano_fundacao, estadio FROM silver.times WHERE time = 'Clube B'"
        ).fetchone() == (None, None)


def test_transformacao_falha_sem_todas_as_tabelas_de_origem(
    monkeypatch, tmp_path
):
    banco = tmp_path / "football.duckdb"
    with duckdb.connect(str(banco)) as conexao:
        conexao.execute("CREATE SCHEMA bronze")
        conexao.execute("CREATE TABLE bronze.brasileirao (temporada VARCHAR)")
    monkeypatch.setattr(
        transformacao.db, "conectar", lambda: duckdb.connect(str(banco))
    )

    assert transformacao.main() == 1
    with duckdb.connect(str(banco), read_only=True) as conexao:
        assert not conexao.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'silver'"
        ).fetchall()


def test_transformacao_rejeita_valor_numerico_invalido(monkeypatch, tmp_path):
    banco = tmp_path / "football.duckdb"
    _criar_bronze(banco, valor_pontos="inválido")
    monkeypatch.setattr(
        transformacao.db, "conectar", lambda: duckdb.connect(str(banco))
    )

    assert transformacao.main() == 1
