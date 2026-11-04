# Arquitetura

O projeto separa ingestão, tipagem e análises em etapas. O arquivo DuckDB fica
na raiz do repositório e os caminhos do pipeline são resolvidos a partir dos
módulos, não do diretório corrente.

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
                       │       │
                       ▼       ▼
                    painel.py  app.py
                 leitura/gráficos  Streamlit
```

`pipeline.db` centraliza acesso ao banco, criação de schemas e gravação. A
ingestão grava as tabelas Bronze, a transformação recria as tabelas Silver e
a etapa Gold executa as consultas SQL versionadas. `painel.py` lê Gold em
modo somente leitura e constrói tabelas e figuras Plotly; `app.py` compõe a
interface Streamlit.

As definições analíticas estão nos arquivos SQL, não na etapa Python que os
materializa. A etapa Gold recria o schema `football.gold` em transação e
reverte a alteração se alguma consulta falhar.

## Componentes

| Caminho | Responsabilidade |
|---|---|
| `pipeline/db.py` | Conexão DuckDB, criação de schema e substituição de tabelas. |
| `pipeline/ingestao.py` | Leitura dos CSVs de origem e gravação em Bronze. |
| `pipeline/transformacao.py` | Conversão dos campos Bronze para tipos Silver. |
| `pipeline/gold.py` | Validação e execução das consultas SQL Gold. |
| `sql/gold/` | Fonte das consultas analíticas materializadas. |
| `painel.py` | Leitura Gold, formatação e construtores de gráficos. |
| `app.py` | Interface interativa Streamlit. |
| `test/` | Testes automatizados com bancos temporários. |
