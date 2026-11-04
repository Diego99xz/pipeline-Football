"""Aplicação Streamlit para explorar as consultas materializadas na camada Gold."""

import duckdb
import pandas as pd
import streamlit as st

import painel


@st.cache_data(show_spinner="Lendo as tabelas analíticas Gold...")
def carregar_dados() -> dict[str, pd.DataFrame]:
    return painel.ler_tabelas_gold()


def _selecionar_temporada(
    dados: dict[str, pd.DataFrame],
    *,
    key: str,
    label: str = "Temporada",
    incluir_todas: bool = True,
    padrao: int | None = None,
) -> int | None:
    temporadas = painel.temporadas_disponiveis(dados)
    if not temporadas:
        return None

    opcoes = [*temporadas]
    if incluir_todas:
        opcoes = [painel.TODAS_TEMPORADAS, *opcoes]

    if padrao is None:
        index = 0 if incluir_todas else 0
    else:
        index = opcoes.index(padrao) if padrao in opcoes else 0

    selecionada = st.selectbox(
        label,
        opcoes,
        index=index,
        key=key,
        format_func=lambda valor: (
            valor if valor == painel.TODAS_TEMPORADAS else str(valor)
        ),
        help=(
            "Aplica o filtro somente às análises que usam a coluna de temporada "
            "na tabela Gold."
        ),
    )
    return None if selecionada == painel.TODAS_TEMPORADAS else int(selecionada)


def _dados_para_visualizacao(
    dados: dict[str, pd.DataFrame],
    tabela: str,
    temporada: int | None,
) -> pd.DataFrame | None:
    dataframe = dados.get(tabela)
    if dataframe is None:
        st.error(
            f"A tabela `football.gold.{tabela}` não foi encontrada. "
            "Execute `uv run python -m pipeline.gold`."
        )
        return None

    colunas_validas, ausentes = painel.validar_colunas(dados, tabela)
    if not colunas_validas:
        st.error(
            f"A tabela `football.gold.{tabela}` não contém as colunas "
            f"esperadas: {', '.join(ausentes)}."
        )
        return None

    if tabela in painel.TABELAS_COM_TEMPORADA:
        dataframe = painel.filtrar_temporada(dataframe, temporada)
    if dataframe.empty:
        st.info(f"Não há registros em `football.gold.{tabela}` para a seleção atual.")
        return None
    return dataframe


def _tabela(dataframe: pd.DataFrame, nome: str) -> None:
    st.dataframe(
        painel.formatar_tabela(dataframe, nome),
        hide_index=True,
        width="stretch",
        key=f"tabela_{nome}",
    )


def _secao(titulo: str, descricao: str) -> None:
    st.markdown(
        f"""
        <div class="section-head">
            <h2>{titulo}</h2>
            <p>{descricao}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metricas_iniciais(dados: dict[str, pd.DataFrame]) -> list[dict[str, str]]:
    metricas: list[dict[str, str]] = []

    campeoes = dados.get("campeoes_por_temporada")
    if campeoes is not None and not campeoes.empty:
        ultimo = campeoes.sort_values("temporada").iloc[-1]
        metricas.append(
            {
                "label": "Campeão atual",
                "value": str(ultimo["campeao"]),
                "meta": f"{int(ultimo['temporada'])} · {int(ultimo['pontos'])} pts",
                "tone": "accent-blue",
            }
        )

        media_pontos = float(campeoes["pontos"].mean())
        metricas.append(
            {
                "label": "Média de pontos",
                "value": f"{media_pontos:.1f}",
                "meta": "Média dos campeões",
                "tone": "accent-green",
            }
        )

    ranking = dados.get("ranking_historico_times")
    if ranking is not None and not ranking.empty:
        melhor_saldo = int(ranking["saldo_de_gols"].max())
        metricas.append(
            {
                "label": "Maior saldo",
                "value": f"{melhor_saldo:+d}",
                "meta": "Campanha histórica",
                "tone": "accent-orange",
            }
        )

    clubes = dados.get("clubes_por_estado")
    if clubes is not None and not clubes.empty:
        total = int(clubes["total_clubes"].sum())
        estado_lider = clubes.sort_values("total_clubes", ascending=False).iloc[0]
        metricas.append(
            {
                "label": "Clubes por estado",
                "value": str(total),
                "meta": f"{estado_lider['estado']} lidera",
                "tone": "accent-purple",
            }
        )

    return metricas[:4]


def _consultar_campeoes(
    dados: dict[str, pd.DataFrame],
) -> None:
    _secao(
        "Campeões e evolução histórica",
        "Campeões por edição e pontuação registrada para cada título.",
    )
    temporada = _selecionar_temporada(dados, key="temporada_campeoes")
    campeoes = _dados_para_visualizacao(dados, "campeoes_por_temporada", temporada)
    evolucao = _dados_para_visualizacao(dados, "evolucao_pontuacao_campeao", None)
    coluna_tabela, coluna_grafico = st.columns([1.15, 1])
    with coluna_tabela:
        st.subheader("01 · Campeões por temporada")
        if campeoes is not None:
            _tabela(campeoes, "campeoes_por_temporada")
    with coluna_grafico:
        st.subheader("02 · Pontuação dos campeões por temporada")
        if evolucao is not None:
            st.plotly_chart(
                painel.grafico_pontuacao_campeoes(evolucao, None),
                width="stretch",
                key="grafico_evolucao_pontuacao_campeao",
            )


def _consultar_classificacao(
    dados: dict[str, pd.DataFrame],
) -> None:
    _secao(
        "Classificação e desempenho dos times",
        "Classificações e indicadores por campanha, preservando a temporada no histórico.",
    )
    temporadas = painel.temporadas_disponiveis(dados)
    temporada_padrao = temporadas[0] if temporadas else None

    temporada_ranking = _selecionar_temporada(
        dados,
        key="temporada_classificacao_ranking",
        incluir_todas=False,
        padrao=temporada_padrao,
    )
    ranking = _dados_para_visualizacao(dados, "ranking_historico_times", temporada_ranking)
    if ranking is not None:
        st.subheader("03 · Ranking dos times")
        _tabela(ranking, "ranking_historico_times")

    temporada_saldos = _selecionar_temporada(
        dados,
        key="temporada_classificacao_saldos",
        incluir_todas=False,
        padrao=temporada_padrao,
    )
    saldos = _dados_para_visualizacao(dados, "maiores_saldos_de_gols", temporada_saldos)
    if saldos is not None:
        st.subheader("04 · Maiores saldos de gols")
        st.plotly_chart(
            painel.grafico_saldo_gols(saldos, temporada_saldos),
            width="stretch",
            key="grafico_maiores_saldos_de_gols",
        )

    temporada_aproveitamento = _selecionar_temporada(
        dados,
        key="temporada_classificacao_aproveitamento",
        incluir_todas=False,
        padrao=temporada_padrao,
    )
    aproveitamento = _dados_para_visualizacao(
        dados, "aproveitamento_por_time_temporada", temporada_aproveitamento
    )
    if aproveitamento is not None:
        st.subheader("05 · Aproveitamento dos times")
        st.plotly_chart(
            painel.grafico_aproveitamento(aproveitamento, temporada_aproveitamento),
            width="stretch",
            key="grafico_aproveitamento_por_time_temporada",
        )


def _consultar_regioes(
    dados: dict[str, pd.DataFrame],
) -> None:
    _secao(
        "Desempenho regional",
        "Indicadores agregados por região. Com todas as temporadas, cada categoria identifica sua edição.",
    )
    temporadas = painel.temporadas_disponiveis(dados)
    temporada_padrao = temporadas[0] if temporadas else None

    temporada_regional = _selecionar_temporada(
        dados,
        key="temporada_desempenho_regional_06",
        incluir_todas=False,
        padrao=temporada_padrao,
    )
    regional = _dados_para_visualizacao(dados, "desempenho_por_regiao", temporada_regional)
    if regional is not None:
        st.subheader("06 · Desempenho agregado por região")
        metrica = st.selectbox(
            "Métrica da query 06",
            list(painel.METRICAS_DESEMPENHO_REGIONAL),
            key="metrica_desempenho_regional",
        )
        st.plotly_chart(
            painel.grafico_desempenho_regional(regional, metrica, temporada_regional),
            width="stretch",
            key="grafico_desempenho_por_regiao",
        )

    temporada_comparativo = _selecionar_temporada(
        dados,
        key="temporada_regional_09",
        incluir_todas=True,
        padrao=temporada_padrao,
    )
    comparativo = _dados_para_visualizacao(
        dados, "comparativo_campanhas_por_regiao", temporada_comparativo
    )
    if comparativo is not None:
        st.subheader("09 · Comparativo regional de campanhas")
        metrica_comparativo = st.selectbox(
            "Métrica da query 09",
            list(painel.METRICAS_COMPARATIVO_REGIONAL),
            key="metrica_comparativo_regional",
        )
        st.plotly_chart(
            painel.grafico_comparativo_regional(
                comparativo,
                metrica_comparativo,
                temporada_comparativo,
            ),
            width="stretch",
            key="grafico_comparativo_campanhas_por_regiao",
        )


def _consultar_clubes(dados: dict[str, pd.DataFrame]) -> None:
    _secao(
        "Perfil dos clubes",
        "Cadastro por estado e histórico consolidado dos clubes, sem filtro de temporada.",
    )
    clubes_estado = _dados_para_visualizacao(dados, "clubes_por_estado", temporada=None)
    if clubes_estado is not None:
        st.subheader("07 · Clubes cadastrados por estado")
        st.plotly_chart(
            painel.grafico_clubes_por_estado(clubes_estado),
            width="stretch",
            key="grafico_clubes_por_estado",
        )

    perfil = _dados_para_visualizacao(
        dados, "perfil_historico_dos_clubes", temporada=None
    )
    if perfil is not None:
        st.subheader("08 · Perfil histórico dos clubes")
        _tabela(perfil, "perfil_historico_dos_clubes")


def _consultar_posicao_saldo(
    dados: dict[str, pd.DataFrame],
) -> None:
    _secao(
        "Relação entre posição e saldo de gols",
        "Cada ponto representa uma campanha. Posições menores indicam melhor colocação; o gráfico não implica causalidade.",
    )
    temporadas = painel.temporadas_disponiveis(dados)
    temporada_padrao = temporadas[0] if temporadas else None
    temporada = _selecionar_temporada(
        dados,
        key="temporada_posicao_saldo",
        incluir_todas=True,
        padrao=temporada_padrao,
    )
    dataframe = _dados_para_visualizacao(dados, "relacao_posicao_saldo_gols", temporada)
    if dataframe is not None:
        st.subheader("10 · Posição final × saldo de gols")
        st.plotly_chart(
            painel.grafico_posicao_saldo_gols(dataframe),
            width="stretch",
            key="grafico_relacao_posicao_saldo_gols",
        )


def main() -> None:
    st.set_page_config(
        page_title="Brasileirão · Dashboard histórico",
        page_icon="⚽",
        layout="wide",
    )
    st.markdown(painel.CSS, unsafe_allow_html=True)

    header_col, action_col = st.columns([5, 1.1])
    with header_col:
        st.markdown(
            """
            <div class="topbar-shell">
                <p class="eyebrow">Análise histórica</p>
                <h1>Brasileirão · Dashboard histórico</h1>
                <p class="subtitle">Indicadores históricos do Campeonato Brasileiro: campeões, campanhas, desempenho regional e perfil dos clubes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with action_col:
        recarregar = st.button("Recarregar dados", use_container_width=True)
    if recarregar:
        carregar_dados.clear()
        st.cache_data.clear()
        st.session_state["releitura_solicitada"] = True
        st.rerun()

    if not painel.CAMINHO_BANCO.is_file():
        st.error(
            f"Banco não encontrado: `{painel.CAMINHO_BANCO.name}`. "
            "Execute `uv run python -m pipeline.gold` após preparar as camadas."
        )
        st.stop()

    try:
        dados = carregar_dados()
    except (duckdb.Error, OSError, ValueError) as erro:
        st.error(f"Não foi possível ler os dados Gold: {erro}")
        st.stop()

    if st.session_state.pop("releitura_solicitada", False):
        st.success("Os dados Gold foram lidos novamente com sucesso.")

    ausentes = [tabela for tabela in painel.TABELAS_GOLD if tabela not in dados]
    if ausentes:
        nomes = ", ".join(f"`football.gold.{tabela}`" for tabela in ausentes)
        st.warning(
            f"Tabelas Gold ausentes: {nomes}. Execute `uv run python -m pipeline.gold`."
        )

    temporadas = painel.temporadas_disponiveis(dados)
    if not temporadas:
        st.error(
            "Não há temporadas disponíveis nas tabelas Gold. "
            "Verifique a materialização com `uv run python -m pipeline.gold`."
        )
        st.stop()

    st.markdown(
        """
        <div class="auxiliar-bar">
            <span>As análises por temporada usam filtros locais dentro de cada seção.</span>
            <span>As consultas 07 e 08 permanecem consolidadas e independentes do ano.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metricas = _metricas_iniciais(dados)
    colunas = st.columns(4)
    for coluna, metrica in zip(colunas, metricas):
        with coluna:
            st.markdown(
                f"""
                <div class="metric-card {metrica['tone']}">
                    <span class="metric-label">{metrica['label']}</span>
                    <strong class="metric-value">{metrica['value']}</strong>
                    <small class="metric-meta">{metrica['meta']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _consultar_campeoes(dados)
    _consultar_classificacao(dados)
    _consultar_regioes(dados)
    _consultar_clubes(dados)
    _consultar_posicao_saldo(dados)


if __name__ == "__main__":
    main()
