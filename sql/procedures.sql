-- PROCEDURES

-- 1. Registrar atendimento completo 
CREATE OR REPLACE PROCEDURE sp_registrar_atendimento_completo(
    IN p_data_hora TIMESTAMP,
    IN p_duracao_minutos INT,
    IN p_id_paciente INT,
    IN p_id_residente INT,
    IN p_id_preceptor INT,
    IN p_id_unidade INT,
    IN p_procedimentos JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_atendimento INT;
    proc_atual JSONB;
BEGIN

    BEGIN -- Uso de outro "BEGIN" para permitir o tratamento de erros dentro da transação 

        -- 1. Inserção do atendimento fornecido à tabela Atendimento
        INSERT INTO Atendimento(
            data_hora, duracao_minutos,
            id_paciente, id_residente, id_preceptor,
            id_unidade -- Nova coluna adicionada na etapa 2
        )
        VALUES(
            p_data_hora, p_duracao_minutos,
            p_id_paciente, p_id_residente, p_id_preceptor,
            p_id_unidade
        )
        RETURNING id_atendimento INTO v_id_atendimento;

        FOR proc_atual IN SELECT * FROM jsonb_array_elements(p_procedimentos) 
        LOOP
            INSERT INTO Procedimento_Realizado(
                id_atendimento,
                id_procedimento,
                quantidade,
                tempo_real_minutos,
                observacao,
                is_faturado,
                data_hora_inicio -- Nova coluna adicionada na etapa 2
            )
            VALUES(
                v_id_atendimento,
                (proc_atual->>'id_procedimento')::INT,
                (proc_atual->>'quantidade')::INT,
                (proc_atual->>'tempo_real_minutos')::INT,
                proc_atual->>'observacao',
                (proc_atual->>'is_faturado')::BOOLEAN,
                (proc_atual->>'data_hora_inicio')::TIMESTAMP
            );
        END LOOP;

        -- Caso contrário:
        EXCEPTION
            WHEN OTHERS THEN
                RAISE;
    END;
END;
$$;
