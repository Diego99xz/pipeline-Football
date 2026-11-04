# Ingestão para Bronze

Módulo: `pipeline/ingestao.py`.

A ingestão usa os arquivos `brasileirao.csv` e `times.csv` localizados na pasta
`bronze/`, conforme o caminho definido por `pipeline.db`. Ela verifica a
presença dos dois arquivos antes de abrir o banco.

Os CSVs são lidos com pandas usando `dtype="string"`: cabeçalhos e valores são
preservados como texto, e o parser mantém seu tratamento padrão de ausências.
Os resultados substituem `football.bronze.brasileirao` e
`football.bronze.times`, respectivamente; reexecutar a etapa não acumula
linhas.

```bash
uv run python -m pipeline.ingestao
```

A etapa informa as contagens consultadas no DuckDB. Arquivo ausente, falha de
leitura, conexão ou gravação resulta em código de saída diferente de zero. A
conexão é fechada quando chega a ser aberta.
