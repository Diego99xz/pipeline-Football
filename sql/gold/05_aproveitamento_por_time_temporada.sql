-- Qual foi o aproveitamento de pontos de cada time em uma temporada?
-- Grão: um time em uma temporada.
-- Considera 3 pontos por vitória e 1 por empate como referência de pontuação máxima.
SELECT
    temporada,
    time,
    posicao,
    pontos,
    jogos_disputados,
    ROUND(
        100.0 * pontos / NULLIF(jogos_disputados * 3, 0),
        2
    ) AS aproveitamento_pct
FROM football.silver.brasileirao
ORDER BY temporada DESC, aproveitamento_pct DESC;