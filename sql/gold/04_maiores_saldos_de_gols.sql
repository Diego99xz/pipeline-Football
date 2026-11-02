-- Quais times terminaram uma temporada com os maiores saldos de gols?
-- Grão: um time em uma temporada.
SELECT
    temporada,
    time,
    posicao,
    gols,
    gols_sofridos,
    saldo_de_gols
FROM football.silver.brasileirao
ORDER BY saldo_de_gols DESC, temporada DESC;