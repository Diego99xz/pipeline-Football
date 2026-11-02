-- Quais regiões tiveram melhor desempenho agregado em cada temporada?
-- Grão: uma região em uma temporada.
SELECT
    b.temporada,
    t.regiao,
    COUNT(*) AS times_participantes,
    ROUND(AVG(b.posicao), 2) AS media_posicao,
    ROUND(AVG(b.pontos), 2) AS media_pontos,
    SUM(b.vitorias) AS total_vitorias,
    SUM(b.gols) AS total_gols,
    SUM(b.gols_sofridos) AS total_gols_sofridos
FROM football.silver.brasileirao AS b
JOIN football.silver.times AS t
    ON b.time = t.time
GROUP BY
    b.temporada,
    t.regiao
ORDER BY
    b.temporada,
    media_posicao ASC;