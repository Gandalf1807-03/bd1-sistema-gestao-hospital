import models as md

from datetime import date, datetime
from sqlalchemy.orm import Session
from database import engine


#=====================================================================
#Criação de funções de inserção da ETAPA 1 (com alterações da etapa 2)
#=====================================================================

def inserir_pessoa(Session, nome, cpf, data_nascimento, is_flamengo = False):
    pessoa = md.Pessoa(
        nome = nome,
        cpf = cpf,
        data_nascimento = data_nascimento,
        is_flamengo = is_flamengo
    )
    Session.add(pessoa)
    Session.flush()
    return pessoa

def inserir_pessoa_telefone(Session, id_pessoa, telefone):
    pessoa_telefone = md.Pessoa_Telefone(
        id_pessoa = id_pessoa,
        telefone = telefone
    )
    Session.add(pessoa_telefone)
    Session.flush()
    return pessoa_telefone

def inserir_paciente(Session, id_pessoa, num_convenio, grupo_sanguineo):
    paciente = md.Paciente(
        id_pessoa = id_pessoa,
        num_convenio = num_convenio,
        grupo_sanguineo = grupo_sanguineo
    )
    Session.add(paciente)
    Session.flush()
    return paciente

def inserir_paciente_alergias(Session, id_pessoa, alergia):
    paciente_alergias = md.Paciente_Alergia(
        id_pessoa = id_pessoa,
        alergia = alergia
    )
    Session.add(paciente_alergias)
    Session.flush()
    return paciente_alergias

def inserir_profissional(Session, id_pessoa, crm, data_admissao, especialidade):
    profissional = md.Profissional(
        id_pessoa = id_pessoa,
        crm = crm,
        data_admissao = data_admissao,
        especialidade = especialidade
    )

    Session.add(profissional)
    Session.flush()
    return profissional

def inserir_preceptor(Session, id_pessoa, titulacao):
    preceptor = md.Preceptor(
        id_pessoa = id_pessoa,
        titulacao = titulacao
    )
    Session.add(preceptor)
    Session.flush()
    return preceptor

def inserir_residente(Session, id_pessoa, ano_residencia):
    residente = md.Residente(
        id_pessoa = id_pessoa,
        ano_residencia = ano_residencia
    )
    Session.add(residente)
    Session.flush()
    return residente

def inserir_unidade(Session, nome, tipo, capacidade_leitos):
    unidade = md.Unidade(
        nome = nome,
        tipo = tipo,
        capacidade_leitos = capacidade_leitos
    )
    Session.add(unidade)
    Session.flush()
    return unidade

def inserir_escala(Session, id_unidade, dia_semana, turno, id_residente, id_preceptor):
    escala = md.Escala(
        id_unidade = id_unidade,
        dia_semana = dia_semana,
        turno = turno,
        id_residente = id_residente,
        id_preceptor = id_preceptor
    )
    Session.add(escala)
    Session.flush()
    return escala

def inserir_atendimento(Session, data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade):
    atendimento = md.Atendimento(
        data_hora = data_hora,
        duracao_minutos = duracao_minutos,
        id_paciente = id_paciente,
        id_residente = id_residente,
        id_preceptor = id_preceptor,
        id_unidade = id_unidade #ADICIONADO na Etapa 2 (changes-etapa-2.sql)
    )
    Session.add(atendimento)
    Session.flush()
    return atendimento

def inserir_procedimento(Session, codigo, nome, tempo_medio_minutos, nivel_risco, media_tempo_procedimento):
    procedimento = md.Procedimento(
        codigo = codigo,
        nome = nome,
        tempo_medio_minutos = tempo_medio_minutos,
        nivel_risco = nivel_risco,
        media_tempo_procedimento = media_tempo_procedimento #ADICIONADO na Etapa 2 (changes-etapa-2.sql)
    )
    Session.add(procedimento)
    Session.flush()
    return procedimento

def inserir_procedimento_realizado(Session, id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao, data_hora_inicio, is_faturado = False):
    procedimento_realizado = md.Procedimento_Realizado(
        id_atendimento = id_atendimento,
        id_procedimento = id_procedimento,
        quantidade = quantidade,
        tempo_real_minutos = tempo_real_minutos,
        observacao = observacao,
        is_faturado = is_faturado,
        data_hora_inicio = data_hora_inicio #ADICIONADO na Etapa 2 (changes-etapa-2.sql)
    )
    Session.add(procedimento_realizado)
    Session.flush()
    return procedimento_realizado

#=========================================
#Criação de funções de inserção da ETAPA 2
#=========================================

def inserir_auditoria_atendimento(Session, id_auditoria, id_atendimento, operacao, usuario, data_hora, dados_antigos, dados_novos):
    auditoria_atendimento = md.Auditoria_Atendimento(
        id_auditoria = id_auditoria,
        id_atendimento = id_atendimento,
        operacao = operacao,
        usuario = usuario,
        data_hora = data_hora,
        dados_antigos = dados_antigos,
        dados_novos = dados_novos
    )
    Session.add(auditoria_atendimento)
    Session.flush()
    return auditoria_atendimento

def inserir_internacao(Session, id_internacao, id_atendimento, data_hora_entrada, data_hora_saida):
    internacao = md.Internacao(
        id_internacao = id_internacao,
        id_atendimento = id_atendimento,
        data_hora_entrada = data_hora_entrada,
        data_hora_saida = data_hora_saida
    )
    Session.add(internacao)
    Session.flush()
    return internacao


#=======================
#DEMONSTRAÇÃO DE INSERTS
#=======================
if __name__ == "__main__":
    with Session(engine) as session:
        try:
            #==========================
            # PESSOA (ids 1-15 na ordem)
            #==========================
            pessoas_dados = [
                ("Thiago Sergio",   "52998224725", date(1985, 4, 12), False),
                ("Beatriz Souza",   "34578279472", date(1992, 7, 21), False),
                ("Diego Alves",     "47362478835", date(1988, 11, 5), True),
                ("Fernanda Lima",   "61684186507", date(1995, 2, 28), False),
                ("Gustavo Nunes",   "73255396100", date(1979, 9, 15), True),
                ("Jennifer Freire", "87748241068", date(1988, 12, 22), True),
                ("Bruno Rocha",     "11144477735", date(1980, 8, 22), True),
                ("Clara Melo",      "49601481859", date(1983, 6, 17), False),
                ("Luis Eduardo",    "63067547300", date(1987, 10, 22), False),
                ("Ana Maria",       "21486597897", date(1990, 12, 5), True),
                ("João Pedro",      "15976387674", date(1997, 1, 24), False),
                ("Janaina Pereira", "11122233396", date(1998, 6, 14), True),
                ("Gabriel Lorenzo", "22233344405", date(1996, 7, 18), True),
                ("Juliana Rocha",   "33344455514", date(1997, 8, 9), True),
                ("Iago Vitor",      "44455566623", date(1999, 2, 25), False),
            ]

            pessoas = []
            for nome, cpf, nascimento, flamengo in pessoas_dados:
                p = inserir_pessoa(session, nome, cpf, nascimento, flamengo)
                pessoas.append(p)

            #==========================
            # PESSOA_TELEFONES
            #==========================
            telefones_dados = [
                (1, "81992085860"), (1, "83998887777"),
                (2, "83991110002"), (3, "83991110003"),
                (4, "83991110004"), (5, "83991110005"),
                (6, "83991084287"), (7, "83992220002"),
                (8, "83992220003"), (9, "83991496860"),
                (10, "83992220005"), (11, "83994198490"),
                (12, "83993330002"), (13, "83999314014"),
                (14, "83993330004"), (15, "83993428882"),
            ]
            for id_pessoa, telefone in telefones_dados:
                inserir_pessoa_telefone(session, id_pessoa, telefone)

            #==========================
            # PACIENTE (ids 1-5)
            #==========================
            pacientes_dados = [
                (1, "CONV-001", "A+"),
                (2, "CONV-002", "O-"),
                (3, "CONV-003", None),   
                (4, None, "AB+"),        
                (5, "CONV-005", "O+"),
            ]
            for id_pessoa, convenio, grupo in pacientes_dados:
                inserir_paciente(session, id_pessoa, convenio, grupo)

            #==========================
            # PACIENTE_ALERGIAS
            #==========================
            alergias_dados = [
                (1, "Penicilina"),
                (3, "Dipirona"),
                (5, "Cefalexina"),
                (5, "Ibuprofeno"),
                (5, "AAS"),
            ]
            for id_pessoa, alergia in alergias_dados:
                inserir_paciente_alergias(session, id_pessoa, alergia)

            #==========================
            # PROFISSIONAL (ids 6-15)
            #==========================
            profissionais_dados = [
                (6,  "CRM/PB 8560",  date(2010, 3, 1),  "Clinica Medica"),
                (7,  "CRM/PB 9321",  date(2012, 7, 15), "Cirurgia Geral"),
                (8,  "CRM/PB 1042",  date(2008, 1, 20), "Pediatria"),
                (9,  "CRM/PB 1178",  date(2015, 9, 10), "Ortopedia"),
                (10, "CRM/PB 1289",  date(2018, 4, 5),  "Neurologia"),
                (11, "CRM/PB 31045", date(2023, 2, 1),  "Clinica Medica"),
                (12, "CRM/PB 32187", date(2023, 2, 1),  "Cirurgia Geral"),
                (13, "CRM/PB 33962", date(2022, 8, 1),  "Pediatria"),
                (14, "CRM/PB 34501", date(2024, 3, 1),  "Ortopedia"),
                (15, "CRM/PB 35728", date(2024, 3, 1),  "Neurologia"),
            ]
            for id_pessoa, crm, admissao, especialidade in profissionais_dados:
                inserir_profissional(session, id_pessoa, crm, admissao, especialidade)

            #==========================
            # PRECEPTOR (ids 6-10)
            #==========================
            preceptores_dados = [
                (6,  "Doutor"),
                (7,  "Mestre"),
                (8,  "Doutor"),
                (9,  "Especialista"),
                (10, "Doutor"),
            ]
            for id_pessoa, titulacao in preceptores_dados:
                inserir_preceptor(session, id_pessoa, titulacao)

            #==========================
            # RESIDENTE (ids 11-15)
            #==========================
            residentes_dados = [
                (11, "R1"), (12, "R2"), (13, "R1"), (14, "R3"), (15, "R2"),
            ]
            for id_pessoa, ano in residentes_dados:
                inserir_residente(session, id_pessoa, ano)

            #==========================
            # UNIDADE
            #==========================
            unidades_dados = [
                ("Enfermaria Central", "Enfermaria",     30),
                ("UTI Adulto",         "UTI",            20),
                ("Pronto-Socorro",     "Pronto-Socorro", 10),
                ("Ambulatorio Geral",  "Ambulatorio",     5),
            ]
            unidades = []
            for nome, tipo, capacidade in unidades_dados:
                u = inserir_unidade(session, nome, tipo, capacidade)
                unidades.append(u)

            #==========================
            # ESCALA
            #==========================
            escalas_dados = [
                (1, "SEGUNDA", "MANHA", 11, 6),
                (1, "SEGUNDA", "TARDE", 12, 7),
                (2, "TERCA",   "MANHA", 13, 8),
                (2, "TERCA",   "NOITE", 14, 9),
                (3, "QUARTA",  "TARDE", 15, 10),
                (4, "QUINTA",  "MANHA", 11, 6),
                (3, "SEXTA",   "NOITE", 12, 7),
                (2, "SABADO",  "MANHA", 13, 8),
                (4, "DOMINGO", "TARDE", 14, 9),
                (1, "SEGUNDA", "NOITE", 15, 10),
            ]
            for id_unidade, dia, turno, id_residente, id_preceptor in escalas_dados:
                inserir_escala(session, id_unidade, dia, turno, id_residente, id_preceptor)

            #==========================
            # ATENDIMENTO (todos em unidade 1, já que a Etapa 1 não tinha essa coluna)
            #==========================
            atendimentos_dados = [
                (datetime(2026, 5, 1, 8, 0),   30, 1, 11, 6,  1),
                (datetime(2026, 5, 2, 9, 15),  45, 2, 11, 6,  1),
                (datetime(2026, 5, 3, 10, 30), 60, 3, 11, 6,  1),
                (datetime(2026, 5, 4, 11, 0),  20, 4, 11, 6,  1),
                (datetime(2026, 5, 5, 14, 0),  90, 5, 12, 6,  2),
                (datetime(2026, 5, 6, 8, 30),  35, 1, 12, 6,  2),
                (datetime(2026, 5, 7, 9, 0),   50, 2, 13, 7,  3),
                (datetime(2026, 5, 8, 10, 0),  25, 3, 13, 8,  3),
                (datetime(2026, 5, 9, 13, 0),  70, 4, 14, 9,  4),
                (datetime(2026, 5, 10, 15, 0), 40, 5, 15, 10, 4),
            ]
            atendimentos = []
            for data_hora, duracao, id_paciente, id_residente, id_preceptor, id_unidade in atendimentos_dados:
                a = inserir_atendimento(session, data_hora, duracao, id_paciente, id_residente, id_preceptor, id_unidade)
                atendimentos.append(a)

            #==========================
            # PROCEDIMENTO
            #==========================
            procedimentos_dados = [
                ("PROC001", "Coleta de sangue",             15, "BAIXO", None),
                ("PROC002", "Curativo",                     20, "BAIXO", None),
                ("PROC003", "Raio-X",                        30, "MEDIO", None),
                ("PROC004", "Sutura",                        45, "ALTO",  None),
                ("PROC005", "Intubacao",                     60, "ALTO",  None),
                ("PROC006", "Administracao de medicamento",  10, "BAIXO", None),
            ]
            for codigo, nome, tempo, risco, media in procedimentos_dados:
                inserir_procedimento(session, codigo, nome, tempo, risco, media)

            #==========================
            # PROCEDIMENTO_REALIZADO
            #==========================
            realizados_dados = [
                (1,  1, 1, 18, None,                                    False, datetime(2026, 5, 1, 8, 5)),
                (1,  2, 1, 22, "Curativo simples pos-coleta",           True,  datetime(2026, 5, 1, 8, 25)),
                (2,  6, 2, 12, None,                                    False, datetime(2026, 5, 2, 9, 20)),
                (3,  3, 1, 35, None,                                    False, datetime(2026, 5, 3, 10, 35)),
                (4,  2, 1, 20, None,                                    True,  datetime(2026, 5, 4, 11, 5)),
                (5,  1, 1, 16, None,                                    False, datetime(2026, 5, 5, 14, 5)),
                (6,  6, 1, 10, None,                                    False, datetime(2026, 5, 6, 8, 35)),
                (7,  3, 1, 32, None,                                    True,  datetime(2026, 5, 7, 9, 5)),
                (8,  4, 1, 50, "Paciente com dificuldade respiratoria", False, datetime(2026, 5, 8, 10, 5)),
                (9,  5, 1, 65, "Intercorrencia: queda de saturacao",    False, datetime(2026, 5, 9, 13, 5)),
                (10, 1, 1, 12, None,                                    False, datetime(2026, 5, 10, 15, 5)),
            ]
            for id_atendimento, id_procedimento, qtd, tempo_real, obs, faturado, inicio in realizados_dados:
                inserir_procedimento_realizado(
                    session, id_atendimento, id_procedimento, qtd, tempo_real, obs, inicio, faturado
                )

            #==========================
            # AUDITORIA_ATENDIMENTO (Etapa 2)
            #==========================
            auditorias_dados = [
                (1, 1, "INSERT", "luis.eduardo",
                    datetime(2026, 5, 1, 8, 0, 5),
                    None,
                    {"id_atendimento": 1, "id_paciente": 1, "duracao_minutos": 30}),
                (2, 3, "UPDATE", "luis.eduardo",
                    datetime(2026, 5, 3, 11, 0, 0),
                    {"duracao_minutos": 60},
                    {"duracao_minutos": 75}),
                (3, 9, "DELETE", "admin_sistema",
                    datetime(2026, 5, 9, 16, 0, 0),
                    {"id_atendimento": 9, "id_paciente": 4, "duracao_minutos": 70},
                    None),
            ]
            for id_auditoria, id_atendimento, operacao, usuario, data_hora, antigos, novos in auditorias_dados:
                inserir_auditoria_atendimento(
                    session, id_auditoria, id_atendimento, operacao, usuario, data_hora, antigos, novos
                )

            #==========================
            # INTERNACAO (Etapa 2)
            #==========================
            internacoes_dados = [
                (1, 8, datetime(2026, 5, 8, 10, 30), datetime(2026, 5, 12, 9, 0)),   
                (2, 9, datetime(2026, 5, 9, 13, 40), None),                         
            ]
            for id_internacao, id_atendimento, entrada, saida in internacoes_dados:
                inserir_internacao(session, id_internacao, id_atendimento, entrada, saida)

            session.commit()
            print("[LOG] - Insert executado com sucesso!")

        except Exception as e:
            session.rollback()
            print(f"Erro ao popular banco: {e}")
            raise
