-- ============================================================
-- ETAPA 2 - ALTERAÇÕES ESTRUTURAIS
-- ============================================================
-- Executar APÓS:
-- 1. create_tables.sql
-- 2. inserts.sql
-- Este arquivo adapta o banco da Etapa 1 para atender
-- aos requisitos da Etapa 2.
-- ============================================================
-- 1. UNIDADE DO ATENDIMENTO
-- ============================================================
-- Necessário para:
-- - sp_calcular_tempo_medio_espera
-- - vw_estatisticas_atendimentos_mensal

ALTER TABLE Atendimento
ADD COLUMN id_unidade INT; --Criação da coluna id_unidade na tabela Atendimento para referenciar a unidade onde o atendimento ocorreu.

ALTER TABLE Atendimento
ADD CONSTRAINT fk_atendimento_unidade --Criação da constraint fk_atendimento_unidade para garantir a integridade referencial entre Atendimento e Unidade.
FOREIGN KEY (id_unidade)
REFERENCES Unidade(id_unidade)
ON UPDATE CASCADE -- Se a unidade for alterada, o atendimento deve refletir a mudança.
ON DELETE RESTRICT;

-- Distribuição dos atendimentos existentes

UPDATE Atendimento
SET id_unidade =
CASE
    WHEN id_atendimento IN (1,5,9)   THEN 1  -- Enfermaria
    WHEN id_atendimento IN (2,6,10)  THEN 2  -- UTI
    WHEN id_atendimento IN (3,7)     THEN 3  -- Pronto-Socorro
    WHEN id_atendimento IN (4,8)     THEN 4  -- Ambulatorio
END;

ALTER TABLE Atendimento
ALTER COLUMN id_unidade SET NOT NULL; -- Garantir que todos os atendimentos tenham uma unidade associada.

-- ============================================================
-- 2. HORÁRIO DE INÍCIO DO PROCEDIMENTO
-- ============================================================
-- Necessário para:
-- sp_calcular_tempo_medio_espera

ALTER TABLE Procedimento_Realizado
ADD COLUMN data_hora_inicio TIMESTAMP; -- Criação da coluna para registrar o horário de início do procedimento.

UPDATE Procedimento_Realizado pr 
SET data_hora_inicio = -- Calcula o horário de início do procedimento com base no horário do atendimento associado e um tempo adicional específico para cada tipo de procedimento.
    a.data_hora + 
     CASE pr.id_procedimento -- Define o tempo adicional com base no tipo de procedimento.
        WHEN 1 THEN INTERVAL '10 minutes'  -- Coleta de sangue (rápido)
        WHEN 2 THEN INTERVAL '15 minutes'  -- Curativo
        WHEN 3 THEN INTERVAL '20 minutes'  -- Raio-X (precisa deslocar)
        WHEN 4 THEN INTERVAL '15 minutes'  -- Sutura (preparo)
        WHEN 5 THEN INTERVAL '5 minutes'   -- Intubação (emergência)
        WHEN 6 THEN INTERVAL '10 minutes'  -- Medicamento
        ELSE INTERVAL '15 minutes'
    END
FROM Atendimento a
WHERE a.id_atendimento = pr.id_atendimento;

ALTER TABLE Procedimento_Realizado
ALTER COLUMN data_hora_inicio SET NOT NULL;

-- ============================================================
-- 3. MÉDIA REAL DOS PROCEDIMENTOS
-- ============================================================
-- Utilizada pela trigger:
-- trg_atualiza_media_procedimentos

ALTER TABLE Procedimento
ADD COLUMN media_tempo_procedimento NUMERIC(10,2); -- Criação da coluna para armazenar a média real do tempo dos procedimentos realizados (com duas casas decimais).

UPDATE Procedimento p
SET media_tempo_procedimento = medias.media -- Atualiza a coluna media_tempo_procedimento com a média calculada dos tempos reais dos procedimentos realizados, agrupados por id_procedimento.
FROM ( 
--Subconsulta para calcular a média real dos tempos dos procedimentos realizados, agrupados por id_procedimento.
    SELECT
        id_procedimento,
        ROUND(AVG(tempo_real_minutos)::NUMERIC,2) AS media -- Calcula a média arredondada para duas casas decimais.
    FROM Procedimento_Realizado
    GROUP BY id_procedimento
) medias -- Resultado da subconsulta é referenciado como "medias" para ser usado na atualização da tabela Procedimento.

WHERE medias.id_procedimento = p.id_procedimento;

-- ============================================================
-- 4. TABELA DE AUDITORIA
-- ============================================================
-- Utilizada por:
-- trg_audita_atendimento

CREATE TABLE Auditoria_Atendimento ( -- Criação da tabela de auditoria para registrar operações realizadas na tabela Atendimento.

    id_auditoria SERIAL PRIMARY KEY,
    id_atendimento INT, --Permite manter o histórico de operações mesmo que o atendimento seja excluído.
    operacao VARCHAR(10) NOT NULL, -- Tipo de operação realizada (INSERT, UPDATE, DELETE).
    usuario VARCHAR(100) NOT NULL, --Nome do usuário que realizou a operação.
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, --Registra a data e hora da operação, com valor padrão sendo o timestamp atual.
    dados_antigos JSONB, -- Armazena os dados antigos do atendimento antes da operação (em formato JSON).
    dados_novos JSONB, -- Armazena os dados novos do atendimento após a operação (em formato JSON).

    CHECK (
        operacao IN ('INSERT','UPDATE','DELETE')
    )

);

-- ============================================================
-- 5. INTERNAÇÃO
-- ============================================================
--
-- Utilizada por:
-- vw_pacientes_internados
--
-- A internação referencia o atendimento.
-- O paciente e a unidade são obtidos através dele.
--

CREATE TABLE Internacao (

    id_internacao SERIAL PRIMARY KEY,
    id_atendimento INT NOT NULL UNIQUE, -- Cada internação está associada a um único atendimento.
    data_hora_entrada TIMESTAMP NOT NULL, -- Data e hora de entrada do paciente na internação.
    data_hora_saida TIMESTAMP, -- Data e hora de saída do paciente da internação (pode ser nula se o paciente ainda estiver internado).

    FOREIGN KEY (id_atendimento) --Garante a integridade referencial entre Internacao e Atendimento, vinculando cada internação a um atendimento específico.
        REFERENCES Atendimento(id_atendimento)
        ON UPDATE CASCADE -- Se o atendimento for atualizado, a internação refletirá a mudança.
        ON DELETE RESTRICT, -- Impede a exclusão de um atendimento se houver uma internação associada.
    CHECK (data_hora_saida IS NULL OR data_hora_saida >= data_hora_entrada) -- Garante que a data de saída seja nula ou posterior à data de entrada.
);

-- ============================================================
-- 6. TESTES
-- ============================================================

--Verificar colunas adicionadas: 

-- Ver todas as colunas da tabela Atendimento (deve aparecer id_unidade)
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'atendimento' 
ORDER BY ordinal_position;

-- Ver colunas do Procedimento_Realizado (deve aparecer data_hora_inicio)
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'procedimento_realizado' 
ORDER BY ordinal_position;

-- Ver colunas do Procedimento (deve aparecer media_tempo_procedimento)
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'procedimento' 
ORDER BY ordinal_position;

--Verificar novas tabelas: 

SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('auditoria_atendimento', 'internacao');

-- Dados de teste para a tabela Internação:

INSERT INTO Internacao (
    id_atendimento,
    data_hora_entrada,
    data_hora_saida
)
VALUES
(1,'2026-05-01 08:00',NULL),
(5,'2026-05-05 14:00','2026-05-07 09:00'),
(9,'2026-05-09 13:00',NULL);

-- Dados de teste para a tabela Auditoria_Atendimento:

/*
INSERT INTO Auditoria_Atendimento (
    id_atendimento,
    operacao,
    usuario,
    dados_antigos,
    dados_novos
)
VALUES 
  (1, 'INSERT', 'jenni', NULL, '{"id_atendimento": 1, "duracao_minutos": 30}'::jsonb),
  (2, 'UPDATE', 'jenni', '{"duracao_minutos": 45}'::jsonb, '{"duracao_minutos": 50}'::jsonb),
  (3, 'DELETE', 'jenni', '{"id_atendimento": 3}'::jsonb, NULL);

Verificar dados inseridos na tabela Internacao:
SELECT * FROM Internacao;

 Verificar dados inseridos na tabela Auditoria_Atendimento:
SELECT * FROM Auditoria_Atendimento;

*/