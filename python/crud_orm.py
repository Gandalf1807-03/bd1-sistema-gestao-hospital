"""
CRUD via ORM - tradução das 6 operações de crud.sql (Etapa 1) para SQLAlchemy.

Cada função corresponde a UM bloco do crud.sql, na mesma ordem, para
facilitar a comparação SQL puro x ORM no relatório/demonstração.
"""

import models as md

from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database import engine


#===============================================================================
# 1: Inserir um novo atendimento (verificando se paciente, residente, preceptor existem)
#===============================================================================
def inserir_atendimento_verificado(session: Session, data_hora, duracao_minutos,
                                    id_paciente, id_residente, id_preceptor, id_unidade):
    # Em SQL puro isso seria feito com 3 SELECTs manuais antes do INSERT.
    # No ORM, session.get(Classe, chave_primaria) já faz esse SELECT por PK.
    paciente = session.get(md.Paciente, id_paciente)
    residente = session.get(md.Residente, id_residente)
    preceptor = session.get(md.Preceptor, id_preceptor)

    if paciente is None:
        raise ValueError(f"Paciente {id_paciente} não existe.")
    if residente is None:
        raise ValueError(f"Residente {id_residente} não existe.")
    if preceptor is None:
        raise ValueError(f"Preceptor {id_preceptor} não existe.")

    atendimento = md.Atendimento(
        data_hora=data_hora,
        duracao_minutos=duracao_minutos,
        id_paciente=id_paciente,
        id_residente=id_residente,
        id_preceptor=id_preceptor,
        id_unidade=id_unidade,
    )
    session.add(atendimento)
    session.flush()  # gera o id_atendimento sem precisar dar commit ainda
    return atendimento


#===============================================================================
# 2: Listar todos os atendimentos de um paciente específico (ordenados por data)
#===============================================================================
def listar_atendimentos_paciente(session: Session, id_paciente):
    stmt = (
        select(md.Atendimento)
        .where(md.Atendimento.id_paciente == id_paciente)
        .order_by(md.Atendimento.data_hora.asc())
    )
    return session.execute(stmt).scalars().all()


#===============================================================================
# 3: Listar os procedimentos realizados em um atendimento
#    (nome do procedimento, quantidade e tempo real)
#===============================================================================
def listar_procedimentos_do_atendimento(session: Session, id_atendimento):
    # equivalente ao JOIN entre Procedimento e Procedimento_Realizado do SQL puro
    stmt = (
        select(md.Procedimento.nome, md.Procedimento_Realizado.quantidade,
               md.Procedimento_Realizado.tempo_real_minutos)
        .join(md.Procedimento_Realizado,
              md.Procedimento_Realizado.id_procedimento == md.Procedimento.id_procedimento)
        .where(md.Procedimento_Realizado.id_atendimento == id_atendimento)
    )
    return session.execute(stmt).all()


#===============================================================================
# 4: Atualizar os dados de um paciente (convênio)
#===============================================================================
def atualizar_convenio_paciente(session: Session, id_paciente, novo_convenio):
    paciente = session.get(md.Paciente, id_paciente)
    if paciente is None:
        raise ValueError(f"Paciente {id_paciente} não existe.")

    paciente.num_convenio = novo_convenio
    session.flush()
    return paciente


#===============================================================================
# 5: Remover um procedimento realizado (apenas se is_faturado = FALSE)
#===============================================================================
def remover_procedimento_realizado(session: Session, id_atendimento, id_procedimento):
    registro = session.get(md.Procedimento_Realizado, (id_atendimento, id_procedimento))

    if registro is None:
        raise ValueError("Procedimento realizado não encontrado.")
    if registro.is_faturado:
        raise ValueError("Não é possível remover: procedimento já faturado.")

    session.delete(registro)
    session.flush()


#===============================================================================
# 6: Calcular o tempo médio de duração dos atendimentos por residente
#===============================================================================
def tempo_medio_por_residente(session: Session):
    stmt = (
        select(
            md.Pessoa.nome.label("nome_residente"),
            md.Residente.id_pessoa,
            func.round(func.avg(md.Atendimento.duracao_minutos), 2).label("tempo_medio_minutos"),
            func.count(md.Atendimento.id_atendimento).label("total_atendimentos"),
        )
        .join(md.Residente, md.Atendimento.id_residente == md.Residente.id_pessoa)
        .join(md.Pessoa, md.Residente.id_pessoa == md.Pessoa.id_pessoa)
        .group_by(md.Pessoa.nome, md.Residente.id_pessoa)
        .order_by(func.avg(md.Atendimento.duracao_minutos).desc())
    )
    return session.execute(stmt).all()


#=======================
# DEMONSTRAÇÃO
#=======================
if __name__ == "__main__":
    with Session(engine) as session:
        print("\n--- 1) Inserir atendimento verificado ---")
        novo = inserir_atendimento_verificado(
            session, datetime(2026, 7, 12, 19, 0), 60, 5, 14, 8, 4
        )
        print(f"Atendimento criado: id={novo.id_atendimento}")

        print("\n--- 2) Atendimentos do paciente 1 ---")
        for a in listar_atendimentos_paciente(session, 1):
            print(a.id_atendimento, a.data_hora)

        print("\n--- 3) Procedimentos do atendimento 2 ---")
        for nome, qtd, tempo in listar_procedimentos_do_atendimento(session, 2):
            print(nome, qtd, tempo)

        print("\n--- 4) Atualizar convênio do paciente 4 ---")
        atualizar_convenio_paciente(session, 4, "CONV-004")

        print("\n--- 5) Remover procedimento realizado (1, 1) se não faturado ---")
        try:
            remover_procedimento_realizado(session, 1, 1)
            print("Removido com sucesso.")
        except ValueError as e:
            print(f"Não removido: {e}")

        print("\n--- 6) Tempo médio por residente ---")
        for nome, id_residente, media, total in tempo_medio_por_residente(session):
            print(f"{nome} (id={id_residente}): média={media} min, total={total}")

        session.rollback()  # não persiste as alterações de teste; troque por commit() se quiser salvar
