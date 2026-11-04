import duckdb
import pandas as pd
import pytest

from pipeline import db


def test_conectar_cria_banco_ao_lado_do_modulo(monkeypatch, tmp_path):
    pasta_pipeline = tmp_path / "pipeline"
    pasta_pipeline.mkdir()
    monkeypatch.setattr(db, "__file__", str(pasta_pipeline / "db.py"))

    conexao = db.conectar()
    try:
        conexao.execute("SELECT 1").fetchone()
    finally:
        conexao.close()

    assert (tmp_path / "football.duckdb").is_file()


def test_criar_schema_e_gravar_substituem_tabela_e_limpam_registro():
    conexao = duckdb.connect(":memory:")
    try:
        db.criar_schema(conexao, 'camada"teste')
        primeira = pd.DataFrame({"id": [1, 2], "nome": ["A", "B"]})
        assert db.gravar(conexao, primeira, 'camada"teste', 'resultado"teste') == 2

        segunda = pd.DataFrame({"id": [3], "nome": ["C"]})
        assert db.gravar(conexao, segunda, 'camada"teste', 'resultado"teste') == 1
        assert conexao.execute(
            'SELECT * FROM "camada""teste"."resultado""teste"'
        ).fetchall() == [(3, "C")]

        conexao.register("_dataframe_ingestao", segunda)
        assert conexao.execute("SELECT COUNT(*) FROM _dataframe_ingestao").fetchall() == [
            (1,)
        ]
        conexao.unregister("_dataframe_ingestao")
    finally:
        conexao.close()


def test_gravar_fecha_registro_dataframe_apos_falha_na_criacao():
    conexao = duckdb.connect(":memory:")
    try:
        with pytest.raises(duckdb.CatalogException):
            db.gravar(conexao, pd.DataFrame({"id": [1]}), "inexistente", "tabela")

        conexao.register("_dataframe_ingestao", pd.DataFrame({"id": [2]}))
        assert conexao.execute("SELECT id FROM _dataframe_ingestao").fetchall() == [(2,)]
    finally:
        conexao.close()
