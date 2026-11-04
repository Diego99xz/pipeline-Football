# Materialização Gold

Módulo: `pipeline/gold.py`. As regras analíticas são definidas exclusivamente
pelos arquivos `sql/gold/*.sql`.

A etapa verifica as tabelas `football.silver.brasileirao` e
`football.silver.times`, valida os nomes dos arquivos SQL (`NN_nome.sql`) e
rejeita nomes inválidos ou que produzam nomes de tabela duplicados. As
consultas são executadas em ordem alfabética dos arquivos.

O schema `football.gold` é removido e recriado dentro de uma transação. Cada
arquivo cria uma tabela com `CREATE TABLE ... AS`. Resultado vazio é
considerado falha; qualquer falha na materialização provoca rollback para
preservar o schema Gold anterior. Uma execução bem-sucedida também remove
tabelas que já não correspondam a arquivos SQL presentes.

```bash
uv run python -m pipeline.gold
```

A saída informa cada tabela, sua contagem real, o número de tabelas e o total
de linhas.
