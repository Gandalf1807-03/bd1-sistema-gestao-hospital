--ESCRITA DAS BUSCAS




-- Inserir um novo atendimento (verificando se paciente, residente, preceptor existem)
INSERT INTO Atendimento (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor) VALUES
    ('2026-07-12 19:00:00', 60, 5, 14, 8); --correto
    -- ('2026-07-13 19:00:00', 20, 6, 9, 15),
    -- ('2026-07-14 08:00:00', 15, 4, 11, 13),
    -- ('2026-07-15 12:30:00', 45, 1, 6, 16);


-- Listar todos os atendimentos de um paciente específico (ordenados por data)
SELECT * FROM atendimento A
WHERE A.id_paciente = 1 ORDER BY data_hora ASC;


-- Listar os procedimentos realizados em um atendimento (com nome do procedimento, quantidade e tempo real)
SELECT P.nome, PR.quantidade, PR.tempo_real_minutos FROM procedimento P, procedimento_realizado PR
WHERE P.id_procedimento IN (
    SELECT PR.id_procedimento FROM procedimento_realizado
    WHERE PR.id_atendimento = 2
);

-- Atualizar os dados de um paciente (endereço ou convênio)
ALTER TABLE paciente 



-- Remover um procedimento realizado (apenas se ainda não houver faturamento associado – usar uma flag)



-- Calcular o tempo médio de duração dos atendimentos por residente