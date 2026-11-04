# Football

Documentação técnica do projeto de Engenharia de Dados que organiza dados do
Campeonato Brasileiro em camadas Bronze, Silver e Gold e apresenta os
resultados em um dashboard Streamlit com Plotly.

O pipeline e o dashboard usam o banco DuckDB local `football.duckdb`. A camada
Gold é definida pelos arquivos SQL em `sql/gold/`; o dashboard lê as tabelas
materializadas e não executa o pipeline automaticamente.

## Comece por aqui

- [Arquitetura](arquitetura.md): componentes e fluxo entre as camadas.
- [Instalação e execução](instalacao.md): ambiente, comandos e pré-requisitos.
- [Pipeline](pipeline/ingestao.md): ingestão, transformação e materialização.
- [Camadas de dados](dados/bronze.md): formato e responsabilidade de cada camada.
- [Consultas analíticas](consultas.md): catálogo das dez consultas Gold.
- [Dashboard](dashboard.md): indicadores, gráficos e filtros.
- [Testes](testes.md): execução e isolamento dos testes.
- [Desenvolvimento e qualidade](desenvolvimento.md): ferramentas configuradas.

## Repositório

Consulte o [README do repositório](https://github.com/Diego99xz/pipeline-Football#readme)
e o [código-fonte no GitHub](https://github.com/Diego99xz/pipeline-Football).
