-- Quem foi campeão em cada temporada e quantos pontos conquistou?
-- Grão: uma temporada.
SELECT
    temporada,
    time AS campeao,
    pontos,
    vitorias,
    empates,
    derrotas,
    gols,
    gols_sofridos,
    saldo_de_gols
FROM football.silver.brasileirao
WHERE posicao = 1
ORDER BY temporada;