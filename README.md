# Football — Pipeline de Dados do Campeonato Brasileiro

Projeto de Engenharia de Dados para ingestão, tipagem e análise de dados
históricos do Campeonato Brasileiro. O fluxo organiza os dados em camadas
Bronze, Silver e Gold usando DuckDB; consultas SQL materializam os resultados
analíticos consumidos por um dashboard interativo em Streamlit e Plotly.

O repositório também contém testes automatizados com pytest e documentação
técnica gerada localmente pelo MkDocs. O pipeline é executado por etapas
independentes; não há orquestrador central nem atualização automática.

## Índice

- [Objetivos e estado atual](#objetivos-e-estado-atual)
- [Dados de origem](#dados-de-origem)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Instalação](#instalação)
- [Executar o pipeline](#executar-o-pipeline)
- [Consultas Gold](#consultas-gold)
- [Dashboard](#dashboard)
- [Testes e qualidade](#testes-e-qualidade)
- [Documentação MkDocs](#documentação-mkdocs)
- [Git, segurança e CI](#git-segurança-e-ci)
- [Limitações e próximos passos](#limitações-e-próximos-passos)
- [Referências](#referências)

## Objetivos e estado atual

O projeto implementa:

- pipeline modular de ingestão, transformação e materialização analítica;
- organização Bronze/Silver/Gold em um banco DuckDB local;
- consultas SQL para campanhas, campeões, clubes e desempenho regional;
- dashboard Streamlit com gráficos Plotly e filtros por temporada onde
  aplicável;
- testes com dados inventados e bancos DuckDB temporários;
- documentação técnica em Markdown e configuração MkDocs.

Não há download automático dos dados, execução agendada, integração contínua
configurada ou publicação do site de documentação. O fluxo de atualização dos
dados é iniciado manualmente por comandos.

## Dados de origem

A fonte de referência informada para o conjunto é o
[Kaggle — Brasileirão Série A 2006–2022](https://www.kaggle.com/datasets/lucasyukioimafuko/brasileirao-serie-a-2006-2022).
O repositório contém os arquivos `bronze/brasileirao.csv` e
`bronze/times.csv`; a ingestão espera esses nomes e os cabeçalhos abaixo:

| Arquivo | Colunas utilizadas |
|---|---|
| `brasileirao.csv` | `temporada`, `posicao`, `time`, `pontos`, `jogos_disputados`, `vitorias`, `empates`, `derrotas`, `gols`, `gols_sofridos`, `saldo_de_gols` |
| `times.csv` | `time`, `sigla`, `nome_completo`, `ano_fundacao`, `estadio`, `cidade`, `estado`, `regiao` |

Para obter uma cópia externa, baixe o conjunto na página do Kaggle e confira
os nomes, cabeçalhos, tipos e codificação dos CSVs antes de substituir os
arquivos locais. A ingestão não baixa nem reconcilia arquivos.

**Limitação de período:** embora a página do conjunto indique 2006–2022, os
CSV versionados neste repositório contêm temporadas de 2003 a 2024. Não foi
possível confirmar apenas pelo conteúdo local que esses arquivos são uma
cópia sem modificações da versão publicada no Kaggle. Ao atualizar a origem,
verifique a procedência e o período efetivo dos dados.

## Tecnologias

| Tecnologia | Finalidade | Estado |
|---|---|---|
| Python 3.13+ | Implementação do pipeline, painel e testes | Requisito declarado em `pyproject.toml` |
| `uv` | Ambiente, dependências e execução | Usado pelo projeto; `uv.lock` versionado |
| DuckDB | Armazenamento e consultas analíticas locais | Usado pelo pipeline e painel |
| SQL | Definição das consultas Gold | Dez arquivos em `sql/gold/` |
| pandas | Leitura dos CSVs e manipulação/formatamento no painel | Dependência de execução |
| Streamlit | Interface interativa | Dependência de execução |
| Plotly | Gráficos do dashboard | Dependência de execução |
| pytest / pytest-cov | Testes e cobertura de código | Dependências de desenvolvimento configuradas |
| Ruff | Lint | Dependência de desenvolvimento; não há regras personalizadas declaradas |
| MkDocs | Site local da documentação | Dependência de desenvolvimento e configuração presentes |
| Git / GitHub | Versionamento e hospedagem do repositório | Repositório remoto configurado |
| GitHub Actions | Integração contínua | Não há workflow configurado |
| MCP DuckDB | Integração auxiliar com ferramentas no VS Code | Configuração `football-duckdb` em `.vscode/mcp.json`; não é requisito do pipeline |

DuckDB é o mecanismo de banco e execução analítica. MCP é um protocolo para
integrar ferramentas a recursos; não substitui DuckDB, não define regras de
negócio e não executa as transformações do pipeline. A configuração existente
usa `mcp-server-duckdb` em modo somente leitura e é auxiliar ao VS Code. Os
comandos de ingestão, transformação, Gold e dashboard não dependem desse
servidor.

O [MotherDuck MCP Server](https://github.com/motherduckdb/mcp-server-motherduck)
não é o servidor configurado neste repositório.

## Arquitetura

```text
CSV de origem
    │
    ▼
pipeline.ingestao ──► football.bronze
                           │
                           ▼
                 pipeline.transformacao
                           │
                           ▼
                    football.silver
                           │
             sql/gold/*.sql + pipeline.gold
                           │
                           ▼
                     football.gold
                           │
                           ▼
              painel.py ──► app.py
       leitura e gráficos     Streamlit
```

### Bronze

`pipeline/ingestao.py` lê os dois CSVs usando pandas com todas as colunas como
texto e grava `football.bronze.brasileirao` e `football.bronze.times`. A
gravação substitui as tabelas; não acumula uma cópia a cada execução. Arquivos
ausentes ou erros de leitura/gravação fazem a etapa retornar código de erro.

### Silver

`pipeline/transformacao.py` verifica as tabelas Bronze e recria as tabelas
correspondentes em `football.silver`. Converte explicitamente os campos
numéricos para `BIGINT`, mantendo os campos descritivos em `VARCHAR`.
Preserva linhas, duplicatas e nulos; valores que não podem ser convertidos
causam erro. Esta etapa não faz JOIN nem calcula regras analíticas.

### Gold

`pipeline/gold.py` valida e executa, em ordem alfabética, os arquivos SQL que
seguem o padrão `NN_nome.sql`. Cada consulta materializa uma tabela no schema
`football.gold`. O schema é recriado dentro de uma transação: consultas
inválidas ou tabelas vazias provocam rollback para preservar a materialização
anterior.

### Dashboard

`painel.py` abre `football.duckdb` em modo somente leitura, lê tabelas Gold,
formata tabelas e constrói figuras Plotly. `app.py` monta a interface
Streamlit, aplica filtros locais e apresenta erros quando dados necessários
estão ausentes. O painel não dispara o pipeline.

## Estrutura do repositório

```text
Football/
├── .vscode/
│   └── mcp.json                 # Servidor auxiliar DuckDB para VS Code
├── bronze/
│   ├── brasileirao.csv          # Dados de campanhas versionados
│   └── times.csv                # Cadastro de clubes versionado
├── docs/                        # Páginas-fonte do MkDocs
│   ├── dados/
│   └── pipeline/
├── pipeline/
│   ├── db.py                    # Conexão, schema e gravação DuckDB
│   ├── ingestao.py              # CSV → Bronze
│   ├── transformacao.py         # Bronze → Silver
│   └── gold.py                  # SQL → tabelas Gold
├── sql/gold/                    # Dez consultas analíticas SQL
├── test/                        # Testes pytest
├── app.py                       # Interface Streamlit
├── dashboard.css                # Estilo do protótipo HTML
├── index.html                   # Protótipo visual estático para GitHub Pages
├── dashboard.js                # Filtros demonstrativos do protótipo
├── mkdocs.yml                   # Configuração da documentação
├── painel.py                    # Leitura Gold, formatação e gráficos
├── pyproject.toml               # Dependências e configuração pytest/coverage
├── ui.py                        # Entrada opcional da DuckDB Local UI
└── uv.lock                      # Lockfile de dependências
```

`football.duckdb` é um arquivo de banco local ignorado pelo Git, criado e
preenchido pelo pipeline. A página está disponível no
[GitHub Pages](https://diego99xz.github.io/pipeline-Football/) e é servida a
partir de `index.html`: trata-se de uma demonstração estática com dados de
amostra somente para visualização. Os filtros são interativos, mas o site não
lê o DuckDB, não atualiza os dados e não substitui o app Streamlit.

Não existe `main.py`: as etapas do pipeline são pontos de entrada
independentes executados com `python -m`.

## Instalação

### Pré-requisitos

- Python 3.13 ou superior.
- [`uv`](https://docs.astral.sh/uv/).
- Os CSVs de entrada em `bronze/` (já presentes no repositório; confira a
  [origem](#dados-de-origem) ao substituí-los).

Clone o repositório e sincronize o ambiente:

```bash
git clone https://github.com/Diego99xz/pipeline-Football.git
cd pipeline-Football
uv sync
```

## Executar o pipeline

Execute as etapas nesta ordem:

```bash
uv run python -m pipeline.ingestao
uv run python -m pipeline.transformacao
uv run python -m pipeline.gold
```

1. **Ingestão:** requer `bronze/brasileirao.csv` e `bronze/times.csv` e grava
   as tabelas Bronze com valores textuais.
2. **Transformação:** requer ambas as tabelas Bronze e recria Silver com os
   tipos definidos no código.
3. **Gold:** requer as tabelas Silver e os arquivos `sql/gold/*.sql`; valida
   nomes e executa todas as consultas dentro de uma transação.

O pipeline não é iniciado automaticamente pelo Streamlit, MkDocs nem pelos
testes. Erros de entrada e conversão são informados pela etapa correspondente.

## Consultas Gold

Os arquivos SQL são a fonte das regras e fórmulas analíticas. Todos leem de
Silver; as consultas que usam cadastro de clube fazem JOIN com
`football.silver.times`.

| Nº | Arquivo SQL | Objetivo e grão | Entrada(s) → saída Gold |
|---:|---|---|---|
| 01 | `01_campeoes_por_temporada.sql` | Campeão e desempenho; uma temporada | `silver.brasileirao` → `campeoes_por_temporada` |
| 02 | `02_evolucao_pontuacao_campeao.sql` | Pontuação do campeão no histórico; uma temporada/campeão | `silver.brasileirao` → `evolucao_pontuacao_campeao` |
| 03 | `03_ranking_historico_times.sql` | Campanhas ordenadas por temporada e posição; um time/temporada | `silver.brasileirao` → `ranking_historico_times` |
| 04 | `04_maiores_saldos_de_gols.sql` | Campanhas ordenadas por saldo; um time/temporada | `silver.brasileirao` → `maiores_saldos_de_gols` |
| 05 | `05_aproveitamento_por_time_temporada.sql` | Aproveitamento de pontos; um time/temporada | `silver.brasileirao` → `aproveitamento_por_time_temporada` |
| 06 | `06_desempenho_por_regiao.sql` | Métricas agregadas regionais; uma região/temporada | `silver.brasileirao`, `silver.times` → `desempenho_por_regiao` |
| 07 | `07_clubes_por_estado.sql` | Clubes e regiões por estado; um estado | `silver.times` → `clubes_por_estado` |
| 08 | `08_perfil_historico_dos_clubes.sql` | Participações e desempenho histórico; um clube | `silver.brasileirao`, `silver.times` → `perfil_historico_dos_clubes` |
| 09 | `09_comparativo_campanhas_por_regiao.sql` | Médias regionais por temporada; uma região/temporada | `silver.brasileirao`, `silver.times` → `comparativo_campanhas_por_regiao` |
| 10 | `10_relacao_posicao_saldo_gols.sql` | Campanhas para comparar posição e saldo; um time/temporada | `silver.brasileirao`, `silver.times` (LEFT JOIN) → `relacao_posicao_saldo_gols` |

A Query 05 calcula no SQL o percentual de pontos sobre o máximo possível
(três pontos por jogo). Consulte os arquivos em `sql/gold/` para a definição
completa das expressões e ordenações.

## Dashboard

Depois de executar o pipeline até Gold:

```bash
uv run streamlit run app.py
```

O Streamlit disponibiliza o endereço local no terminal. `painel.py` contém a
leitura e os construtores de gráficos; `app.py` contém a apresentação. A
interface inclui quatro cartões de indicadores e análises numeradas de 01 a
10. Ranking (03) aparece em tabela; outras consultas usam gráficos ou tabelas
conforme a implementação.

Os filtros de temporada são locais: a Query 01 é filtrável; a Query 02 mostra
a evolução histórica sem filtro. As Queries 03, 04, 05 e 06 iniciam na
temporada mais recente, sem opção “Todas as temporadas”; as Queries 09 e 10
permitem todas as temporadas. As Queries 07 e 08 são consolidadas e não têm
filtro. O botão “Recarregar dados” limpa o cache e relê Gold.

O banco precisa existir e conter as tabelas Gold. O app exibe erros ou avisos
para banco, tabelas, colunas ou temporadas ausentes; não executa a
materialização por conta própria.

## Testes e qualidade

### Testes automatizados

Execute:

```bash
uv run pytest --cov
```

O projeto configura `test/` como diretório de testes e uma cobertura mínima
global de 60%. A medição inclui `pipeline/` e `painel.py`, excluindo `app.py`,
`ui.py` e a pasta de testes. Os testes cobrem banco, ingestão, transformação,
materialização Gold e funções do painel.

Os cenários usam dados inventados e bancos DuckDB temporários; não exigem que
o pipeline tenha sido executado nem usam o banco real como fonte de
resultados esperados. `app.py` não está na cobertura e deve ser validado
visualmente no navegador. Testes automatizados não substituem a validação da
qualidade ou procedência dos CSVs reais.

### Ruff e estilo

Ruff está instalado como dependência de desenvolvimento. Não há regras
específicas ou scripts de formatação configurados no `pyproject.toml`. O
comando abaixo verifica os testes:

```bash
uv run ruff check test
```

O código deve manter nomes claros, funções com responsabilidades definidas e
estilo legível. Não há validação PEP 8 independente configurada.

### Scripts de validação

Não há scripts dedicados de validação de dados ou automação além das etapas
do pipeline, dos testes pytest, do comando Ruff e do build MkDocs.

## Documentação MkDocs

As páginas-fonte ficam em `docs/`, com navegação organizada por arquitetura,
instalação, pipeline, camadas, consultas, dashboard, testes e referências.
`mkdocs.yml` usa o tema padrão `mkdocs`, locale `pt_BR`, alternância de cores,
realce de Python/SQL/Bash/TOML e extensões de tabelas, blocos de código e
índice de títulos. O tema Material não está instalado.

Para visualizar localmente ou gerar o site estático:

```bash
uv run mkdocs serve
uv run mkdocs build --strict
```

O site gerado vai para `site/`, ignorado pelo Git. Há configuração e build
local; não há publicação configurada.

## Git, segurança e CI

### Branches e commits

Como convenção recomendada para novas tarefas, use uma branch por mudança no
formato `<ID_DA_TAREFA>-<titulo-da-tarefa>`, com título curto separado por
hífens, por exemplo `123-adicionar-dashboard`. O exemplo é ilustrativo, não
representa uma tarefa real. Faça commits descritivos e revise as alterações
antes de integrá-las; use pull requests quando esse fluxo estiver disponível.
Essa convenção não é imposta por configuração do repositório.

### `.gitignore` e credenciais

O `.gitignore` atual cobre ambientes virtuais, caches Python/pytest/Ruff,
arquivos de cobertura, a saída `site/`, bancos DuckDB locais, arquivos `.env`,
chaves privadas e metadados comuns do sistema operacional. Os CSVs da pasta
`bronze/` são versionados; confira a licença e a política de compartilhamento
dos dados antes de adicionar outros arquivos.

`.gitignore` não remove arquivos que já estão versionados. Ele também não
substitui gestão segura de segredos: não inclua senhas, tokens ou credenciais
em commits e, se um segredo for exposto, revogue-o.

A configuração `.vscode/mcp.json` registra um servidor local `football-duckdb`
em modo somente leitura. Verifique cuidadosamente mudanças nesse arquivo
antes de compartilhá-las; o arquivo de configuração não é necessário para
executar o pipeline.

### Integração contínua

Não há arquivos em `.github/workflows/`; GitHub Actions não executa testes,
lint ou build automaticamente neste repositório. Automatizar essas
verificações é uma melhoria futura, não uma capacidade atual.

## Limitações e próximos passos

- Confirmar e documentar a procedência dos CSVs e a diferença entre o período
  anunciado no Kaggle (2006–2022) e o período observado nos arquivos locais
  (2003–2024).
- Adicionar workflows GitHub Actions para testes, Ruff e build da
  documentação.
- Validar manualmente a interface Streamlit em diferentes larguras de tela.
- Avaliar o uso de MkDocs Material caso seja desejado um tema diferente; o
  projeto atualmente usa o tema padrão.

Não há atualização em tempo real, ingestão incremental, orquestração
agendada nem execução em nuvem configuradas.

## Referências

- [Dataset Brasileirão Série A 2006–2022 — Kaggle](https://www.kaggle.com/datasets/lucasyukioimafuko/brasileirao-serie-a-2006-2022)
- [Repositório Football no GitHub](https://github.com/Diego99xz/pipeline-Football)
- [Python](https://docs.python.org/3/)
- [uv](https://docs.astral.sh/uv/)
- [DuckDB](https://duckdb.org/docs/)
- [Streamlit](https://docs.streamlit.io/)
- [Plotly para Python](https://plotly.com/python/)
- [pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Ruff](https://docs.astral.sh/ruff/)
- [MkDocs](https://www.mkdocs.org/)
- [GitHub Actions](https://docs.github.com/actions) — recurso disponível, mas não configurado neste repositório.
- [MotherDuck MCP Server](https://github.com/motherduckdb/mcp-server-motherduck) — referência não utilizada; a configuração local atual usa `mcp-server-duckdb`.
- [Gerador de `.gitignore` da Toptal](https://www.toptal.com/developers/gitignore)
