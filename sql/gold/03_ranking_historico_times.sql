-- Quais times tiveram as melhores campanhas em cada temporada?
-- Grão: um time em uma temporada.
SELECT
    temporada,
    posicao,
    time,
    pontos,
    vitorias,
    empates,
    derrotas,
    saldo_de_gols
FROM football.silver.brasileirao
ORDER BY temporada DESC, posicao ASC;