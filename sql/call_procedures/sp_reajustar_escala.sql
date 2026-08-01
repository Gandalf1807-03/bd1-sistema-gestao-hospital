-- 3. Reajustar escala
CALL sp_reajustar_escala(
    13,         -- Residente com ID 13
    'TERCA',    -- dia_semana antigo
    'MANHA',    -- turno antigo
    2,          -- id_nova_unidade
    'QUARTA',   -- novo dia_semana
    'NOITE'     -- novo turno
);