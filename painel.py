"""Leitura somente leitura e visualizações dos resultados materializados em Gold."""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas.io.formats.style import Styler

BANCO_GOLD = "football.duckdb"
CAMINHO_BANCO = Path(__file__).resolve().parent / BANCO_GOLD
TODAS_TEMPORADAS = "Todas as temporadas"

TABELAS_GOLD = (
    "campeoes_por_temporada",
    "evolucao_pontuacao_campeao",
    "ranking_historico_times",
    "maiores_saldos_de_gols",
    "aproveitamento_por_time_temporada",
    "desempenho_por_regiao",
    "clubes_por_estado",
    "perfil_historico_dos_clubes",
    "comparativo_campanhas_por_regiao",
    "relacao_posicao_saldo_gols",
)

TABELAS_COM_TEMPORADA = (
    "campeoes_por_temporada",
    "ranking_historico_times",
    "maiores_saldos_de_gols",
    "aproveitamento_por_time_temporada",
    "desempenho_por_regiao",
    "comparativo_campanhas_por_regiao",
    "relacao_posicao_saldo_gols",
)

COLUNAS_ESPERADAS = {
    "campeoes_por_temporada": (
        "temporada",
        "campeao",
        "pontos",
        "vitorias",
        "empates",
        "derrotas",
        "gols",
        "gols_sofridos",
        "saldo_de_gols",
    ),
    "evolucao_pontuacao_campeao": ("temporada", "campeao", "pontos"),
    "ranking_historico_times": (
        "temporada",
        "posicao",
        "time",
        "pontos",
        "vitorias",
        "empates",
        "derrotas",
        "saldo_de_gols",
    ),
    "maiores_saldos_de_gols": (
        "temporada",
        "time",
        "posicao",
        "gols",
        "gols_sofridos",
        "saldo_de_gols",
    ),
    "aproveitamento_por_time_temporada": (
        "temporada",
        "time",
        "posicao",
        "pontos",
        "jogos_disputados",
        "aproveitamento_pct",
    ),
    "desempenho_por_regiao": (
        "temporada",
        "regiao",
        "times_participantes",
        "media_posicao",
        "media_pontos",
        "total_vitorias",
        "total_gols",
        "total_gols_sofridos",
    ),
    "clubes_por_estado": ("estado", "total_clubes", "regioes"),
    "perfil_historico_dos_clubes": (
        "time",
        "sigla",
        "nome_completo",
        "estado",
        "regiao",
        "temporadas_disputadas",
        "primeira_temporada",
        "ultima_temporada",
        "media_posicao",
        "total_vitorias",
    ),
    "comparativo_campanhas_por_regiao": (
        "temporada",
        "regiao",
        "total_times",
        "media_pontos",
        "media_vitorias",
        "media_gols",
        "media_saldo_de_gols",
    ),
    "relacao_posicao_saldo_gols": (
        "temporada",
        "time",
        "regiao",
        "posicao",
        "pontos",
        "saldo_de_gols",
        "gols",
        "gols_sofridos",
    ),
}

ROTULOS_COLUNAS = {
    "temporada": "Temporada",
    "campeao": "Campeão",
    "time": "Time",
    "sigla": "Sigla",
    "nome_completo": "Nome completo",
    "posicao": "Posição",
    "pontos": "Pontos",
    "vitorias": "Vitórias",
    "empates": "Empates",
    "derrotas": "Derrotas",
    "jogos_disputados": "Jogos disputados",
    "gols": "Gols",
    "gols_sofridos": "Gols sofridos",
    "saldo_de_gols": "Saldo de gols",
    "aproveitamento_pct": "Aproveitamento (%)",
    "regiao": "Região",
    "times_participantes": "Times participantes",
    "media_posicao": "Média da posição",
    "media_pontos": "Média de pontos",
    "total_vitorias": "Total de vitórias",
    "total_gols": "Total de gols",
    "total_gols_sofridos": "Total de gols sofridos",
    "total_times": "Total de times",
    "media_vitorias": "Média de vitórias",
    "media_gols": "Média de gols",
    "media_saldo_de_gols": "Média do saldo de gols",
    "estado": "Estado",
    "total_clubes": "Total de clubes",
    "regioes": "Regiões",
    "temporadas_disputadas": "Temporadas disputadas",
    "primeira_temporada": "Primeira temporada",
    "ultima_temporada": "Última temporada",
}

METRICAS_DESEMPENHO_REGIONAL = {
    "Times participantes": "times_participantes",
    "Média de posição": "media_posicao",
    "Média de pontos": "media_pontos",
    "Total de vitórias": "total_vitorias",
    "Total de gols": "total_gols",
    "Total de gols sofridos": "total_gols_sofridos",
}

METRICAS_COMPARATIVO_REGIONAL = {
    "Total de times": "total_times",
    "Média de pontos": "media_pontos",
    "Média de vitórias": "media_vitorias",
    "Média de gols": "media_gols",
    "Média do saldo de gols": "media_saldo_de_gols",
}

CORES = {
    "azul": "#2563EB",
    "verde": "#16A34A",
    "laranja": "#EA580C",
    "roxo": "#7C3AED",
    "cinza": "#64748B",
    "vermelho": "#DC2626",
    "grade": "#E2E8F0",
    "texto": "#172B4D",
}

CSS = """
<style>
:root {
  color-scheme: light;
  --football-ink: #172B4D;
  --football-muted: #64748B;
  --football-blue: #2563EB;
  --football-green: #16A34A;
  --football-orange: #EA580C;
  --football-purple: #7C3AED;
  --football-paper: #FFFFFF;
  --football-card: #FFFFFF;
  --football-line: #E2E8F0;
  --football-danger: #DC2626;
  --football-focus: #1D4ED8;
  --football-shadow: rgba(15, 23, 42, 0.04);
}
html {
  scroll-behavior: smooth;
}
.stApp {
  background: var(--football-paper);
  color: var(--football-ink);
}
.block-container {
  max-width: 1500px;
  padding-top: 1.8rem;
  padding-bottom: 3rem;
}
[data-testid="stHeader"] {
  background: rgba(255, 255, 255, 0.92);
}
header[data-testid="stHeader"] {
  box-shadow: none;
}

h1, h2, h3 {
  color: var(--football-ink);
  letter-spacing: -.02em;
}

.topbar-shell {
  display: grid;
  gap: 0.2rem;
  margin-bottom: 1.1rem;
}
.eyebrow {
  margin: 0;
  color: var(--football-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.topbar-shell h1 {
  margin: 0;
  font-size: clamp(1.9rem, 2.5vw, 2.55rem);
  font-weight: 700;
  line-height: 1.2;
}
.subtitle {
  margin: 0;
  color: var(--football-muted);
  font-size: 0.98rem;
  line-height: 1.5;
}

.auxiliar-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 0.8rem 1rem;
  margin: 0.6rem 0 1.4rem;
  border: 1px solid var(--football-line);
  border-radius: 12px;
  background: rgba(255,255,255,0.9);
  color: var(--football-muted);
  font-size: 0.77rem;
  font-weight: 600;
}

.metric-card {
  background: var(--football-card);
  border: 1px solid var(--football-line);
  border-radius: 16px;
  padding: 1.05rem 1rem 0.9rem;
  box-shadow: 0 8px 18px var(--football-shadow);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-height: 128px;
  margin-bottom: 1.25rem;
}
.metric-card.accent-blue { border-color: rgba(37, 99, 235, 0.18); }
.metric-card.accent-green { border-color: rgba(22, 163, 74, 0.18); }
.metric-card.accent-orange { border-color: rgba(234, 88, 12, 0.18); }
.metric-card.accent-purple { border-color: rgba(124, 58, 237, 0.18); }
.metric-label {
  color: var(--football-muted);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.metric-value {
  color: var(--football-ink);
  font-size: clamp(1.55rem, 2vw, 2rem);
  line-height: 1.1;
  letter-spacing: -0.04em;
}
.metric-meta {
  color: var(--football-muted);
  font-size: 0.8rem;
}

.section-head {
  margin: 1.6rem 0 0.8rem;
  padding-top: 0.4rem;
}
.section-head h2 {
  margin: 0 0 0.3rem;
  font-size: clamp(1.2rem, 1.7vw, 1.6rem);
  font-weight: 600;
  line-height: 1.3;
}
.section-head p {
  margin: 0;
  color: var(--football-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

[data-testid="stSelectbox"] label,
[data-testid="stButton"] label {
  color: var(--football-muted);
  font-weight: 600;
}

[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"] {
  border: 1px solid var(--football-line);
  border-radius: 14px;
  background: var(--football-card);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
}

.stButton > button {
  background: var(--football-blue);
  color: #FFFFFF;
  border: 1px solid var(--football-blue);
  border-radius: 10px;
  font-weight: 600;
  padding: 0.62rem 1.05rem;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.18);
}
.stButton > button:hover {
  background: var(--football-focus);
  border-color: var(--football-focus);
  color: #FFFFFF;
}
.stButton > button:focus-visible,
input:focus-visible,
[role="combobox"]:focus-visible {
  outline: 3px solid var(--football-focus) !important;
  outline-offset: 2px !important;
}

section[data-testid="stSidebar"] {
  border-right: 1px solid var(--football-line);
}

@media (max-width: 1024px) {
  .block-container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .auxiliar-bar {
    flex-direction: column;
    align-items: flex-start;
  }
}
@media (max-width: 760px) {
  .block-container {
    padding: 1rem 0.8rem 2rem;
  }
  .topbar-shell h1 { font-size: 1.7rem; }
  [data-testid="stDataFrame"],
  [data-testid="stPlotlyChart"] {
    border-radius: 10px;
  }
}
</style>
"""


def ler_tabelas_gold() -> dict[str, pd.DataFrame]:
    """Lê cada tabela Gold com SELECT * e fecha a conexão antes de retornar."""
    if not CAMINHO_BANCO.is_file():
        raise FileNotFoundError(f"Banco DuckDB não encontrado: {CAMINHO_BANCO}")

    dados: dict[str, pd.DataFrame] = {}
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        for tabela in TABELAS_GOLD:
            try:
                dados[tabela] = conexao.execute(
                    f'SELECT * FROM football.gold."{tabela}"'
                ).fetchdf()
            except duckdb.CatalogException:
                continue
        return dados


def temporadas_disponiveis(dados: dict[str, pd.DataFrame]) -> list[int]:
    temporadas: set[int] = set()
    for tabela in TABELAS_COM_TEMPORADA:
        dataframe = dados.get(tabela)
        if dataframe is not None and "temporada" in dataframe.columns:
            temporadas.update(
                int(valor) for valor in dataframe["temporada"].dropna().unique()
            )
    return sorted(temporadas, reverse=True)


def filtrar_temporada(
    dados: pd.DataFrame,
    temporada: int | None,
) -> pd.DataFrame:
    if temporada is None:
        return dados
    if "temporada" not in dados.columns:
        raise ValueError("A tabela não possui a coluna temporada.")
    return dados.loc[dados["temporada"] == temporada]


def validar_colunas(
    dados: dict[str, pd.DataFrame],
    tabela: str,
) -> tuple[bool, list[str]]:
    dataframe = dados.get(tabela)
    if dataframe is None:
        return False, []
    ausentes = [
        coluna
        for coluna in COLUNAS_ESPERADAS[tabela]
        if coluna not in dataframe.columns
    ]
    return not ausentes, ausentes


def formatar_numero(valor: float, casas: int = 0) -> str:
    if pd.isna(valor):
        return "—"
    return f"{valor:,.{casas}f}".translate(str.maketrans(".,", ",."))


def formatar_tabela(
    dados: pd.DataFrame,
    tabela: str,
) -> Styler:
    exibicao = dados.rename(columns=ROTULOS_COLUNAS)
    formatos: dict[str, object] = {}
    for coluna in dados.columns:
        rotulo = ROTULOS_COLUNAS.get(coluna, coluna)
        if coluna == "aproveitamento_pct":
            formatos[rotulo] = lambda valor: (
                "—" if pd.isna(valor) else f"{formatar_numero(valor, 2)}%"
            )
        elif coluna == "posicao":
            formatos[rotulo] = lambda valor: (
                "—" if pd.isna(valor) else f"{formatar_numero(valor)}º"
            )
        elif pd.api.types.is_numeric_dtype(dados[coluna]):
            casas = 2 if pd.api.types.is_float_dtype(dados[coluna]) else 0
            formatos[rotulo] = lambda valor, casas=casas: formatar_numero(valor, casas)
    estilizada = exibicao.style.format(formatos, na_rep="—")
    if tabela == "campeoes_por_temporada" and "Campeão" in exibicao.columns:
        estilizada = estilizada.set_properties(
            subset=["Campeão"],
            **{"font-weight": "700"},
        )
    if tabela == "ranking_historico_times" and "Posição" in exibicao.columns:
        estilizada = estilizada.set_properties(
            subset=["Posição"],
            **{"font-weight": "700"},
        )
    return estilizada.set_properties(
        **{"text-align": "right"},
        subset=[
            ROTULOS_COLUNAS[coluna]
            for coluna in dados.columns
            if pd.api.types.is_numeric_dtype(dados[coluna])
        ],
    )


def _layout(
    figura: go.Figure,
    *,
    altura: int = 440,
    margem_esquerda: int = 70,
) -> go.Figure:
    figura.update_layout(
        template="plotly_white",
        height=altura,
        margin={"l": margem_esquerda, "r": 30, "t": 70, "b": 55},
        font={"family": "Inter, Segoe UI, sans-serif", "color": CORES["texto"]},
        title={"font": {"size": 18}, "x": 0},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        separators=",.",
        hoverlabel={"bgcolor": "#FFFFFF", "font": {"color": CORES["texto"]}},
        xaxis={
            "gridcolor": CORES["grade"],
            "zerolinecolor": CORES["cinza"],
            "automargin": True,
        },
        yaxis={
            "gridcolor": CORES["grade"],
            "zerolinecolor": CORES["cinza"],
            "automargin": True,
        },
    )
    return figura


def grafico_pontuacao_campeoes(
    dados: pd.DataFrame,
    temporada: int | None,
) -> go.Figure:
    ordenados = dados.sort_values("temporada")
    figura = go.Figure()
    if temporada is None:
        figura.add_trace(
            go.Scatter(
                x=ordenados["temporada"],
                y=ordenados["pontos"],
                mode="lines+markers",
                name="Pontos do campeão",
                line={"color": CORES["azul"], "width": 2.5},
                marker={"color": CORES["azul"], "size": 9},
                customdata=ordenados[["campeao"]].to_numpy(),
                hovertemplate=(
                    "Temporada: %{x}<br>Campeão: %{customdata[0]}"
                    "<br>Pontos do campeão: %{y:,.0f}<extra></extra>"
                ),
            )
        )
        titulo = "02 · Pontuação dos campeões por temporada"
    else:
        linha = ordenados.iloc[0]
        figura.add_trace(
            go.Scatter(
                x=[linha["temporada"]],
                y=[linha["pontos"]],
                mode="markers",
                name="Pontos do campeão",
                marker={"color": CORES["azul"], "size": 12},
                customdata=[[linha["campeao"]]],
                hovertemplate=(
                    "Temporada: %{x}<br>Campeão: %{customdata[0]}"
                    "<br>Pontos do campeão: %{y:,.0f}<extra></extra>"
                ),
            )
        )
        titulo = f"02 · Pontuação do campeão em {temporada}"
    figura.update_layout(
        title=titulo,
        xaxis_title="Temporada",
        yaxis_title="Pontos do campeão",
        showlegend=False,
        xaxis={"type": "linear", "dtick": 1 if temporada is not None else None},
    )
    return _layout(figura)


def grafico_saldo_gols(
    dados: pd.DataFrame,
    temporada: int | None,
) -> go.Figure:
    ordenados = dados.copy()
    ordenados["rotulo_time"] = ordenados.apply(
        lambda linha: (
            linha["time"]
            if temporada is not None
            else f"{linha['time']} · {linha['temporada']}"
        ),
        axis=1,
    )
    cores = [
        CORES["vermelho"] if valor < 0 else CORES["azul"]
        for valor in ordenados["saldo_de_gols"]
    ]
    figura = go.Figure(
        go.Bar(
            x=ordenados["saldo_de_gols"],
            y=ordenados["rotulo_time"],
            orientation="h",
            marker_color=cores,
            customdata=ordenados[
                ["temporada", "time", "posicao", "gols", "gols_sofridos"]
            ].to_numpy(),
            hovertemplate=(
                "Time: %{customdata[1]}<br>Temporada: %{customdata[0]}"
                "<br>Posição: %{customdata[2]}º<br>Saldo de gols: %{x:,.0f}"
                "<br>Gols: %{customdata[3]:,.0f}"
                "<br>Gols sofridos: %{customdata[4]:,.0f}<extra></extra>"
            ),
            name="Saldo de gols",
        )
    )
    figura.update_layout(
        title="04 · Maiores saldos de gols",
        xaxis_title="Saldo de gols",
        yaxis_title="Time" if temporada is not None else "Time · Temporada",
        showlegend=False,
        height=max(500, min(9000, 25 * len(ordenados))),
        yaxis={
            "categoryorder": "array",
            "categoryarray": list(reversed(ordenados["rotulo_time"].tolist())),
            "gridcolor": CORES["grade"],
            "automargin": True,
        },
    )
    figura.add_vline(x=0, line={"color": CORES["cinza"], "width": 1})
    return _layout(
        figura, altura=max(500, min(9000, 25 * len(ordenados))), margem_esquerda=190
    )


def grafico_aproveitamento(
    dados: pd.DataFrame,
    temporada: int | None,
) -> go.Figure:
    ordenados = dados.copy()
    ordenados["rotulo_time"] = ordenados.apply(
        lambda linha: (
            linha["time"]
            if temporada is not None
            else f"{linha['time']} · {linha['temporada']}"
        ),
        axis=1,
    )
    figura = go.Figure(
        go.Bar(
            x=ordenados["aproveitamento_pct"],
            y=ordenados["rotulo_time"],
            orientation="h",
            marker_color=CORES["azul"],
            customdata=ordenados[
                ["temporada", "time", "posicao", "pontos", "jogos_disputados"]
            ].to_numpy(),
            hovertemplate=(
                "Time: %{customdata[1]}<br>Temporada: %{customdata[0]}"
                "<br>Posição: %{customdata[2]}º<br>Aproveitamento: %{x:.2f}%"
                "<br>Pontos: %{customdata[3]:,.0f}"
                "<br>Jogos disputados: %{customdata[4]:,.0f}<extra></extra>"
            ),
            name="Aproveitamento",
        )
    )
    altura = max(500, min(9000, 25 * len(ordenados)))
    figura.update_layout(
        title="05 · Aproveitamento dos times",
        xaxis_title="Aproveitamento (%)",
        yaxis_title="Time" if temporada is not None else "Time · Temporada",
        showlegend=False,
        height=altura,
        xaxis={"range": [0, 100], "ticksuffix": "%"},
        yaxis={
            "categoryorder": "array",
            "categoryarray": list(reversed(ordenados["rotulo_time"].tolist())),
            "gridcolor": CORES["grade"],
            "automargin": True,
        },
    )
    return _layout(figura, altura=altura, margem_esquerda=190)


def grafico_desempenho_regional(
    dados: pd.DataFrame,
    metrica: str,
    temporada: int | None,
) -> go.Figure:
    coluna = METRICAS_DESEMPENHO_REGIONAL[metrica]
    exibicao = dados.copy()
    exibicao["categoria"] = exibicao.apply(
        lambda linha: (
            linha["regiao"]
            if temporada is not None
            else f"{linha['regiao']} · {linha['temporada']}"
        ),
        axis=1,
    )
    exibicao = exibicao.sort_values(coluna, ascending=coluna == "media_posicao")
    custom = exibicao[["temporada", "regiao", coluna]].to_numpy()
    formato = (
        ",.0f"
        if coluna
        in {
            "times_participantes",
            "total_vitorias",
            "total_gols",
            "total_gols_sofridos",
        }
        else ",.2f"
    )
    figura = go.Figure(
        go.Bar(
            x=exibicao[coluna],
            y=exibicao["categoria"],
            orientation="h",
            marker_color=CORES["azul"],
            customdata=custom,
            hovertemplate=(
                "Região: %{customdata[1]}<br>Temporada: %{customdata[0]}"
                f"<br>{metrica}: %{{x:{formato}}}<extra></extra>"
            ),
            name=metrica,
        )
    )
    titulo = (
        f"06 · {metrica} por região"
        if temporada is None
        else f"06 · {metrica} por região · {temporada}"
    )
    if coluna == "media_posicao":
        figura.update_xaxes(autorange="reversed")
    altura = max(420, min(2800, 24 * len(exibicao)))
    figura.update_layout(
        title=titulo,
        xaxis_title=metrica,
        yaxis_title="Região" if temporada is not None else "Região · Temporada",
        showlegend=False,
        height=altura,
        yaxis={
            "categoryorder": "array",
            "categoryarray": list(reversed(exibicao["categoria"].tolist())),
            "gridcolor": CORES["grade"],
            "automargin": True,
        },
    )
    if coluna == "media_posicao":
        figura.update_layout(
            annotations=[
                {
                    "text": "Menor posição representa melhor colocação.",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 1,
                    "y": 1.12,
                    "showarrow": False,
                    "xanchor": "right",
                    "font": {"color": CORES["cinza"], "size": 12},
                }
            ]
        )
    return _layout(figura, altura=altura, margem_esquerda=190)


def grafico_clubes_por_estado(dados: pd.DataFrame) -> go.Figure:
    figura = px.bar(
        dados,
        x="total_clubes",
        y="estado",
        orientation="h",
        custom_data=["regioes"],
        labels={"total_clubes": "Quantidade de clubes", "estado": "Estado"},
        title="07 · Clubes cadastrados por estado",
        color_discrete_sequence=[CORES["azul"]],
    )
    figura.update_traces(
        name="Total de clubes",
        showlegend=False,
        hovertemplate=(
            "Estado: %{y}<br>Total de clubes: %{x:,.0f}"
            "<br>Regiões: %{customdata[0]}<extra></extra>"
        ),
    )
    figura.update_layout(
        yaxis={
            "categoryorder": "array",
            "categoryarray": list(reversed(dados["estado"].tolist())),
            "gridcolor": CORES["grade"],
            "automargin": True,
        },
        xaxis_title="Quantidade de clubes",
        yaxis_title="Estado",
        showlegend=False,
    )
    return _layout(figura, margem_esquerda=170)


def grafico_comparativo_regional(
    dados: pd.DataFrame,
    metrica: str,
    temporada: int | None,
) -> go.Figure:
    coluna = METRICAS_COMPARATIVO_REGIONAL[metrica]
    exibicao = dados.copy()
    exibicao["categoria"] = exibicao.apply(
        lambda linha: (
            linha["regiao"]
            if temporada is not None
            else f"{linha['regiao']} · {linha['temporada']}"
        ),
        axis=1,
    )
    exibicao = exibicao.sort_values(coluna)
    formato = ",.0f" if coluna == "total_times" else ",.2f"
    figura = go.Figure(
        go.Bar(
            x=exibicao[coluna],
            y=exibicao["categoria"],
            orientation="h",
            marker_color=CORES["laranja"],
            customdata=exibicao[["temporada", "regiao", "total_times"]].to_numpy(),
            hovertemplate=(
                "Região: %{customdata[1]}<br>Temporada: %{customdata[0]}"
                f"<br>{metrica}: %{{x:{formato}}}"
                "<br>Times participantes: %{customdata[2]:,.0f}<extra></extra>"
            ),
            name="Comparativo regional",
        )
    )
    titulo = (
        f"09 · {metrica} por região e temporada"
        if temporada is None
        else f"09 · {metrica} por região · {temporada}"
    )
    altura = max(420, min(2800, 24 * len(exibicao)))
    figura.update_layout(
        title=titulo,
        xaxis_title=metrica,
        yaxis_title="Região" if temporada is not None else "Região · Temporada",
        showlegend=False,
        height=altura,
        yaxis={
            "categoryorder": "array",
            "categoryarray": list(reversed(exibicao["categoria"].tolist())),
            "gridcolor": CORES["grade"],
            "automargin": True,
        },
    )
    return _layout(figura, altura=altura, margem_esquerda=190)


def grafico_posicao_saldo_gols(dados: pd.DataFrame) -> go.Figure:
    custom = dados[
        [
            "time",
            "temporada",
            "pontos",
            "saldo_de_gols",
            "gols",
            "gols_sofridos",
            "regiao",
        ]
    ].to_numpy()
    figura = go.Figure(
        go.Scatter(
            x=dados["saldo_de_gols"],
            y=dados["posicao"],
            mode="markers",
            name="Campanhas",
            marker={"color": CORES["azul"], "size": 9, "opacity": 0.75},
            customdata=custom,
            hovertemplate=(
                "Time: %{customdata[0]}<br>Temporada: %{customdata[1]}"
                "<br>Posição: %{y}º<br>Pontos: %{customdata[2]:,.0f}"
                "<br>Saldo de gols: %{customdata[3]:,.0f}"
                "<br>Gols: %{customdata[4]:,.0f}"
                "<br>Gols sofridos: %{customdata[5]:,.0f}"
                "<br>Região: %{customdata[6]}<extra></extra>"
            ),
        )
    )
    figura.update_layout(
        title="10 · Posição final × saldo de gols",
        xaxis_title="Saldo de gols",
        yaxis_title="Posição final (1º lugar no topo)",
        showlegend=False,
        yaxis={"autorange": "reversed", "dtick": 1},
    )
    return _layout(figura)
