-- Pacientes: ids 1-5 | Preceptores: ids 6-10 | Residentes: ids 11-15

INSERT INTO Pessoa (nome, cpf, data_nascimento, is_flamengo) VALUES
    ('Thiago Sergio',   '52998224725', '1985-04-12', FALSE),
    ('Beatriz Souza',   '34578279472', '1992-07-21', FALSE),
    ('Diego Alves',     '47362478835', '1988-11-05', TRUE),
    ('Fernanda Lima',   '61684186507', '1995-02-28', FALSE),
    ('Gustavo Nunes',   '73255396100', '1979-09-15', TRUE),
    ('Jennifer Freire', '87748241068', '1988-12-22', TRUE),
    ('Bruno Rocha',     '11144477735', '1980-08-22', TRUE),
    ('Clara Melo',      '49601481859', '1983-06-17', FALSE),
    ('Luis Eduardo',    '63067547300', '1987-10-22', FALSE),
    ('Ana Maria',       '21486597897', '1990-12-05', TRUE),
    ('João Pedro',      '15976387674', '1997-01-24', FALSE),
    ('Janaina Pereira', '11122233396', '1998-06-14', TRUE),
    ('Gabriel Lorenzo', '22233344405', '1996-07-18', TRUE),
    ('Juliana Roccha',  '33344455514', '1997-08-09', TRUE),
    ('Iago Vitor',      '44455566623', '1999-02-25', FALSE);

INSERT INTO Pessoa_Telefones (id_pessoa, telefone) VALUES
    (1,  '81992085860'),
    (1,  '83998887777'),
    (2,  '83991110002'),
    (3,  '83991110003'),
    (4,  '83991110004'),
    (5,  '83991110005'),
    (6,  '83991084287'),
    (7,  '83992220002'),
    (8,  '83992220003'),
    (9,  '83991496860'),
    (10, '83992220005'),
    (11, '83994198490'),
    (12, '83993330002'),
    (13, '83999314014'),
    (14, '83993330004'),
    (15, '83993428882');

INSERT INTO Paciente (id_pessoa, num_convenio, grupo_sanguineo) VALUES
    (1, 'CONV-001', 'A+'),
    (2, 'CONV-002', 'O-'),
    (3, 'CONV-003', NULL), --Paciente 3 não sabe seu grupo sanguíneo
    (4,   NULL,    'AB+'), --Paciente 4 não tem convênio
    (5, 'CONV-005', 'O+');

INSERT INTO Paciente_Alergias (id_pessoa, alergia) VALUES
    (1, 'Penicilina'),
    (3, 'Dipirona'),
    (5, 'Cefalexina'), 
    (5, 'Ibuprofeno'),
    (5, 'AAS');

-- CRM no formato CRM/PB 

INSERT INTO Profissional (id_pessoa, crm, data_admissao, especialidade) VALUES
    (6,  'CRM/PB 8560',  '2010-03-01', 'Clinica Medica'),
    (7,  'CRM/PB 9321',  '2012-07-15', 'Cirurgia Geral'),
    (8,  'CRM/PB 1042', '2008-01-20', 'Pediatria'),
    (9,  'CRM/PB 1178', '2015-09-10', 'Ortopedia'),
    (10, 'CRM/PB 1289', '2018-04-05', 'Neurologia'),
    (11, 'CRM/PB 31045', '2023-02-01', 'Clinica Medica'),
    (12, 'CRM/PB 32187', '2023-02-01', 'Cirurgia Geral'),
    (13, 'CRM/PB 33962', '2022-08-01', 'Pediatria'),
    (14, 'CRM/PB 34501', '2024-03-01', 'Ortopedia'),
    (15, 'CRM/PB 35728', '2024-03-01', 'Neurologia');

INSERT INTO Preceptor (id_pessoa, titulacao) VALUES
    (6,  'Doutor'),
    (7,  'Mestre'),
    (8,  'Doutor'),
    (9,  'Especialista'),
    (10, 'Doutor');

INSERT INTO Residente (id_pessoa, ano_residencia) VALUES
    (11, 'R1'),
    (12, 'R2'),
    (13, 'R1'),
    (14, 'R3'),
    (15, 'R2');

INSERT INTO Unidade (nome, tipo, capacidade_leitos) VALUES
    ('Enfermaria Central', 'Enfermaria',     30),
    ('UTI Adulto',         'UTI',            20),
    ('Pronto-Socorro',     'Pronto-Socorro', 10),
    ('Ambulatorio Geral',  'Ambulatorio',     5);

INSERT INTO Escala (id_unidade, dia_semana, turno, id_residente, id_preceptor) VALUES
    (1, 'SEGUNDA', 'MANHA', 11, 6),
    (1, 'SEGUNDA', 'TARDE', 12, 7),
    (2, 'TERCA',   'MANHA', 13, 8),
    (2, 'TERCA',   'NOITE', 14, 9),
    (3, 'QUARTA',  'TARDE', 15, 10),
    (4, 'QUINTA',  'MANHA', 11, 6),
    (3, 'SEXTA',   'NOITE', 12, 7),
    (2, 'SABADO',  'MANHA', 13, 8),
    (4, 'DOMINGO', 'TARDE', 14, 9),
    (1, 'SEGUNDA', 'NOITE', 15, 10);

-- ATENDIMENTO (todos em maio/2026)
INSERT INTO Atendimento (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor) VALUES
    ('2026-05-01 08:00:00', 30, 1, 11, 6),
    ('2026-05-02 09:15:00', 45, 2, 11, 6),
    ('2026-05-03 10:30:00', 60, 3, 11, 6),
    ('2026-05-04 11:00:00', 20, 4, 11, 6),
    ('2026-05-05 14:00:00', 90, 5, 12, 6),
    ('2026-05-06 08:30:00', 35, 1, 12, 6),
    ('2026-05-07 09:00:00', 50, 2, 13, 7),
    ('2026-05-08 10:00:00', 25, 3, 13, 8),
    ('2026-05-09 13:00:00', 70, 4, 14, 9),
    ('2026-05-10 15:00:00', 40, 5, 15, 10);


INSERT INTO Procedimento (codigo, nome, tempo_medio_minutos, nivel_risco) VALUES
    ('PROC001', 'Coleta de sangue',             15, 'BAIXO'),
    ('PROC002', 'Curativo',                     20, 'BAIXO'),
    ('PROC003', 'Raio-X',                       30, 'MEDIO'),
    ('PROC004', 'Sutura',                       45, 'ALTO'),
    ('PROC005', 'Intubacao',                    60, 'ALTO'),
    ('PROC006', 'Administracao de medicamento', 10, 'BAIXO');

INSERT INTO Procedimento_Realizado (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao, is_faturado) VALUES
    (1,  1, 1, 18, NULL,                                    FALSE),
    (1,  2, 1, 22, 'Curativo simples pos-coleta',           TRUE),
    (2,  6, 2, 12, NULL,                                    FALSE),
    (3,  3, 1, 35, NULL,                                    FALSE),
    (4,  2, 1, 20, NULL,                                    TRUE),
    (5,  1, 1, 16, NULL,                                    FALSE),
    (6,  6, 1, 10, NULL,                                    FALSE),
    (7,  3, 1, 32, NULL,                                    TRUE),
    (8,  4, 1, 50, 'Paciente com dificuldade respiratoria', FALSE),
    (9,  5, 1, 65, 'Intercorrencia: queda de saturacao',    FALSE),
    (10, 1, 1, 12, NULL,                                    FALSE);

-- Reseta os dados, mas não apaga nenhuma tabela
-- TRUNCATE TABLE
--     Pessoa,
--     Pessoa_Telefones,
--     Paciente,
--     Paciente_Alergias,
--     Profissional,
--     Preceptor,
--     Residente,
--     Unidade,
--     Escala,
--     Atendimento,
--     Procedimento,
--     Procedimento_Realizado
-- RESTART IDENTITY CASCADE;
