-- OPERAÇÕES CRUD (Create, Read, Update, Delete)

--===============================================================================
-- 1: Inserir um novo atendimento (verificando se paciente, residente, preceptor existem)

--ANTES DA MODIFICAÇÃO: SELECT * FROM Atendimento

INSERT INTO Atendimento (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor) VALUES
    ('2026-07-12 19:00:00', 60, 5, 14, 8); 

--DEPOIS DA MODIFICAÇÃO: SELECT * FROM Atendimento
--===============================================================================
-- 2: Listar todos os atendimentos de um paciente específico (ordenados por data)
SELECT * FROM Atendimento A
WHERE A.id_paciente = 1 ORDER BY data_hora ASC;


-- 3: Listar os procedimentos realizados em um atendimento (com nome do procedimento, quantidade e tempo real)
SELECT P.nome, PR.quantidade, PR.tempo_real_minutos FROM Procedimento P, Procedimento_Realizado PR
WHERE P.id_procedimento IN (
    SELECT PR.id_procedimento FROM Procedimento_Realizado
    WHERE PR.id_atendimento = 2
);

--===============================================================================
-- 4: Atualizar os dados de um paciente (convênio)

--ANTES DA MODIFICAÇÃO: SELECT * FROM Paciente;

UPDATE Paciente
SET num_convenio = 'CONV-004'
WHERE id_pessoa = 4;

--DEPOIS DA MODIFICAÇÃO: SELECT * FROM Paciente;
--===============================================================================
-- 5:Remover um procedimento realizado (remove apenas se is_faturado = FALSE)

-- ANTES DA MODIFICAÇÃO: SELECT * FROM Procedimento_Realizado;

DELETE FROM Procedimento_Realizado
WHERE id_atendimento = 1
  AND id_procedimento = 1
  AND is_faturado = FALSE;

--DEPOIS DA MODIFICAÇÃO: SELECT * FROM Procedimento_Realizado;
--===============================================================================
-- 6: Calcular o tempo médio de duração dos atendimentos por residente

SELECT
    Pe.nome                  AS nome_residente,
    R.id_pessoa,
    ROUND(AVG(A.duracao_minutos),2) AS tempo_medio_minutos,
    COUNT(A.id_atendimento)  AS total_atendimentos
FROM Atendimento A
JOIN Residente R      ON A.id_residente = R.id_pessoa
JOIN Profissional Pr  ON R.id_pessoa = Pr.id_pessoa
JOIN Pessoa Pe        ON Pr.id_pessoa = Pe.id_pessoa
GROUP BY Pe.nome, R.id_pessoa
ORDER BY tempo_medio_minutos DESC;
--===============================================================================