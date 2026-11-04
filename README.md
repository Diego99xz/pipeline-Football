# ⚽ Football — Pipeline de Engenharia de Dados

**Análise histórica do Campeonato Brasileiro utilizando Python, DuckDB, SQL e Streamlit.**

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualização-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

## Sobre o projeto

O **Football** é um projeto de Engenharia de Dados desenvolvido para explorar o histórico do Campeonato Brasileiro por meio de um pipeline modular de dados.

A solução utiliza a arquitetura Medallion, organizando o processamento em três camadas:

- **Bronze:** ingestão dos arquivos CSV originais.
- **Silver:** transformação e tipagem dos dados.
- **Gold:** consultas SQL que produzem tabelas analíticas para consumo.

Os resultados são armazenados localmente no DuckDB e disponibilizados em um dashboard interativo desenvolvido com Streamlit e Plotly.

O projeto também contempla testes automatizados com pytest, análise estática com Ruff e documentação técnica com MkDocs.

> O pipeline é executado manualmente por etapas independentes. Não há orquestrador ou atualização automática configurados.

## Demonstração

**Dashboard estático:** [Visualizar no GitHub Pages](https://diego99xz.github.io/pipeline-Football/index.html)

A demonstração publicada apresenta dados de amostra para ilustrar a interface e as possibilidades de visualização. Ela não possui conexão com o DuckDB nem com o pipeline.

O dashboard interativo conectado aos dados locais pode ser executado com Streamlit, conforme as instruções deste README.

## Arquitetura

O projeto utiliza a arquitetura Medallion para separar ingestão, transformação e disponibilização analítica.


### Bronze — Ingestão

Responsável por carregar os arquivos CSV para o banco DuckDB.

- Leitura dos arquivos utilizando pandas.
- Colunas inicialmente tratadas como texto.
- Gravação das tabelas no schema `football.bronze`.
- Substituição das tabelas a cada execução.

Tabelas:
- `football.bronze.brasileirao`
- `football.bronze.times`

Módulo: `pipeline/ingestao.py`

### Silver — Transformação

Responsável por converter os dados da camada Bronze para os tipos definidos pelo projeto.

- Verificação das tabelas de origem.
- Conversão explícita dos campos numéricos para `BIGINT`.
- Manutenção dos campos descritivos como `VARCHAR`.
- Materialização das tabelas no schema `football.silver`.

Tabelas:
- `football.silver.brasileirao`
- `football.silver.times`

Módulo: `pipeline/transformacao.py`

### Gold — Análises analíticas

Responsável por executar consultas SQL e materializar os resultados analíticos no schema `football.gold`.

- Execução dos arquivos SQL em ordem alfabética.
- Validação dos arquivos conforme o padrão `NN_nome.sql`.
- Materialização das consultas em tabelas independentes.
- Execução transacional para proteger a materialização anterior em caso de falha.

Módulo: `pipeline/gold.py`

As consultas Gold são a fonte das regras e métricas analíticas do projeto.

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python 3.13+ | Desenvolvimento do pipeline |
| uv | Gerenciamento de ambiente e dependências |
| pandas | Leitura dos arquivos CSV |
| DuckDB | Banco de dados analítico local |
| SQL | Transformações e consultas analíticas |
| Streamlit | Interface do dashboard |
| Plotly | Visualizações interativas |
| pytest | Testes automatizados |
| pytest-cov | Análise de cobertura |
| Ruff | Análise estática de código |
| MkDocs | Documentação técnica |
| Git / GitHub | Versionamento |

## Estrutura do projeto

```text
Football/
│
├── .vscode/
│   └── mcp.json
│
├── bronze/
│   ├── brasileirao.csv
│   └── times.csv
│
├── docs/
│   ├── dados/
│   └── pipeline/
│
├── pipeline/
│   ├── db.py
│   ├── ingestao.py
│   ├── transformacao.py
│   └── gold.py
│
├── sql/
│   └── gold/
│       ├── 01_campeoes_por_temporada.sql
│       ├── 02_evolucao_pontuacao_campeao.sql
│       ├── 03_ranking_historico_times.sql
│       ├── 04_maiores_saldos_de_gols.sql
│       ├── 05_aproveitamento_por_time_temporada.sql
│       ├── 06_desempenho_por_regiao.sql
│       ├── 07_clubes_por_estado.sql
│       ├── 08_perfil_historico_dos_clubes.sql
│       ├── 09_comparativo_campanhas_por_regiao.sql
│       └── 10_relacao_posicao_saldo_gols.sql
│
├── test/
│
├── app.py
├── painel.py
├── dashboard.css
├── dashboard.js
├── index.html
├── mkdocs.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

O banco `football.duckdb` é criado localmente pelo pipeline e não é versionado no Git.

## Dados de origem

O projeto utiliza dados históricos do Campeonato Brasileiro.

Fonte de referência:

[Kaggle — Brasileirão Série A 2006–2022](https://www.kaggle.com/datasets/lucasyukioimafuko/brasileirao-serie-a-2006-2022)

Arquivos utilizados:

| Arquivo | Conteúdo |
|---|---|
| `brasileirao.csv` | Temporadas, posições, pontuação, jogos, vitórias, empates, derrotas e gols |
| `times.csv` | Cadastro dos clubes, siglas, fundação, estádio, cidade, estado e região |

**Observação sobre os dados:** embora o conjunto de referência do Kaggle indique o período de 2006 a 2022, os arquivos atualmente versionados no repositório apresentam temporadas de 2003 a 2024. A procedência e a correspondência integral entre essas versões ainda não foram confirmadas.

A ingestão utiliza os arquivos locais e não realiza download automático nem atualização da fonte externa.

## Consultas analíticas — Gold

A camada Gold possui dez consultas SQL, organizadas para responder a diferentes perguntas sobre o histórico do campeonato.

| Nº | Análise | Objetivo |
|---:|---|---|
| 01 | Campeões por temporada | Identificar os campeões e suas campanhas |
| 02 | Evolução da pontuação dos campeões | Comparar a pontuação dos campeões ao longo dos anos |
| 03 | Ranking histórico dos times | Consultar as campanhas por temporada e posição |
| 04 | Maiores saldos de gols | Identificar as campanhas com maiores saldos |
| 05 | Aproveitamento por time e temporada | Comparar o aproveitamento dos clubes |
| 06 | Desempenho por região | Analisar métricas agrupadas por região |
| 07 | Clubes por estado | Explorar a distribuição geográfica dos clubes |
| 08 | Perfil histórico dos clubes | Consultar participações e desempenho histórico |
| 09 | Comparativo de campanhas por região | Comparar médias regionais por temporada |
| 10 | Relação entre posição e saldo de gols | Explorar a relação entre classificação e saldo |

As consultas estão disponíveis em `sql/gold/`.

## Dashboard

O dashboard permite explorar os resultados materializados na camada Gold por meio de indicadores, tabelas e gráficos interativos.

Tecnologias:
- Streamlit para a interface.
- Plotly para visualizações.
- DuckDB para consulta dos resultados analíticos.

A implementação está dividida em dois módulos:

| Arquivo | Responsabilidade |
|---|---|
| `painel.py` | Acesso aos dados Gold, formatação e construção dos gráficos |
| `app.py` | Interface Streamlit, filtros e apresentação |

O dashboard possui dez análises numeradas, com filtros de temporada conforme a disponibilidade de cada consulta.

**Importante:** o dashboard não executa as etapas de ingestão, transformação ou materialização Gold. É necessário executar o pipeline previamente.

## Instalação e configuração

### Pré-requisitos

- Python 3.13 ou superior.
- [uv](https://docs.astral.sh/uv/).
- Git.

### Clonar o repositório

```bash
git clone https://github.com/Diego99xz/pipeline-Football.git

cd pipeline-Football
```

### Instalar as dependências

```bash
uv sync
```

O `uv` utiliza o `pyproject.toml` e o `uv.lock` para preparar o ambiente do projeto.

## Executar o pipeline

As etapas devem ser executadas na sequência abaixo.

### 1. Ingestão — Bronze

```bash
uv run python -m pipeline.ingestao
```

Carrega os arquivos CSV e materializa as tabelas Bronze.

### 2. Transformação — Silver

```bash
uv run python -m pipeline.transformacao
```

Lê as tabelas Bronze, realiza as conversões de tipos e materializa as tabelas Silver.

### 3. Análises — Gold

```bash
uv run python -m pipeline.gold
```

Executa as consultas SQL e materializa as tabelas analíticas Gold.

### 4. Executar o dashboard

```bash
uv run streamlit run app.py
```

O Streamlit disponibiliza o endereço local para acesso à aplicação no terminal.

## Testes e qualidade de código

O projeto utiliza pytest para verificar o comportamento dos módulos do pipeline e das funções do painel.

### Executar os testes

```bash
uv run pytest
```

### Executar com cobertura

```bash
uv run pytest --cov
```

A configuração atual estabelece uma cobertura mínima global de 60%.

Os testes utilizam dados inventados e bancos DuckDB temporários, evitando dependência dos dados reais e do banco utilizado pelo dashboard.

O módulo `app.py` não está incluído na medição de cobertura e deve ser validado visualmente no navegador.

### Verificação com Ruff

```bash
uv run ruff check test
```

O comando verifica o diretório de testes conforme a configuração atual.

## Documentação técnica — MkDocs

O projeto utiliza MkDocs para organizar a documentação técnica em páginas Markdown.

A documentação contempla informações sobre arquitetura, dados, pipeline, consultas analíticas e execução do projeto.

### Executar localmente

```bash
uv run mkdocs serve
```

### Gerar o site

```bash
uv run mkdocs build --strict
```

O site gerado fica no diretório `site/`, que não é versionado no Git.

A configuração atual permite a geração e visualização local da documentação. Não há publicação automática configurada.

## Configurações adicionais

### MCP DuckDB

O repositório contém uma configuração MCP em `.vscode/mcp.json`, utilizando o servidor `mcp-server-duckdb` em modo somente leitura.

Essa integração é auxiliar ao ambiente de desenvolvimento no VS Code e não é necessária para executar o pipeline.

MCP é um protocolo de integração entre ferramentas e recursos. Não substitui o DuckDB nem executa as transformações do projeto.

### Git e organização

Convenção recomendada para branches:

```text
<ID_DA_TAREFA>-<titulo-da-tarefa>
```

Exemplo:

```bash
git checkout -b 123-adicionar-dashboard
```

Os commits devem utilizar mensagens descritivas, facilitando o rastreamento das alterações.

### Segurança

O `.gitignore` contempla ambientes virtuais, caches, bancos locais, arquivos de cobertura e arquivos de configuração de segredos.

Não versionar tokens, senhas, chaves privadas ou credenciais. O `.gitignore` não substitui o gerenciamento seguro de segredos e não remove arquivos que já estejam versionados.

## Limitações e melhorias futuras

O projeto possui algumas limitações conhecidas:

- Execução manual e independente das etapas.
- Ausência de orquestração e agendamento.
- Ausência de ingestão incremental.
- Ausência de integração contínua com GitHub Actions.
- Ausência de publicação automática da documentação MkDocs.
- Necessidade de validar a procedência e a atualização dos dados de origem.

Possíveis evoluções incluem:

- Implementar testes e lint automatizados em GitHub Actions.
- Adicionar validações de qualidade dos dados.
- Automatizar a execução das etapas do pipeline.
- Evoluir a documentação técnica.
- Ampliar as análises históricas e comparativas.

## Referências

- [Dataset Brasileirão Série A — Kaggle](https://www.kaggle.com/datasets/lucasyukioimafuko/brasileirao-serie-a-2006-2022)
- [Repositório Football — GitHub](https://github.com/Diego99xz/pipeline-Football)
- [Python](https://docs.python.org/3/)
- [uv](https://docs.astral.sh/uv/)
- [DuckDB](https://duckdb.org/docs/)
- [pandas](https://pandas.pydata.org/docs/)
- [Streamlit](https://docs.streamlit.io/)
- [Plotly](https://plotly.com/python/)
- [pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Ruff](https://docs.astral.sh/ruff/)
- [MkDocs](https://www.mkdocs.org/)

---

**Desenvolvido como projeto de estudo e portfólio em Engenharia de Dados.**
