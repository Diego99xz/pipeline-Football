# Transformação para Silver

Módulo: `pipeline/transformacao.py`.

A etapa lê somente `football.bronze.brasileirao` e `football.bronze.times`.
Verifica a presença das duas tabelas antes de gravar e recria as cópias em
`football.silver`.

Na tabela `brasileirao`, temporada, posição, estatísticas e contagens são
convertidas para `BIGINT`; `time` permanece `VARCHAR`. Na tabela `times`,
`ano_fundacao` é convertido para `BIGINT` e os demais campos permanecem
`VARCHAR`. Nomes e ordem das colunas são preservados.

A transformação mantém linhas, duplicatas e nulos. Valores que não podem ser
convertidos causam falha em vez de serem corrigidos ou descartados. Não há
JOIN nem regras analíticas nesta etapa.

```bash
uv run python -m pipeline.transformacao
```

As contagens de origem e destino são consultadas no banco e exibidas ao fim
da execução.
