-- Existe uma associação entre saldo de gols e posição final?
-- Grão: um time em uma temporada.
SELECT
    b.temporada,
    b.time,
    t.regiao,
    b.posicao,
    b.pontos,
    b.saldo_de_gols,
    b.gols,
    b.gols_sofridos
FROM football.silver.brasileirao AS b
LEFT JOIN football.silver.times AS t
    ON b.time = t.time
ORDER BY b.temporada, b.posicao;