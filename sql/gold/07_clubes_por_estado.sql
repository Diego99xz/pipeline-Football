-- Quantos clubes estão cadastrados em cada estado?
-- Grão: um estado.
SELECT
    estado,
    COUNT(*) AS total_clubes,
    COUNT(DISTINCT regiao) AS regioes
FROM football.silver.times
GROUP BY estado
ORDER BY total_clubes DESC, estado;