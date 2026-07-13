-- CONSULTAS ANALÍTICAS

-- 1. Ranking dos residentes por número de atendimentos realizados (mostrar nome e total)
SELECT R.id_pessoa, P.nome, COUNT(*) AS total_atendimentos
FROM Atendimento A
INNER JOIN Residente R      ON A.id_residente = R.id_pessoa
INNER JOIN Profissional PR  ON R.id_pessoa = PR.id_pessoa
INNER JOIN Pessoa P         ON PR.id_pessoa = P.id_pessoa
GROUP BY R.id_pessoa, P.nome
ORDER BY total_atendimentos DESC

-- 2. Listar os preceptores que supervisionaram mais de 5 atendimentos em um determinado mês
SELECT *
FROM Preceptor P
INNER JOIN Atendimento A ON 
WHERE 