-- ============================================================
-- 1. VIEW: vw_pacientes_internados
-- ============================================================
-- Lista os pacientes atualmente internados
-- (data_hora_saida IS NULL), mostrando a unidade
-- relacionada ao atendimento que originou a internação.
-- ============================================================

CREATE OR REPLACE VIEW vw_pacientes_internados AS -- Criação da view para listar pacientes internados, incluindo informações sobre a unidade de atendimento.
SELECT  
    P.id_pessoa, --P: identificador da pessoa, nome e CPF do paciente;
    P.nome,
    P.cpf,
    I.id_internacao, -- I: identificador da internação e data/hora de entrada
    I.data_hora_entrada,
    U.nome AS unidade_atual, -- U: nome e tipo da unidade de atendimento.
    U.tipo AS tipo_unidade
FROM Internacao I -- Utiliza a tabela de internações como base da consulta.
INNER JOIN Atendimento A -- Vincular a internação ao atendimento correspondente
    ON I.id_atendimento = A.id_atendimento
INNER JOIN Paciente Pac -- Vincular o atendimento ao paciente correspondente
    ON A.id_paciente = Pac.id_pessoa
INNER JOIN Pessoa P -- Vincular o paciente à tabela de pessoas para obter informações adicionais
    ON Pac.id_pessoa = P.id_pessoa
INNER JOIN Unidade U -- Vincular o atendimento à unidade correspondente
    ON A.id_unidade = U.id_unidade
WHERE I.data_hora_saida IS NULL -- Filtrar apenas pacientes que ainda estão internados (data_hora_saida é nula)
ORDER BY I.data_hora_entrada; -- Ordenar os resultados pela data de entrada.


-- ============================================================
-- 2. VIEW: vw_residentes_sem_supervisor
-- ============================================================
-- Lista residentes escalados cujo preceptor
-- não possui titulação de Doutor.
-- ============================================================

CREATE OR REPLACE VIEW vw_residentes_sem_supervisor AS --Criação da view para listar residentes sem supervisores com titulação de Doutor.
SELECT DISTINCT --DISTINCT é usado para eliminar duplicatas.
    P_res.id_pessoa AS id_residente, --P: identificador da pessoa e nome do residente;
    P_res.nome AS residente,
    R.ano_residencia, -- R: ano de residência do residente;
    P_pre.id_pessoa AS id_preceptor, -- P_pre: identificador da pessoa e nome do preceptor;
    P_pre.nome AS preceptor,
    Pre.titulacao, -- Pre: titulação do preceptor;
    E.dia_semana, --E: dia da semana e turno da escala em que o residente está escalado;
    E.turno,
    U.nome AS unidade -- U: nome da unidade de atendimento onde o residente está escalado.
FROM Escala E -- Seleciona os registros da tabela Escala 
INNER JOIN Residente R -- Vincula a escala ao residente correspondente
    ON E.id_residente = R.id_pessoa
INNER JOIN Pessoa P_res -- Vincula o residente à tabela de pessoas para obter informações adicionais
    ON R.id_pessoa = P_res.id_pessoa
INNER JOIN Preceptor Pre -- Vincula a escala ao preceptor correspondente
    ON E.id_preceptor = Pre.id_pessoa
INNER JOIN Pessoa P_pre -- Vincula o preceptor à tabela de pessoas para obter informações adicionais
    ON Pre.id_pessoa = P_pre.id_pessoa
INNER JOIN Unidade U -- Vincula a escala à unidade correspondente
    ON E.id_unidade = U.id_unidade
WHERE Pre.titulacao <> 'Doutor' -- Filtra preceptores que não possuem titulação de Doutor
ORDER BY -- Ordena os resultados pelo nome do residente, dia da semana e turno
    P_res.nome,
    E.dia_semana,
    E.turno;

-- ============================================================
-- 3. VIEW: vw_estatisticas_atendimentos_mensal
-- ============================================================
-- Agregação por mês e unidade mostrando:
-- - Total de atendimentos;
-- - Média de duração;
-- - Procedimento mais comum.
-- ============================================================

CREATE OR REPLACE VIEW vw_estatisticas_atendimentos_mensal AS -- Criação da view para exibir estatísticas mensais de atendimentos.

SELECT 
    U.nome AS unidade, -- Nome da unidade de atendimento.
    TO_CHAR(DATE_TRUNC('month', A.data_hora), 'MM/YYYY') AS mes_ano, --Transforma a data do atendimento em um formato de mês/ano para agregação mensal.
    COUNT(DISTINCT A.id_atendimento) AS total_atendimentos, -- Conta o número total de atendimentos distintos realizados na unidade durante o mês.
    ROUND(AVG(A.duracao_minutos)::NUMERIC, 2) AS media_duracao_minutos, -- Calcula a média da duração dos atendimentos, arredondada para duas casas decimais.
    PMC.procedimento_nome AS procedimento_mais_comum, -- Nome do procedimento mais comum realizado na unidade durante o mês.
    PMC.qtd AS quantidade_procedimento --Quantidade de vezes que o procedimento mais comum foi realizado na unidade durante o mês.

FROM Atendimento A -- Seleciona os registros da tabela Atendimento para agregação.

INNER JOIN Unidade U -- Vincula o atendimento à unidade correspondente
    ON A.id_unidade = U.id_unidade -- Garante que cada atendimento seja associado à unidade correta.

-- LEFT JOIN é utilizado porque pode existir atendimento sem procedimento registrado. Assim, esses atendimentos continuam aparecendo nas estatísticas.
LEFT JOIN ( --Junta uma subconsulta que calcula o procedimento mais comum realizado em cada unidade por mês.

    SELECT -- Subconsulta para determinar o procedimento mais comum por unidade e mês.
        X.id_unidade,
        X.mes,
        X.procedimento_nome,
        X.qtd
    FROM ( -- Subconsulta para calcular a quantidade de cada procedimento realizado por unidade e mês.

        SELECT
            A.id_unidade, -- Identificador da unidade de atendimento.
            DATE_TRUNC('month', A.data_hora) AS mes, -- Trunca a data do atendimento para o primeiro dia do mês, permitindo a agregação mensal.
            P.nome AS procedimento_nome, -- Nome do procedimento realizado.
            COUNT(*) AS qtd, -- Conta o número de vezes que cada procedimento foi realizado na unidade durante o mês.
            RANK() OVER ( -- Utiliza a função RANK() para classificar os procedimentos por quantidade, permitindo identificar o mais comum. Em caso de empate, todos os procedimentos empatados recebem a mesma classificação.
                PARTITION BY A.id_unidade, -- Particiona os resultados por unidade e mês, garantindo que a classificação seja feita separadamente para cada unidade e mês.
                        DATE_TRUNC('month', A.data_hora)
                ORDER BY COUNT(*) DESC -- Ordena os procedimentos pela quantidade em ordem decrescente, para que o procedimento mais comum receba a classificação 1.
            ) AS posicao -- Atribui uma posição a cada procedimento com base na quantidade, permitindo identificar o procedimento mais comum (posição 1).

        FROM Atendimento A --Conta os procedimentos realizados em cada atendimento, agrupando por unidade e mês.

        INNER JOIN Procedimento_Realizado PR -- Vincula o atendimento aos procedimentos realizados, permitindo contar quantos procedimentos foram realizados em cada atendimento.
            ON A.id_atendimento = PR.id_atendimento

        INNER JOIN Procedimento P -- Vincula os procedimentos realizados à tabela de procedimentos para obter informações adicionais, como o nome do procedimento.
            ON PR.id_procedimento = P.id_procedimento

        GROUP BY --Cada procedimento em cada unidade e mês é agrupado para contar a quantidade de vezes que foi realizado.
            A.id_unidade,
            DATE_TRUNC('month', A.data_hora),
            P.nome

    ) X-- A subconsulta X calcula a quantidade de cada procedimento realizado por unidade e mês, atribuindo uma posição com base na quantidade.

    WHERE X.posicao = 1 -- Filtra apenas os procedimentos que ocupam a posição 1, ou seja, os mais comuns em cada unidade e mês.

) PMC -- A subconsulta PMC contém os procedimentos mais comuns por unidade e mês, que serão utilizados na view principal para exibir as estatísticas.

ON A.id_unidade = PMC.id_unidade -- Garante que cada atendimento seja associado ao procedimento mais comum da unidade correspondente.
AND DATE_TRUNC('month', A.data_hora) = PMC.mes 

GROUP BY -- Agrega os resultados por unidade, mês e procedimento mais comum, permitindo calcular as estatísticas desejadas.
    U.nome,
    DATE_TRUNC('month', A.data_hora),
    PMC.procedimento_nome,
    PMC.qtd

ORDER BY --Ordena os resultados finais da view por unidade, mês e procedimento mais comum, facilitando a leitura e análise das estatísticas.
    U.nome,
    DATE_TRUNC('month', A.data_hora) DESC,
    PMC.procedimento_nome;

-- ============================================================
-- 4. TESTES DAS VIEWS
-- ============================================================

-- Teste 1: Pacientes atualmente internados
SELECT * FROM vw_pacientes_internados;

-- Teste 2: Residentes sem supervisor Doutor
SELECT * FROM vw_residentes_sem_supervisor;

-- Teste 3: Estatísticas mensais dos atendimentos
SELECT * FROM vw_estatisticas_atendimentos_mensal;

-- Teste 4: Quantidade de pacientes internados
SELECT COUNT(*) AS total_internados
FROM vw_pacientes_internados;
