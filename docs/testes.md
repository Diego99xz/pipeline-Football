# Testes

Os testes usam pytest. Os testes que precisam de DuckDB criam bancos
temporários com `tmp_path`; não dependem de o pipeline ter sido executado nem
do banco `football.duckdb` do projeto.

Execute a suíte com coverage:

```bash
uv run pytest --cov
```

A configuração em `pyproject.toml` define `test/` como diretório de testes e
uma cobertura mínima global de 60%. A medição inclui `pipeline/` e
`painel.py`, e exclui `app.py`, `ui.py` e os próprios testes. A interface
Streamlit deve ser validada manualmente no navegador.

Os arquivos atuais de teste são:

- `test/test_db.py`
- `test/test_ingestao.py`
- `test/test_transformacao.py`
- `test/test_gold.py`
- `test/test_painel.py`
