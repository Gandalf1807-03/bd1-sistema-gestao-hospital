-- 1. Registrar atendimento completo

CALL sp_registrar_atendimento_completo(
    date_trunc('second', NOW()::TIMESTAMP),
    30,     -- 30 min de duração
    1,      -- Paciente  com ID 1 (Thiago Sergio)
    15,     -- Residente com ID 15 (Iago Vitor)
    6,      -- Preceptor com ID 6 (Jennifer Freire)
    1,      -- Unidade   com ID 1 (Enfermaria Central)

    -- Procedimentos realizados:
    '[
        {
            "id_procedimento": 1,
            "quantidade": 2,
            "tempo_real_minutos": 10,
            "observacao": "ok",
            "is_faturado": true,
            "data_hora_inicio": "2026-05-11 14:05:00"
        },
        {
            "id_procedimento": 2,
            "quantidade": 1,
            "tempo_real_minutos": 20,
            "observacao": "demorado",
            "is_faturado": false,
            "data_hora_inicio": "2026-05-13 8:17:32"
        }
    ]'::jsonb
);
