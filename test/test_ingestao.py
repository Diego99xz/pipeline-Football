import duckdb

from pipeline import ingestao


def _conectar_temporario(caminho):
    return duckdb.connect(str(caminho))


def test_ingestao_preserva_colunas_textuais_e_substitui_registros(
    monkeypatch, tmp_path
):
    bronze = tmp_path / "bronze"
    bronze.mkdir()
    monkeypatch.setattr(ingestao.db, "PASTA_BRONZE", bronze)
    banco = tmp_path / "ingestao.duckdb"
    monkeypatch.setattr(
        ingestao.db, "conectar", lambda: _conectar_temporario(banco)
    )
    (bronze / "brasileirao.csv").write_text(
        "temporada,time\n2024,Clube A\n2023,Clube B\n", encoding="utf-8"
    )
    (bronze / "times.csv").write_text(
        "time,estado\nClube A,SP\nClube B,\n", encoding="utf-8"
    )

    assert ingestao.main() == 0
    with duckdb.connect(str(banco), read_only=True) as conexao:
        assert conexao.execute(
            "SELECT temporada, time FROM bronze.brasileirao ORDER BY temporada"
        ).fetchall() == [("2023", "Clube B"), ("2024", "Clube A")]
        assert conexao.execute(
            "SELECT time, estado FROM bronze.times ORDER BY time"
        ).fetchall() == [("Clube A", "SP"), ("Clube B", None)]

    (bronze / "brasileirao.csv").write_text(
        "temporada,time\n2025,Clube C\n", encoding="utf-8"
    )
    assert ingestao.main() == 0
    with duckdb.connect(str(banco), read_only=True) as conexao:
        assert conexao.execute("SELECT * FROM bronze.brasileirao").fetchall() == [
            ("2025", "Clube C")
        ]


def test_ingestao_nao_grava_se_arquivo_necessario_esta_ausente(
    monkeypatch, tmp_path
):
    bronze = tmp_path / "bronze"
    bronze.mkdir()
    monkeypatch.setattr(ingestao.db, "PASTA_BRONZE", bronze)
    monkeypatch.setattr(
        ingestao.db,
        "conectar",
        lambda: (_ for _ in ()).throw(AssertionError("não deveria conectar")),
    )
    (bronze / "brasileirao.csv").write_text(
        "temporada,time\n2024,Clube A\n", encoding="utf-8"
    )

    assert ingestao.main() == 1


def test_ingestao_informa_erro_de_leitura_sem_conectar(monkeypatch, tmp_path):
    bronze = tmp_path / "bronze"
    bronze.mkdir()
    monkeypatch.setattr(ingestao.db, "PASTA_BRONZE", bronze)
    monkeypatch.setattr(
        ingestao.db,
        "conectar",
        lambda: (_ for _ in ()).throw(AssertionError("não deveria conectar")),
    )
    arquivo = bronze / "brasileirao.csv"
    arquivo.write_text("conteúdo inválido\n", encoding="utf-8")
    (bronze / "times.csv").write_text("time\nClube A\n", encoding="utf-8")
    leitor_original = ingestao.pd.read_csv

    def leitor_com_erro(caminho, **kwargs):
        if caminho == arquivo:
            raise ValueError("CSV inválido")
        return leitor_original(caminho, **kwargs)

    monkeypatch.setattr(ingestao.pd, "read_csv", leitor_com_erro)

    assert ingestao.main() == 1


def test_ingestao_fecha_conexao_quando_gravacao_falha(monkeypatch, tmp_path):
    bronze = tmp_path / "bronze"
    bronze.mkdir()
    banco = tmp_path / "falha.duckdb"
    monkeypatch.setattr(ingestao.db, "PASTA_BRONZE", bronze)
    monkeypatch.setattr(
        ingestao.db, "conectar", lambda: _conectar_temporario(banco)
    )
    for nome in ("brasileirao.csv", "times.csv"):
        (bronze / nome).write_text("time\nClube A\n", encoding="utf-8")
    monkeypatch.setattr(
        ingestao.db,
        "criar_schema",
        lambda con, schema: (_ for _ in ()).throw(duckdb.IOException("falha")),
    )

    assert ingestao.main() == 1
    with duckdb.connect(str(banco), read_only=True) as conexao:
        assert conexao.execute("SELECT 1").fetchone() == (1,)
