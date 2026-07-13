-- CONSULTAS ANALÍTICAS

-- 1. Ranking dos residentes por número de atendimentos realizados (mostrar nome e total)
SELECT  R.id_pessoa     AS id_residente,
        P.nome          AS nome_residente,
        COUNT(*)        AS total_atendimentos
FROM Atendimento A
INNER JOIN Residente R      ON A.id_residente = R.id_pessoa
INNER JOIN Profissional PR  ON R.id_pessoa = PR.id_pessoa
INNER JOIN Pessoa P         ON PR.id_pessoa = P.id_pessoa
GROUP BY R.id_pessoa, P.nome
ORDER BY total_atendimentos DESC;

-- 2. Listar os preceptores que supervisionaram mais de 5 atendimentos em um determinado mês
SELECT  PP.id_pessoa    AS id_preceptor, 
        P.nome          AS nome_preceptor,
        COUNT(*)        AS num_atendimentos 
FROM Atendimento A
INNER JOIN Preceptor PP     ON A.id_preceptor = PP.id_pessoa
INNER JOIN Profissional PR  ON PP.id_pessoa = PR.id_pessoa
INNER JOIN Pessoa P         ON PR.id_pessoa = P.id_pessoa
WHERE EXTRACT(MONTH FROM A.data_hora) = 5   -- Mês selecionado: Maio
  AND EXTRACT(YEAR FROM A.data_hora) = 2026 -- Ano selecionado: 2026
GROUP BY PP.id_pessoa, P.nome
HAVING COUNT(*) > 5
ORDER BY num_atendimentos DESC;

-- 3. Para cada unidade, mostrar a quantidade de plantões escalados por residente no mês corrente


-- 4. Listar pacientes que nunca realizaram nenhum procedimento de nível de risco 'ALTO'

