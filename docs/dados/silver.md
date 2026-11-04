# Camada Silver

`pipeline/transformacao.py` recria as tabelas Silver a partir das duas tabelas
Bronze. A camada declara tipos de forma explícita e preserva as colunas, sua
ordem, as linhas duplicadas e os valores nulos.

Na tabela `football.silver.brasileirao`, as colunas numéricas de temporada,
posição, partidas e desempenho são `BIGINT`; `time` é `VARCHAR`. Na tabela
`football.silver.times`, `ano_fundacao` é `BIGINT` e os atributos descritivos
são `VARCHAR`.

Valores incompatíveis com os tipos esperados causam erro. A transformação não
calcula classificação, métricas agregadas ou junções; essas análises pertencem
às consultas SQL Gold.
