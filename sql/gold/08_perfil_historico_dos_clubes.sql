-- Quais clubes aparecem em mais temporadas no histórico disponível?
-- Grão: um clube.
SELECT
    b.time,
    t.sigla,
    t.nome_completo,
    t.estado,
    t.regiao,
    COUNT(DISTINCT b.temporada) AS temporadas_disputadas,
    MIN(b.temporada) AS primeira_temporada,
    MAX(b.temporada) AS ultima_temporada,
    ROUND(AVG(b.posicao), 2) AS media_posicao,
    SUM(b.vitorias) AS total_vitorias
FROM football.silver.brasileirao AS b
JOIN football.silver.times AS t
    ON b.time = t.time
GROUP BY
    b.time,
    t.sigla,
    t.nome_completo,
    t.estado,
    t.regiao
ORDER BY temporadas_disputadas DESC, media_posicao ASC;