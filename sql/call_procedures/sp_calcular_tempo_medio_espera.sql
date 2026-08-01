-- 2. Calcular tempo médio de espera
BEGIN;
    -- Executa a procedure passando o nome do cursor
    CALL sp_calcular_tempo_medio_espera('rs_tempo_espera');

    -- Lê o resultado gerado pelo cursor
    FETCH ALL FROM rs_tempo_espera;
COMMIT;
