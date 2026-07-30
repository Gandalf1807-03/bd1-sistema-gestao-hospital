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

-- 2. Calcular tempo médio de espera
CREATE OR REPLACE PROCEDURE sp_calcular_tempo_medio_espera(
    INOUT p_cursor REFCURSOR DEFAULT 'rs_tempo_espera'
)
LANGUAGE plpgsql
AS $$
BEGIN
    OPEN p_cursor FOR
        SELECT 
            u.id_unidade,
            u.nome AS nome_unidade,
            -- Calcula a média em minutos entre a chegada (atendimento) 
            -- e o primeiro procedimento (menor data_hora_inicio)
            ROUND(
                AVG(
                    EXTRACT(EPOCH FROM (pr.primeiro_procedimento - a.data_hora)) / 60
                )::NUMERIC, 2
            ) AS tempo_medio_espera_minutos
        FROM UNIDADE u
        -- Relaciona o atendimento à unidade (através da escala)
        INNER JOIN ESCALA e ON u.id_unidade = e.id_unidade
        INNER JOIN ATENDIMENTO a ON a.id_residente = e.id_residente 
                          AND a.id_preceptor = e.id_preceptor
        -- Busca a menor data de início dos procedimentos para cada atendimento
        INNER JOIN (
            SELECT id_atendimento, MIN(data_hora_inicio) AS primeiro_procedimento
            FROM PROCEDIMENTO_REALIZADO
            GROUP BY id_atendimento
        ) pr ON a.id_atendimento = pr.id_atendimento
        GROUP BY u.id_unidade, u.nome;
END;
$$;
