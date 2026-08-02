"""
Consultas analíticas via ORM - tradução de consultas.sql (Etapa 1) para SQLAlchemy.
"""

import models as md

from sqlalchemy import select, func, extract, exists, and_
from sqlalchemy.orm import Session
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
# semana ocorre no mês corrente. Isso é lógica bem específica do PostgreSQL, então
# aqui resolvemos a parte de "quantos dias de cada tipo há no mês" em Python com
# a biblioteca padrão `calendar`, e deixamos só o JOIN/GROUP BY para o ORM.
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

    # agrega em Python usando o dicionário de ocorrências calculado acima
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
    # equivalente ao NOT EXISTS do SQL puro
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
