import io
import shutil

import duckdb

from pipeline import gold


class _Utf8Output(io.StringIO):
    def reconfigure(self, *, encoding):
        self.encoding_solicitada = encoding


def _stdout_capture(monkeypatch):
    output = _Utf8Output()
    monkeypatch.setattr(gold.sys, "stdout", output)
    return output


def _attach_football(caminho):
    return duckdb.connect(str(caminho))


def _criar_silver(caminho):
    with _attach_football(caminho) as conexao:
        conexao.execute("CREATE SCHEMA football.silver")
        conexao.execute(
            """
            CREATE TABLE football.silver.brasileirao (
                temporada BIGINT, posicao BIGINT, time VARCHAR, pontos BIGINT,
                jogos_disputados BIGINT, vitorias BIGINT, empates BIGINT,
                derrotas BIGINT, gols BIGINT, gols_sofridos BIGINT,
                saldo_de_gols BIGINT
            )
            """
        )
        # Os valores inventados formam duas posições em cada uma de duas temporadas.
        conexao.execute(
            """
            INSERT INTO football.silver.brasileirao VALUES
                (2024, 1, 'Clube A', 6, 2, 2, 0, 0, 5, 1, 4),
                (2024, 2, 'Clube B', 0, 2, 0, 0, 2, 1, 5, -4),
                (2023, 1, 'Clube A', 4, 2, 1, 1, 0, 3, 2, 1),
                (2023, 2, 'Clube B', 1, 2, 0, 1, 1, 2, 3, -1)
            """
        )
        conexao.execute(
            """
            CREATE TABLE football.silver.times (
                time VARCHAR, sigla VARCHAR, nome_completo VARCHAR,
                ano_fundacao BIGINT, estadio VARCHAR, cidade VARCHAR,
                estado VARCHAR, regiao VARCHAR
            )
            """
        )
        conexao.execute(
            """
            INSERT INTO football.silver.times VALUES
                ('Clube A', 'CA', 'Clube A Completo', 1900, 'Estádio A',
                 'Cidade A', 'SP', 'Sudeste'),
                ('Clube B', 'CB', 'Clube B Completo', 1910, 'Estádio B',
                 'Cidade B', 'RS', 'Sul')
            """
        )


def _copiar_sql_gold(tmp_path):
    pasta = tmp_path / "sql_gold"
    pasta.mkdir()
    origem = gold.PASTA_SQL
    for arquivo in origem.glob("*.sql"):
        shutil.copyfile(arquivo, pasta / arquivo.name)
    return pasta


def test_descobrir_consultas_requer_pasta_e_arquivos(monkeypatch, tmp_path):
    monkeypatch.setattr(gold, "PASTA_SQL", tmp_path / "inexistente")
    try:
        gold._descobrir_consultas()
    except SystemExit as erro:
        assert erro.code == 1
    else:
        raise AssertionError("deveria encerrar quando a pasta SQL falta")

    pasta = tmp_path / "sem_consultas"
    pasta.mkdir()
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    try:
        gold._descobrir_consultas()
    except SystemExit as erro:
        assert erro.code == 1
    else:
        raise AssertionError("deveria encerrar quando não há SQL")


def test_descobrir_consultas_rejeita_nome_invalido_e_colisao(
    monkeypatch, tmp_path
):
    pasta = tmp_path / "sql"
    pasta.mkdir()
    (pasta / "consulta.sql").write_text("SELECT 1", encoding="utf-8")
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    try:
        gold._descobrir_consultas()
    except SystemExit as erro:
        assert erro.code == 1
    else:
        raise AssertionError("deveria rejeitar nome fora do padrão")

    (pasta / "consulta.sql").unlink()
    (pasta / "01_relatorio.sql").write_text("SELECT 1", encoding="utf-8")
    (pasta / "02_relatorio.sql").write_text("SELECT 1", encoding="utf-8")
    try:
        gold._descobrir_consultas()
    except SystemExit as erro:
        assert erro.code == 1
    else:
        raise AssertionError("deveria rejeitar tabelas duplicadas")


def test_gold_materializa_consultas_existentes_sobre_silver_inventada(
    monkeypatch, tmp_path
):
    banco = tmp_path / "football.duckdb"
    _criar_silver(banco)
    pasta_sql = _copiar_sql_gold(tmp_path)
    monkeypatch.setattr(gold, "PASTA_SQL", pasta_sql)
    monkeypatch.setattr(gold.db, "conectar", lambda: _attach_football(banco))
    saida = _stdout_capture(monkeypatch)

    assert gold.main() == 0
    assert saida.encoding_solicitada == "utf-8"
    assert "Tabelas Gold criadas: 10" in saida.getvalue()
    with _attach_football(banco) as conexao:
        assert conexao.execute(
            "SELECT COUNT(*) FROM football.gold.campeoes_por_temporada"
        ).fetchone() == (2,)
        assert conexao.execute(
            "SELECT temporada, campeao, pontos "
            "FROM football.gold.campeoes_por_temporada ORDER BY temporada"
        ).fetchall() == [(2023, "Clube A", 4), (2024, "Clube A", 6)]
        assert conexao.execute(
            "SELECT temporada, time, aproveitamento_pct "
            "FROM football.gold.aproveitamento_por_time_temporada "
            "WHERE time = 'Clube A' ORDER BY temporada"
        ).fetchall() == [(2023, "Clube A", 66.67), (2024, "Clube A", 100.0)]
        assert conexao.execute(
            "SELECT estado, total_clubes FROM football.gold.clubes_por_estado"
        ).fetchall() == [("RS", 1), ("SP", 1)]
        assert conexao.execute(
            "SELECT COUNT(*) FROM football.gold.relacao_posicao_saldo_gols"
        ).fetchone() == (4,)


def test_gold_falha_sem_tabelas_silver_necessarias(monkeypatch, tmp_path):
    banco = tmp_path / "football.duckdb"
    with _attach_football(banco) as conexao:
        conexao.execute("CREATE SCHEMA football.silver")
    pasta = tmp_path / "sql"
    pasta.mkdir()
    (pasta / "01_saida.sql").write_text("SELECT 1 AS valor", encoding="utf-8")
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    monkeypatch.setattr(gold.db, "conectar", lambda: _attach_football(banco))
    _stdout_capture(monkeypatch)

    assert gold.main() == 1


def test_gold_informa_falha_de_conexao_antes_de_iniciar_transacao(
    monkeypatch, tmp_path
):
    pasta = tmp_path / "sql"
    pasta.mkdir()
    (pasta / "01_saida.sql").write_text("SELECT 1 AS valor", encoding="utf-8")
    caminho_modulo = tmp_path / "diretorio_inexistente" / "pipeline" / "db.py"
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    monkeypatch.setattr(gold.db, "__file__", str(caminho_modulo))
    _stdout_capture(monkeypatch)

    assert gold.main() == 1


def test_gold_rollback_preserva_schema_existente_apos_falha(
    monkeypatch, tmp_path
):
    banco = tmp_path / "football.duckdb"
    _criar_silver(banco)
    with _attach_football(banco) as conexao:
        conexao.execute("CREATE SCHEMA football.gold")
        conexao.execute("CREATE TABLE football.gold.anterior AS SELECT 42 AS valor")
    pasta = tmp_path / "sql"
    pasta.mkdir()
    (pasta / "01_parcial.sql").write_text(
        "SELECT * FROM football.silver.brasileirao", encoding="utf-8"
    )
    (pasta / "02_invalida.sql").write_text(
        "SELECT * FROM football.silver.nao_existe", encoding="utf-8"
    )
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    monkeypatch.setattr(gold.db, "conectar", lambda: _attach_football(banco))
    _stdout_capture(monkeypatch)

    assert gold.main() == 1
    with _attach_football(banco) as conexao:
        assert conexao.execute(
            "SELECT valor FROM football.gold.anterior"
        ).fetchall() == [(42,)]
        assert not conexao.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_catalog = 'football' AND table_schema = 'gold' "
            "AND table_name = 'parcial'"
        ).fetchall()


def test_gold_rollback_se_tabela_resultante_ficar_vazia(monkeypatch, tmp_path):
    banco = tmp_path / "football.duckdb"
    _criar_silver(banco)
    with _attach_football(banco) as conexao:
        conexao.execute("CREATE SCHEMA football.gold")
        conexao.execute("CREATE TABLE football.gold.anterior AS SELECT 7 AS valor")
    pasta = tmp_path / "sql"
    pasta.mkdir()
    (pasta / "01_vazia.sql").write_text(
        "SELECT * FROM football.silver.brasileirao WHERE FALSE",
        encoding="utf-8",
    )
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    monkeypatch.setattr(gold.db, "conectar", lambda: _attach_football(banco))
    _stdout_capture(monkeypatch)

    assert gold.main() == 1
    with _attach_football(banco) as conexao:
        assert conexao.execute(
            "SELECT valor FROM football.gold.anterior"
        ).fetchall() == [(7,)]


def test_gold_recria_resultados_sem_tabelas_removidas_dos_sql(
    monkeypatch, tmp_path
):
    banco = tmp_path / "football.duckdb"
    _criar_silver(banco)
    with _attach_football(banco) as conexao:
        conexao.execute("CREATE SCHEMA football.gold")
        conexao.execute("CREATE TABLE football.gold.obsoleta AS SELECT 1 AS id")
    pasta = tmp_path / "sql"
    pasta.mkdir()
    (pasta / "01_atual.sql").write_text(
        "SELECT 1 AS valor", encoding="utf-8"
    )
    monkeypatch.setattr(gold, "PASTA_SQL", pasta)
    monkeypatch.setattr(gold.db, "conectar", lambda: _attach_football(banco))
    _stdout_capture(monkeypatch)

    assert gold.main() == 0
    with _attach_football(banco) as conexao:
        nomes = {
            linha[0]
            for linha in conexao.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_catalog = 'football' AND table_schema = 'gold'"
            ).fetchall()
        }
        assert nomes == {"atual"}
