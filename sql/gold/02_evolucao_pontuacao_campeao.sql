-- A pontuação necessária para ser campeão mudou ao longo do tempo?
-- Grão: uma temporada, considerando o campeão.
SELECT
    temporada,
    time AS campeao,
    pontos,
    vitorias,
    saldo_de_gols
FROM football.silver.brasileirao
WHERE posicao = 1
ORDER BY temporada;