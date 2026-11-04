# Instalação e execução

## Requisitos

- Python 3.13 ou superior, conforme `pyproject.toml`.
- [`uv`](https://docs.astral.sh/uv/).
- Os CSVs `brasileirao.csv` e `times.csv` na pasta `bronze/`.

O projeto já mantém esses dois arquivos em `bronze/`. A referência informada
para os dados é o conjunto [Brasileirão Série A 2006–2022 no Kaggle](https://www.kaggle.com/datasets/lucasyukioimafuko/brasileirao-serie-a-2006-2022).
Confirme que os arquivos baixados correspondem ao formato esperado antes de
substituir os CSVs versionados.

## Preparar o ambiente

Na raiz do repositório:

```bash
uv sync
```

Isso instala as dependências do projeto, incluindo DuckDB, pandas, Plotly e
Streamlit. O MkDocs está no grupo de desenvolvimento.

## Executar o pipeline

Execute as etapas na ordem abaixo:

```bash
uv run python -m pipeline.ingestao
uv run python -m pipeline.transformacao
uv run python -m pipeline.gold
```

A ingestão exige os dois CSVs em `bronze/`. A transformação depende das tabelas
`football.bronze.brasileirao` e `football.bronze.times`. A materialização Gold
depende das tabelas Silver e dos arquivos SQL em `sql/gold/`.

Cada etapa retorna código diferente de zero e informa a etapa com erro quando
uma entrada ou operação falha. A etapa Gold preserva a última materialização
bem-sucedida caso uma consulta falhe.

## Executar o dashboard e os testes

```bash
uv run streamlit run app.py
uv run pytest --cov
```

O dashboard lê as tabelas Gold existentes. Ele não executa ingestão,
transformação nem materialização ao iniciar. Veja [Dashboard](dashboard.md)
para o comportamento dos filtros.

## Documentação local

```bash
uv run mkdocs serve
uv run mkdocs build
```

O servidor local apresenta a documentação durante a edição. O build estático
é gerado em `site/`; esse diretório está listado no `.gitignore`.
