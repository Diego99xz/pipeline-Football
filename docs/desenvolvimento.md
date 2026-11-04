# Desenvolvimento e qualidade

## Dependências e ferramentas

As dependências de execução declaradas em `pyproject.toml` são DuckDB,
pandas, Plotly e Streamlit. O grupo de desenvolvimento contém MkDocs, pytest,
pytest-cov e Ruff. O ambiente e o lockfile são gerenciados com `uv`.

Comandos usuais:

```bash
uv sync
uv run ruff check test
uv run pytest --cov
uv run mkdocs serve
uv run mkdocs build
```

O repositório não contém configuração de GitHub Actions em
`.github/workflows/`; portanto, não há integração contínua configurada a
documentar. Não há configuração explícita de regras Ruff em `pyproject.toml`;
o comando usa os padrões do Ruff instalado.

O comando de exemplo do Ruff verifica a pasta de testes; uma verificação
abrangente também pode encontrar pendências de lint em módulos de produção.

## Alterações de dados

Mantenha as regras de negócio nas consultas SQL Gold. Antes de alterar uma
consulta, verifique sua tabela resultante e os consumidores em `painel.py`.
Preserve os contratos de tipos e colunas das camadas, e execute testes após
mudanças.

O dashboard lê os dados Gold. Para atualizar as tabelas, execute as etapas do
pipeline explicitamente, conforme [Instalação e execução](instalacao.md).
