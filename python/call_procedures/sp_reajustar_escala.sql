-- 3. Reajustar escala
CALL sp_reajustar_escala(
    :p_id_residente,
    :p_dia_semana_antigo,
    :p_turno_antigo,
    :p_id_nova_unidade,
    :p_novo_dia_semana,
    :p_novo_turno
);