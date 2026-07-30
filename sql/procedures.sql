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

        -- Inserção do atendimento fornecido à tabela Atendimento
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

-- 3. Reajustar escala
CREATE OR REPLACE PROCEDURE sp_reajustar_escala(
    p_id_residente INT,
    p_dia_semana_antigo VARCHAR,
    p_turno_antigo VARCHAR,
    p_nova_unidade INT,
    p_novo_dia_semana VARCHAR,
    p_novo_turno VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_conflito INT;
    v_id_escala INT;
BEGIN
    -- Verifica se a escala original realmente existe para o residente
    SELECT id_escala INTO v_id_escala
    FROM ESCALA
    WHERE id_residente = p_id_residente
        AND dia_semana = p_dia_semana_antigo
        AND turno = p_turno_antigo;

    IF v_id_escala IS NULL THEN
        RAISE EXCEPTION 'Escala de origem não encontrada para o residente informado.';
    END IF;

    -- Verifica se a nova escala vai gerar conflito 
    -- (Mesma unidade, mesmo dia, mesmo turno e mesmo residente)
    SELECT COUNT(*) INTO v_conflito
    FROM ESCALA
    WHERE id_unidade = p_nova_unidade
        AND dia_semana = p_novo_dia_semana
        AND turno = p_novo_turno
        AND id_residente = p_id_residente
        AND id_escala <> v_id_escala; -- Ignora o próprio registro se for apenas alteração de unidade no mesmo horário

    IF v_conflito > 0 THEN
        RAISE EXCEPTION 'Conflito detectado: O residente já possui escala nessa unidade, dia e turno.';
    END IF;

    -- Atualiza a escala caso não haja conflito
    UPDATE ESCALA
    SET id_unidade = p_nova_unidade,
        dia_semana = p_novo_dia_semana,
        turno = p_novo_turno
    WHERE id_escala = v_id_escala;

    RAISE NOTICE 'Escala reajustada com sucesso!';
END;
$$;