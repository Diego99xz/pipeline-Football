# Camada Gold

As tabelas `football.gold` são materializadas pelos arquivos SQL de
`sql/gold/`. A etapa Python valida os arquivos e executa suas consultas, sem
completar ou alterar a lógica analítica.

As dez tabelas produzidas atualmente são:

1. `campeoes_por_temporada`
2. `evolucao_pontuacao_campeao`
3. `ranking_historico_times`
4. `maiores_saldos_de_gols`
5. `aproveitamento_por_time_temporada`
6. `desempenho_por_regiao`
7. `clubes_por_estado`
8. `perfil_historico_dos_clubes`
9. `comparativo_campanhas_por_regiao`
10. `relacao_posicao_saldo_gols`

`painel.py` lê essas tabelas usando uma conexão DuckDB somente leitura. As
colunas esperadas por tabela estão declaradas em `COLUNAS_ESPERADAS` no módulo.
Para o grão e o conteúdo de cada consulta, consulte o [catálogo SQL](../consultas.md).
