-- ============================================================
-- 1. TRIGGER: trg_check_sobreposicao_escala
-- ============================================================
-- Impede que um mesmo residente seja escalado no mesmo dia
-- e turno em duas unidades diferentes.
-- ============================================================

CREATE OR REPLACE FUNCTION fn_check_sobreposicao_escala() -- Criação da função que será chamada pela trigger para verificar sobreposição de escalas.
RETURNS TRIGGER AS --Retorna um tipo TRIGGER.
$$
BEGIN --Início do bloco de código da função.
    -- Para INSERT: não existe OLD, só verifica conflito com outras linhas.
    IF TG_OP = 'INSERT' THEN -- Verifica se a operação é um INSERT.

        IF EXISTS ( -- Verifica se já existe um registro na tabela Escala com o mesmo residente, dia da semana e turno, mas em uma unidade diferente.
            SELECT 1
            FROM Escala --NEW: dados que estão sendo inseridos na tabela.
            WHERE id_residente = NEW.id_residente -- Verifica se o residente já está escalado.
              AND dia_semana = NEW.dia_semana  -- Verifica se o dia da semana é o mesmo.
              AND turno = NEW.turno -- Verifica se o turno é o mesmo.
              AND id_unidade <> NEW.id_unidade --Verifica se a unidade é diferente.
        ) THEN -- Se existir, gera uma exceção informando que o residente já está escalado no mesmo dia/turno em outra unidade.
            RAISE EXCEPTION 'Residente % já está escalado no mesmo dia/turno em outra unidade.',
                NEW.id_residente;
        END IF;

    -- Para UPDATE: existe OLD, verifica conflito com outras linhas, ignorando a própria linha que está sendo atualizada.
    ELSIF TG_OP = 'UPDATE' THEN -- Verifica se a operação é um UPDATE.

        IF EXISTS ( -- Verifica se já existe um registro na tabela Escala com o mesmo residente, dia da semana e turno, mas em uma unidade diferente, excluindo a própria linha que está sendo atualizada.
            SELECT 1
            FROM Escala
            WHERE id_residente = NEW.id_residente
              AND dia_semana = NEW.dia_semana
              AND turno = NEW.turno
              AND id_unidade <> NEW.id_unidade
              AND id_escala <> NEW.id_escala -- Exclui a própria linha que está sendo atualizada da verificação de conflito. Isso evita que a trigger gere um erro ao atualizar a mesma linha sem alterar o dia/turno/unidade.
        ) THEN
            RAISE EXCEPTION 'Residente % já está escalado no mesmo dia/turno em outra unidade.',
                NEW.id_residente;
        END IF;

    END IF;

    RETURN NEW; -- Retorna a nova linha para que a operação de INSERT ou UPDATE possa prosseguir.
END;
$$
LANGUAGE plpgsql; -- Define a linguagem da função como PL/pgSQL, que é uma extensão do SQL para PostgreSQL, permitindo a criação de funções e triggers mais complexas.

DROP TRIGGER IF EXISTS trg_check_sobreposicao_escala ON Escala; -- Remove a trigger se ela já existir na tabela, garantindo que não haja conflitos ao criar uma nova trigger com o mesmo nome.

CREATE TRIGGER trg_check_sobreposicao_escala -- Cria o gatilho.
BEFORE INSERT OR UPDATE ON Escala -- Executa antes de inserir ou atualizar.
FOR EACH ROW --Executa para cada linha afetada.
EXECUTE FUNCTION fn_check_sobreposicao_escala(); --Chama a função criada.


-- ============================================================
-- 2. TRIGGER: trg_audita_atendimento
-- ============================================================
-- Registra automaticamente operações INSERT, UPDATE e DELETE
-- na tabela Atendimento, armazenando o histórico na tabela
-- Auditoria_Atendimento com dados em JSON.
-- ============================================================

CREATE OR REPLACE FUNCTION fn_audita_atendimento() --Criação da função que registra operações na tabela Atendimento.
RETURNS TRIGGER AS
$$
BEGIN
    IF TG_OP = 'INSERT' THEN 

        INSERT INTO Auditoria_Atendimento --Insere na tabela de auditoria.
        (
            id_atendimento,
            operacao,
            usuario,
            dados_novos
        )
        VALUES
        (
            NEW.id_atendimento, --ID que está sendo inserido.
            'INSERT', -- Tipo de operação.
            CURRENT_USER, --Quem fez a operação.
            to_jsonb(NEW) --Dados após a operação.
        );

        RETURN NEW; --Retorna os dados

    ELSIF TG_OP = 'UPDATE' THEN 

        INSERT INTO Auditoria_Atendimento
        (
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES
        (
            NEW.id_atendimento,
            'UPDATE',
            CURRENT_USER,
            to_jsonb(OLD), --Dados antes da atualização.
            to_jsonb(NEW) -- Dados depois da atualização.
        );

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN

        INSERT INTO Auditoria_Atendimento
        (
            id_atendimento,
            operacao,
            usuario,
            dados_antigos
        )
        VALUES
        (
            OLD.id_atendimento, -- ID que está sendo removido.
            'DELETE',
            CURRENT_USER,
            to_jsonb(OLD) --Dados do atendimento antes da exclusão.
        );

        RETURN OLD; --Retorna os dados antigos.

    END IF;

    RETURN NULL; --Retorna nulo caso nenhuma condição seja atendida.
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audita_atendimento ON Atendimento;

CREATE TRIGGER trg_audita_atendimento 
AFTER INSERT OR UPDATE OR DELETE ON Atendimento --Executar o trigger depois (registrar) de qualquer operação.
FOR EACH ROW
EXECUTE FUNCTION fn_audita_atendimento();


-- ============================================================
-- 3. TRIGGER: trg_atualiza_media_procedimentos
-- ============================================================
-- Mantém a média real de tempo dos procedimentos atualizada
-- automaticamente após cada inserção em Procedimento_Realizado.
-- ============================================================

CREATE OR REPLACE FUNCTION fn_atualiza_media_procedimentos()
RETURNS TRIGGER AS
$$
BEGIN
    UPDATE Procedimento --Atualiza a tabela de procedimento.
       SET media_tempo_procedimento = --Define o valor dessa coluna.
       (
            SELECT ROUND(AVG(tempo_real_minutos)::NUMERIC,2) --Calcula a média de todos os tempos reais. 
            FROM Procedimento_Realizado --Busca os procedimentos realizados.
            WHERE id_procedimento = NEW.id_procedimento -- Subconsulta: calcula a média usando apenas os registros do procedimento inserido.
       )
     WHERE id_procedimento = NEW.id_procedimento; -- UPDATE: aplica o cálculo apenas no procedimento correspondente.

    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_atualiza_media_procedimentos ON Procedimento_Realizado;

CREATE TRIGGER trg_atualiza_media_procedimentos
AFTER INSERT ON Procedimento_Realizado --Executa depois da operação.
FOR EACH ROW
EXECUTE FUNCTION fn_atualiza_media_procedimentos();


-- ============================================================
-- 4. TESTES DAS TRIGGERS
-- ============================================================

-- TESTE 1: TRIGGER DE SOBREPOSIÇÃO DE ESCALA

-- 1.1 Verificação do estado inicial
SELECT * FROM Escala WHERE id_residente = 11 ORDER BY id_escala;

-- 1.2 Teste de bloqueio (deve gerar erro)
-- O residente 11 já está escalado na unidade 1 na SEGUNDA MANHA
/*
INSERT INTO Escala (id_unidade, dia_semana, turno, id_residente, id_preceptor)
VALUES (2, 'SEGUNDA', 'MANHA', 11, 7);
*/

-- 1.3 Teste de permissão (deve executar com sucesso)
-- A combinação QUARTA MANHA para o residente 11 não existe
/*
INSERT INTO Escala (id_unidade, dia_semana, turno, id_residente, id_preceptor)
VALUES (1, 'QUARTA', 'MANHA', 11, 7);
*/

-- 1.4 Verificação do estado final
SELECT * FROM Escala WHERE id_residente = 11 ORDER BY id_escala;

-- TESTE 2: TRIGGER DE AUDITORIA DE ATENDIMENTOS

-- 2.1 Consulta ao estado atual da auditoria
SELECT * FROM Auditoria_Atendimento ORDER BY id_auditoria DESC LIMIT 5;

-- 2.2 Teste de INSERT
-- Insere um novo atendimento e verifica o registro na auditoria
/*
INSERT INTO Atendimento (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade)
VALUES (CURRENT_TIMESTAMP, 30, 1, 11, 6, 1);
*/
SELECT * FROM Auditoria_Atendimento WHERE operacao = 'INSERT' ORDER BY id_auditoria DESC LIMIT 3;

-- 2.3 Teste de UPDATE
-- Atualiza a duração de um atendimento e verifica o registro na auditoria
/*
UPDATE Atendimento SET duracao_minutos = 45 WHERE id_atendimento = 1;
*/
SELECT * FROM Auditoria_Atendimento WHERE operacao = 'UPDATE' ORDER BY id_auditoria DESC LIMIT 3;

-- 2.4 Teste de DELETE
-- Remove o último atendimento e verifica o registro na auditoria
/*
DELETE FROM Atendimento WHERE id_atendimento = (SELECT MAX(id_atendimento) FROM Atendimento);
*/
SELECT * FROM Auditoria_Atendimento WHERE operacao = 'DELETE' ORDER BY id_auditoria DESC LIMIT 3;

-- 2.5 Visão completa da auditoria
SELECT * FROM Auditoria_Atendimento ORDER BY id_auditoria DESC;

-- TESTE 3: TRIGGER DE ATUALIZAÇÃO DA MÉDIA DE PROCEDIMENTOS

-- 3.1 Média atual do procedimento 2 (Curativo)

SELECT id_procedimento, nome, media_tempo_procedimento 
FROM Procedimento 
WHERE id_procedimento = 2;

-- 3.2 Inserção de um novo registro
-- Adiciona um procedimento Curativo com tempo real de 25 minutos
/*
INSERT INTO Procedimento_Realizado (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, data_hora_inicio, is_faturado)
VALUES (2, 2, 1, 25, CURRENT_TIMESTAMP, FALSE);
*/

-- 3.3 Verificação da média após a inserção
SELECT id_procedimento, nome, media_tempo_procedimento 
FROM Procedimento 
WHERE id_procedimento = 2;

-- 3.4 Relatório completo das médias
SELECT 
    id_procedimento, 
    nome, 
    tempo_medio_minutos AS estimado, 
    media_tempo_procedimento AS real_medio 
FROM Procedimento 
ORDER BY id_procedimento;