import sys
import multiprocessing
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from database import engine
import models as md
from insert import inserir_escala


#==================================================
""" CENÁRIO OTIMISTA
 Nenhum lock explícito: os dois processos tentam
 inserir ao mesmo tempo, e o UniqueConstraint do
 banco resolve o conflito no momento do commit.
"""
#==================================================
def tentar_escalar_otimista(nome_processo, barreira):
    engine.dispose()
    with Session(engine) as session:
        try:
            barreira.wait()
            print(f"[{nome_processo}] (OTIMISTA) Tentando escalar...")

            escala = inserir_escala(
                session,
                id_unidade=1,
                dia_semana="SEGUNDA",
                turno="MANHA",
                id_residente=11,
                id_preceptor=6
            )
            session.commit()
            print(f"[{nome_processo}] SUCESSO — escala id={escala.id_escala} criada")

        except IntegrityError as e:
            session.rollback()
            print(f"[{nome_processo}] FALHOU — violação de unique_escala: {e.orig}")


#==================================================
"""CENÁRIO PESSIMISTA
Trava a linha da Unidade antes de verificar/inserir,
forçando o segundo processo a esperar o primeiro
terminar antes de sequer checar o conflito.
"""
#==================================================
def tentar_escalar_pessimista(nome_processo, barreira):
    engine.dispose()
    with Session(engine) as session:
        barreira.wait()
        print(f"[{nome_processo}] (PESSIMISTA) Tentando escalar...")

        stmt = select(md.Unidade).where(md.Unidade.id_unidade == 1).with_for_update()
        session.execute(stmt).scalar_one()

        print(f"[{nome_processo}] Lock adquirido, verificando conflito...")

        ja_existe = session.execute(
            select(md.Escala).where(
                md.Escala.id_unidade == 1,
                md.Escala.dia_semana == "SEGUNDA",
                md.Escala.turno == "MANHA",
                md.Escala.id_residente == 11,
            )
        ).first()

        if ja_existe:
            print(f"[{nome_processo}] Já existe escala — abortando")
            session.rollback()
            return

        escala = inserir_escala(session, 1, "SEGUNDA", "MANHA", 11, 6)
        session.commit()
        print(f"[{nome_processo}] SUCESSO — escala id={escala.id_escala} criada")


#==================================================
# ORQUESTRAÇÃO
#==================================================
CENARIOS = {
    "otimista": tentar_escalar_otimista,
    "pessimista": tentar_escalar_pessimista,
}


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CENARIOS:
        print("Uso: python3 simulacaoOP.py [otimista|pessimista]")
        sys.exit(1)

    cenario = sys.argv[1]
    funcao_alvo = CENARIOS[cenario]

    print(f"=== Executando cenário: {cenario.upper()} ===\n")

    barreira = multiprocessing.Barrier(2)

    p1 = multiprocessing.Process(target=funcao_alvo, args=("Processo A", barreira))
    p2 = multiprocessing.Process(target=funcao_alvo, args=("Processo B", barreira))

    p1.start()
    p2.start()
    p1.join()
    p2.join()