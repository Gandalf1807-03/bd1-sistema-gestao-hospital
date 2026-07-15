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
WITH dias_mes AS (
    SELECT generate_series(
        date_trunc('month', CURRENT_DATE),
        date_trunc('month', CURRENT_DATE) + INTERVAL '1 month - 1 day',
        INTERVAL '1 day'
    )::date AS dia
),
ocorrencias_dia_semana AS (
    SELECT
        CASE EXTRACT(DOW FROM dia)
            WHEN 0 THEN 'DOMINGO'
            WHEN 1 THEN 'SEGUNDA'
            WHEN 2 THEN 'TERCA'
            WHEN 3 THEN 'QUARTA'
            WHEN 4 THEN 'QUINTA'
            WHEN 5 THEN 'SEXTA'
            WHEN 6 THEN 'SABADO'
        END AS dia_semana,
        COUNT(*) AS qtd_no_mes
    FROM dias_mes
    GROUP BY dia_semana
)
SELECT
    U.nome AS unidade,
    P.nome AS residente,
    SUM(ODS.qtd_no_mes) AS qtd_plantoes
FROM Escala E
INNER JOIN Unidade U ON U.id_unidade = E.id_unidade
INNER JOIN Residente R ON R.id_pessoa = E.id_residente
INNER JOIN Pessoa P ON P.id_pessoa = R.id_pessoa
INNER JOIN ocorrencias_dia_semana ODS ON ODS.dia_semana = E.dia_semana
GROUP BY U.nome, P.nome
ORDER BY U.nome, P.nome;




-- 4. Listar pacientes que nunca realizaram nenhum procedimento de nível de risco 'ALTO'

SELECT P.nome
FROM Pessoa P
INNER JOIN Paciente PC ON PC.id_pessoa = P.id_pessoa
WHERE NOT EXISTS(
  SELECT 1
  FROM Atendimento ATD
  INNER JOIN Procedimento_Realizado PR ON PR.id_atendimento = ATD.id_atendimento
  INNER JOIN Procedimento PRC ON PRC.id_procedimento = PR.id_procedimento
  WHERE ATD.id_paciente = PC.id_pessoa AND PRC.nivel_risco = 'ALTO'
)
GROUP BY P.nome;