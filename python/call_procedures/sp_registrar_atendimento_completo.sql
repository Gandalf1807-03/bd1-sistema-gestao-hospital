-- 1. Registrar atendimento completo
CALL sp_registrar_atendimento_completo(
    :p_data_hora,
    :p_duracao_minutos,
    :p_id_paciente,
    :p_id_residente,
    :p_id_preceptor,
    :p_id_unidade,
    CAST(:p_procedimentos AS jsonb)
);
