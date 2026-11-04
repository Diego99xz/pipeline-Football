# Camada Bronze

A Bronze contém a cópia tabular de origem. `pipeline/ingestao.py` lê os CSVs
`brasileirao.csv` e `times.csv` de `bronze/` como texto e substitui as tabelas
`football.bronze.brasileirao` e `football.bronze.times`.

Os cabeçalhos observados nos arquivos de origem são:

- `brasileirao.csv`: `temporada`, `posicao`, `time`, `pontos`,
  `jogos_disputados`, `vitorias`, `empates`, `derrotas`, `gols`,
  `gols_sofridos`, `saldo_de_gols`.
- `times.csv`: `time`, `sigla`, `nome_completo`, `ano_fundacao`, `estadio`,
  `cidade`, `estado`, `regiao`.

A ingestão conserva os valores textuais para que a conversão de tipos ocorra
na etapa Silver. Os caminhos são relativos ao módulo do banco, e não ao
diretório atual do shell.
