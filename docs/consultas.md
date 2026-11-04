# Consultas analíticas Gold

Os arquivos em `sql/gold/` são a fonte da verdade das métricas. Cada consulta
é materializada em tabela com o nome derivado do arquivo, sem o prefixo
numérico.

| Nº | Arquivo / tabela | Pergunta e grão descritos no SQL |
|---:|---|---|
| 01 | `01_campeoes_por_temporada.sql` → `campeoes_por_temporada` | Campeão e desempenho por temporada; uma linha por temporada. |
| 02 | `02_evolucao_pontuacao_campeao.sql` → `evolucao_pontuacao_campeao` | Pontuação do campeão ao longo das temporadas; uma linha por temporada. |
| 03 | `03_ranking_historico_times.sql` → `ranking_historico_times` | Campanhas ordenadas por temporada e posição; um time em uma temporada. |
| 04 | `04_maiores_saldos_de_gols.sql` → `maiores_saldos_de_gols` | Campanhas ordenadas pelo saldo de gols; um time em uma temporada. |
| 05 | `05_aproveitamento_por_time_temporada.sql` → `aproveitamento_por_time_temporada` | Aproveitamento de pontos por time e temporada, calculado no SQL usando três pontos por vitória e máximo de três pontos por jogo. |
| 06 | `06_desempenho_por_regiao.sql` → `desempenho_por_regiao` | Agregados regionais por temporada; uma região em uma temporada. |
| 07 | `07_clubes_por_estado.sql` → `clubes_por_estado` | Quantidade de clubes e regiões por estado; um estado. |
| 08 | `08_perfil_historico_dos_clubes.sql` → `perfil_historico_dos_clubes` | Histórico de participações e desempenho de cada clube; um clube. |
| 09 | `09_comparativo_campanhas_por_regiao.sql` → `comparativo_campanhas_por_regiao` | Médias regionais por temporada; uma região em uma temporada. |
| 10 | `10_relacao_posicao_saldo_gols.sql` → `relacao_posicao_saldo_gols` | Campanhas para relacionar posição final e saldo; um time em uma temporada. |

O filtro, a ordenação e as expressões exatas estão definidos nos arquivos SQL.
Consulte-os antes de interpretar os resultados; esta página não redefine as
regras de negócio.
