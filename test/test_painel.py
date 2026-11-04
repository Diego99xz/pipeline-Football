import duckdb
import pandas as pd
import pytest

import painel


def _criar_gold_temporario(caminho):
    with duckdb.connect(str(caminho)) as conexao:
        conexao.execute("CREATE SCHEMA gold")
        conexao.execute(
            """
            CREATE TABLE gold.campeoes_por_temporada AS
            SELECT 2023 AS temporada, 'Clube A' AS campeao, 6 AS pontos
            UNION ALL
            SELECT 2024, 'Clube B', 9
            """
        )


def _dados_grafico():
    campeoes = pd.DataFrame(
        {
            "temporada": [2024, 2023],
            "campeao": ["Clube B", "Clube A"],
            "pontos": [9, 6],
        }
    )
    saldos = pd.DataFrame(
        {
            "temporada": [2024, 2024],
            "time": ["Clube A", "Clube B"],
            "posicao": [1, 2],
            "gols": [5, 1],
            "gols_sofridos": [1, 5],
            "saldo_de_gols": [4, -4],
        }
    )
    aproveitamento = pd.DataFrame(
        {
            "temporada": [2024, 2024],
            "time": ["Clube A", "Clube B"],
            "posicao": [1, 2],
            "pontos": [6, 0],
            "jogos_disputados": [2, 2],
            "aproveitamento_pct": [100.0, 0.0],
        }
    )
    regional = pd.DataFrame(
        {
            "temporada": [2024, 2024],
            "regiao": ["Sul", "Sudeste"],
            "times_participantes": [1, 1],
            "media_posicao": [2.0, 1.0],
            "media_pontos": [0.0, 6.0],
            "total_vitorias": [0, 2],
            "total_gols": [1, 5],
            "total_gols_sofridos": [5, 1],
        }
    )
    clubes_estado = pd.DataFrame(
        {
            "estado": ["SP", "RS"],
            "total_clubes": [1, 1],
            "regioes": ["Sudeste", "Sul"],
        }
    )
    comparativo = pd.DataFrame(
        {
            "temporada": [2024, 2024],
            "regiao": ["Sul", "Sudeste"],
            "total_times": [1, 1],
            "media_pontos": [0.0, 6.0],
            "media_vitorias": [0.0, 2.0],
            "media_gols": [1.0, 5.0],
            "media_saldo_de_gols": [-4.0, 4.0],
        }
    )
    posicao_saldo = pd.DataFrame(
        {
            "temporada": [2024, 2024],
            "time": ["Clube A", "Clube B"],
            "regiao": ["Sudeste", "Sul"],
            "posicao": [1, 2],
            "pontos": [6, 0],
            "saldo_de_gols": [4, -4],
            "gols": [5, 1],
            "gols_sofridos": [1, 5],
        }
    )
    return (
        campeoes,
        saldos,
        aproveitamento,
        regional,
        clubes_estado,
        comparativo,
        posicao_saldo,
    )


def test_leitura_gold_usa_o_caminho_configurado_e_ignora_tabelas_ausentes(
    monkeypatch, tmp_path
):
    caminho = tmp_path / "football.duckdb"
    _criar_gold_temporario(caminho)
    monkeypatch.setattr(painel, "CAMINHO_BANCO", caminho)

    dados = painel.ler_tabelas_gold()

    assert tuple(dados) == ("campeoes_por_temporada",)
    assert dados["campeoes_por_temporada"]["campeao"].tolist() == [
        "Clube A",
        "Clube B",
    ]


def test_leitura_gold_falha_com_mensagem_quando_banco_nao_existe(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(painel, "CAMINHO_BANCO", tmp_path / "ausente.duckdb")

    with pytest.raises(FileNotFoundError, match="DuckDB"):
        painel.ler_tabelas_gold()


def test_temporadas_disponiveis_faz_uniao_ordenada_apenas_das_tabelas_validas():
    dados = {
        "campeoes_por_temporada": pd.DataFrame({"temporada": [2024, 2022, None]}),
        "ranking_historico_times": pd.DataFrame({"temporada": [2023, 2022]}),
        "evolucao_pontuacao_campeao": pd.DataFrame({"temporada": [1990]}),
        "clubes_por_estado": pd.DataFrame({"ano": [2025]}),
    }

    assert painel.temporadas_disponiveis(dados) == [2024, 2023, 2022]


def test_filtrar_temporada_devolve_historico_ou_apenas_temporada_solicitada():
    historico = pd.DataFrame(
        {"temporada": [2023, 2024], "time": ["Clube A", "Clube B"]}
    )

    assert painel.filtrar_temporada(historico, None) is historico
    assert painel.filtrar_temporada(historico, 2024)["time"].tolist() == ["Clube B"]
    with pytest.raises(ValueError, match="coluna temporada"):
        painel.filtrar_temporada(pd.DataFrame({"time": ["Clube A"]}), 2024)


def test_validar_colunas_informa_colunas_ausentes_e_tabela_ausente():
    dados = {"campeoes_por_temporada": pd.DataFrame({"temporada": [2024]})}

    assert painel.validar_colunas(dados, "campeoes_por_temporada") == (
        False,
        [
            "campeao",
            "pontos",
            "vitorias",
            "empates",
            "derrotas",
            "gols",
            "gols_sofridos",
            "saldo_de_gols",
        ],
    )
    assert painel.validar_colunas({}, "campeoes_por_temporada") == (False, [])


def test_formatadores_numero_e_tabela_preservam_rotulos_e_formatacao():
    assert painel.formatar_numero(float("nan")) == "—"
    assert painel.formatar_numero(1234.5, 2) == "1.234,50"
    dados = pd.DataFrame(
        {
            "temporada": [2024],
            "campeao": ["Clube A"],
            "pontos": [6],
            "aproveitamento_pct": [66.67],
            "posicao": [1],
        }
    )

    html = painel.formatar_tabela(dados, "campeoes_por_temporada").to_html()

    assert "Campeão" in html
    assert "66,67%" in html
    assert "1º" in html
    assert "font-weight: 700" in html

    ranking = painel.formatar_tabela(
        pd.DataFrame({"posicao": [1], "time": ["Clube A"], "pontos": [6]}),
        "ranking_historico_times",
    ).to_html()
    assert "font-weight: 700" in ranking


def test_grafico_pontuacao_campeoes_exibe_historico_e_temporada():
    campeoes, *_ = _dados_grafico()

    historico = painel.grafico_pontuacao_campeoes(campeoes, None)
    temporada = painel.grafico_pontuacao_campeoes(
        campeoes.loc[campeoes["temporada"] == 2024], 2024
    )

    assert list(historico.data[0].x) == [2023, 2024]
    assert historico.layout.title.text == "02 · Pontuação dos campeões por temporada"
    assert list(temporada.data[0].x) == [2024]
    assert temporada.layout.title.text.endswith("2024")


def test_grafico_saldo_gols_rotula_temporada_no_historico():
    _, saldos, *_ = _dados_grafico()

    figura = painel.grafico_saldo_gols(saldos, None)

    assert list(figura.data[0].y) == ["Clube A · 2024", "Clube B · 2024"]
    assert figura.data[0].marker.color[1] == painel.CORES["vermelho"]
    assert figura.layout.xaxis.title.text == "Saldo de gols"


def test_grafico_aproveitamento_preserva_valores_e_limite_percentual():
    _, _, aproveitamento, *_ = _dados_grafico()

    figura = painel.grafico_aproveitamento(aproveitamento, 2024)

    assert list(figura.data[0].x) == [100.0, 0.0]
    assert list(figura.data[0].y) == ["Clube A", "Clube B"]
    assert list(figura.layout.xaxis.range) == [0, 100]


def test_grafico_regional_formata_metrica_e_reverte_eixo_de_posicao():
    _, _, _, regional, *_ = _dados_grafico()

    posicao = painel.grafico_desempenho_regional(
        regional, "Média de posição", 2024
    )
    pontos = painel.grafico_desempenho_regional(
        regional, "Média de pontos", None
    )

    assert posicao.layout.xaxis.autorange == "reversed"
    assert "Menor posição" in posicao.layout.annotations[0].text
    assert posicao.layout.title.text.endswith("2024")
    assert list(pontos.data[0].y) == ["Sudeste · 2024", "Sul · 2024"]


def test_grafico_clubes_por_estado_exibe_valores_e_eixos():
    _, _, _, _, estados, *_ = _dados_grafico()

    figura = painel.grafico_clubes_por_estado(estados)

    assert list(figura.data[0].x) == [1, 1]
    assert list(figura.data[0].y) == ["SP", "RS"]
    assert figura.layout.xaxis.title.text == "Quantidade de clubes"


def test_grafico_comparativo_regional_usa_metrica_e_rotulos_temporais():
    _, _, _, _, _, comparativo, _ = _dados_grafico()

    figura = painel.grafico_comparativo_regional(
        comparativo, "Média de pontos", None
    )

    assert list(figura.data[0].x) == [0.0, 6.0]
    assert list(figura.data[0].y) == ["Sul · 2024", "Sudeste · 2024"]
    assert "região e temporada" in figura.layout.title.text


def test_grafico_posicao_saldo_tem_um_ponto_por_campanha():
    *_, posicao_saldo = _dados_grafico()

    figura = painel.grafico_posicao_saldo_gols(posicao_saldo)

    assert len(figura.data[0].x) == len(posicao_saldo)
    assert list(figura.data[0].x) == [4, -4]
    assert list(figura.data[0].y) == [1, 2]
    assert figura.layout.yaxis.autorange == "reversed"
