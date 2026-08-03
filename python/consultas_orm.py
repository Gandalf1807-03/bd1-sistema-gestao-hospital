"""
Consultas analíticas via ORM - tradução de consultas.sql (Etapa 1) para SQLAlchemy.
"""

import models as md

from sqlalchemy import select, func, extract, exists, and_, case
from sqlalchemy.orm import Session, aliased
from database import engine


#===============================================================================
# 1: Ranking dos residentes por número de atendimentos realizados
#===============================================================================
def ranking_residentes(session: Session):
    stmt = (
        select(
            md.Residente.id_pessoa.label("id_residente"),
            md.Pessoa.nome.label("nome_residente"),
            func.count().label("total_atendimentos"),
        )
        .join(md.Profissional, md.Residente.id_pessoa == md.Profissional.id_pessoa)
        .join(md.Pessoa, md.Profissional.id_pessoa == md.Pessoa.id_pessoa)
        .join(md.Atendimento, md.Atendimento.id_residente == md.Residente.id_pessoa)
        .group_by(md.Residente.id_pessoa, md.Pessoa.nome)
        .order_by(func.count().desc())
    )
    return session.execute(stmt).all()


#===============================================================================
# 2: Preceptores que supervisionaram mais de 5 atendimentos em um mês
#===============================================================================
def preceptores_acima_de_5_atendimentos(session: Session, mes: int, ano: int):
    stmt = (
        select(
            md.Preceptor.id_pessoa.label("id_preceptor"),
            md.Pessoa.nome.label("nome_preceptor"),
            func.count().label("num_atendimentos"),
        )
        .join(md.Profissional, md.Preceptor.id_pessoa == md.Profissional.id_pessoa)
        .join(md.Pessoa, md.Profissional.id_pessoa == md.Pessoa.id_pessoa)
        .join(md.Atendimento, md.Atendimento.id_preceptor == md.Preceptor.id_pessoa)
        .where(
            extract("month", md.Atendimento.data_hora) == mes,
            extract("year", md.Atendimento.data_hora) == ano,
        )
        .group_by(md.Preceptor.id_pessoa, md.Pessoa.nome)
        .having(func.count() > 5)
        .order_by(func.count().desc())
    )
    return session.execute(stmt).all()


#===============================================================================
# 3: Para cada unidade, plantões escalados por residente no mês corrente
#===============================================================================
# A versão SQL usa generate_series + CTEs para contar quantas vezes cada dia da
# semana ocorre no mês corrente.
# Aqui resolvemos em Python com a biblioteca padrão `calendar`,
# e deixamos só o JOIN/GROUP BY para o ORM.
def plantoes_por_unidade_residente_mes_corrente(session: Session):
    import calendar
    from datetime import date

    hoje = date.today()
    _, dias_no_mes = calendar.monthrange(hoje.year, hoje.month)

    dias_semana_pt = ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA", "SABADO", "DOMINGO"]
    ocorrencias = {dia: 0 for dia in dias_semana_pt}
    for d in range(1, dias_no_mes + 1):
        dia_atual = date(hoje.year, hoje.month, d)
        ocorrencias[dias_semana_pt[dia_atual.weekday()]] += 1

    stmt = (
        select(
            md.Unidade.nome.label("unidade"),
            md.Pessoa.nome.label("residente"),
            md.Escala.dia_semana,
        )
        .join(md.Escala, md.Escala.id_unidade == md.Unidade.id_unidade)
        .join(md.Residente, md.Residente.id_pessoa == md.Escala.id_residente)
        .join(md.Pessoa, md.Pessoa.id_pessoa == md.Residente.id_pessoa)
        .order_by(md.Unidade.nome, md.Pessoa.nome)
    )
    linhas = session.execute(stmt).all()

    resultado = {}
    for unidade, residente, dia_semana in linhas:
        chave = (unidade, residente)
        resultado[chave] = resultado.get(chave, 0) + ocorrencias[dia_semana]

    return [
        {"unidade": u, "residente": r, "qtd_plantoes": qtd}
        for (u, r), qtd in sorted(resultado.items())
    ]


#===============================================================================
# 4: Pacientes que nunca realizaram nenhum procedimento de nível de risco 'ALTO'
#===============================================================================
def pacientes_sem_procedimento_alto_risco(session: Session):
    subquery = (
        select(1)
        .select_from(md.Atendimento)
        .join(md.Procedimento_Realizado,
              md.Procedimento_Realizado.id_atendimento == md.Atendimento.id_atendimento)
        .join(md.Procedimento,
              md.Procedimento.id_procedimento == md.Procedimento_Realizado.id_procedimento)
        .where(
            md.Atendimento.id_paciente == md.Paciente.id_pessoa,
            md.Procedimento.nivel_risco == "ALTO",
        )
    )

    stmt = (
        select(md.Pessoa.nome)
        .join(md.Paciente, md.Paciente.id_pessoa == md.Pessoa.id_pessoa)
        .where(~exists(subquery))
    )
    return session.execute(stmt).scalars().all()


#===============================================================================
# 5: Preceptores que supervisionaram residentes que atenderam pacientes flamenguistas
#===============================================================================
def preceptores_de_flamenguistas(session: Session):
    pessoa_paciente = aliased(md.Pessoa)

    stmt = (
        select(md.Pessoa.nome.label("nome_preceptor"))
        .distinct()
        .join(md.Preceptor, md.Preceptor.id_pessoa == md.Pessoa.id_pessoa)
        .join(md.Atendimento, md.Atendimento.id_preceptor == md.Preceptor.id_pessoa)
        .join(md.Paciente, md.Paciente.id_pessoa == md.Atendimento.id_paciente)
        .join(pessoa_paciente, pessoa_paciente.id_pessoa == md.Paciente.id_pessoa)
        .where(pessoa_paciente.is_flamengo.is_(True))
    )
    return session.execute(stmt).scalars().all()


#===============================================================================
# 6: Último atendimento de cada paciente (data_hora, residente, preceptor, procedimentos)
#===============================================================================
def ultimo_atendimento_por_paciente(session: Session):
    ultima_data_subq = (
        select(
            md.Atendimento.id_paciente,
            func.max(md.Atendimento.data_hora).label("ultima_data"),
        )
        .group_by(md.Atendimento.id_paciente)
        .subquery()
    )

    pessoa_residente = aliased(md.Pessoa)
    pessoa_preceptor = aliased(md.Pessoa)

    stmt = (
        select(
            md.Atendimento.id_atendimento,
            md.Pessoa.nome.label("nome_paciente"),
            md.Atendimento.data_hora,
            pessoa_residente.nome.label("nome_residente"),
            pessoa_preceptor.nome.label("nome_preceptor"),
        )
        .join(md.Paciente, md.Paciente.id_pessoa == md.Pessoa.id_pessoa)
        .join(md.Atendimento, md.Atendimento.id_paciente == md.Paciente.id_pessoa)
        .join(
            ultima_data_subq,
            (ultima_data_subq.c.id_paciente == md.Atendimento.id_paciente)
            & (ultima_data_subq.c.ultima_data == md.Atendimento.data_hora),
        )
        .join(md.Residente, md.Residente.id_pessoa == md.Atendimento.id_residente)
        .join(pessoa_residente, pessoa_residente.id_pessoa == md.Residente.id_pessoa)
        .join(md.Preceptor, md.Preceptor.id_pessoa == md.Atendimento.id_preceptor)
        .join(pessoa_preceptor, pessoa_preceptor.id_pessoa == md.Preceptor.id_pessoa)
        .order_by(md.Pessoa.nome)
    )
    linhas = session.execute(stmt).all()

    resultado = []
    for id_atendimento, nome_paciente, data_hora, nome_residente, nome_preceptor in linhas:
        procs_stmt = (
            select(md.Procedimento.nome)
            .join(
                md.Procedimento_Realizado,
                md.Procedimento_Realizado.id_procedimento == md.Procedimento.id_procedimento,
            )
            .where(md.Procedimento_Realizado.id_atendimento == id_atendimento)
        )
        procedimentos = session.execute(procs_stmt).scalars().all()
        resultado.append(
            (nome_paciente, data_hora, nome_residente, nome_preceptor, procedimentos)
        )
    return resultado


#===============================================================================
# 7: Percentual de procedimentos de alto risco realizados por cada residente
#===============================================================================
def percentual_alto_risco_por_residente(session: Session):
    stmt = (
        select(
            md.Residente.id_pessoa.label("id_residente"),
            md.Pessoa.nome.label("nome_residente"),
            func.sum(md.Procedimento_Realizado.quantidade).label("total"),
            func.sum(
                case(
                    (md.Procedimento.nivel_risco == "ALTO", md.Procedimento_Realizado.quantidade),
                    else_=0,
                )
            ).label("total_alto_risco"),
        )
        .join(md.Profissional, md.Residente.id_pessoa == md.Profissional.id_pessoa)
        .join(md.Pessoa, md.Profissional.id_pessoa == md.Pessoa.id_pessoa)
        .join(md.Atendimento, md.Atendimento.id_residente == md.Residente.id_pessoa)
        .join(
            md.Procedimento_Realizado,
            md.Procedimento_Realizado.id_atendimento == md.Atendimento.id_atendimento,
        )
        .join(md.Procedimento, md.Procedimento.id_procedimento == md.Procedimento_Realizado.id_procedimento)
        .group_by(md.Residente.id_pessoa, md.Pessoa.nome)
    )

    resultado = []
    for id_residente, nome, total, total_alto_risco in session.execute(stmt).all():
        percentual = round(total_alto_risco / total * 100, 2) if total else 0.0
        resultado.append((id_residente, nome, total, total_alto_risco, percentual))
    return resultado


#=======================
# DEMONSTRAÇÃO
#=======================
if __name__ == "__main__":
    with Session(engine) as session:
        print("\n--- 1) Ranking de residentes ---")
        for id_res, nome, total in ranking_residentes(session):
            print(f"{nome} (id={id_res}): {total} atendimentos")

        print("\n--- 2) Preceptores com mais de 5 atendimentos em maio/2026 ---")
        for id_prec, nome, total in preceptores_acima_de_5_atendimentos(session, 5, 2026):
            print(f"{nome} (id={id_prec}): {total} atendimentos")

        print("\n--- 3) Plantões por unidade/residente no mês corrente ---")
        for linha in plantoes_por_unidade_residente_mes_corrente(session):
            print(linha)

        print("\n--- 4) Pacientes sem procedimento de alto risco ---")
        for nome in pacientes_sem_procedimento_alto_risco(session):
            print(nome)

        print("\n--- 5) Preceptores de pacientes flamenguistas ---")
        for nome in preceptores_de_flamenguistas(session):
            print(nome)

        print("\n--- 6) Último atendimento por paciente ---")
        for paciente, data_hora, residente, preceptor, procedimentos in ultimo_atendimento_por_paciente(session):
            print(
                f"{paciente} | {data_hora} | residente: {residente} | "
                f"preceptor: {preceptor} | procedimentos: {', '.join(procedimentos) or '(nenhum)'}"
            )

        print("\n--- 7) Percentual de alto risco por residente ---")
        for id_res, nome, total, total_alto_risco, percentual in percentual_alto_risco_por_residente(session):
            print(f"{nome}: {percentual}% ({total_alto_risco}/{total})")
