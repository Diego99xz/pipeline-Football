-- Como a média de pontos dos clubes varia entre as regiões por temporada?
-- Grão: uma região em uma temporada.
SELECT
    b.temporada,
    t.regiao,
    COUNT(*) AS total_times,
    ROUND(AVG(b.pontos), 2) AS media_pontos,
    ROUND(AVG(b.vitorias), 2) AS media_vitorias,
    ROUND(AVG(b.gols), 2) AS media_gols,
    ROUND(AVG(b.saldo_de_gols), 2) AS media_saldo_de_gols
FROM football.silver.brasileirao AS b
JOIN football.silver.times AS t
    ON b.time = t.time
GROUP BY
    b.temporada,
    t.regiao
ORDER BY
    b.temporada,
    media_pontos DESC;