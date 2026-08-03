"""
Demonstração de LAZY LOADING vs EAGER LOADING.
Para ver a diferença de verdade, rodamos com echo=True no engine (já está
configurado em database.py) e olhamos quantos SELECTs aparecem no console.
"""

import models as md

from sqlalchemy.orm import Session, joinedload, selectinload
from database import engine


def demo_lazy(session: Session):
    print("\n========== LAZY LOADING ==========")
    atendimento = session.get(md.Atendimento, 1)
    print(">>> Atendimento carregado. Ainda NÃO buscamos o paciente.")

    print(">>> Acessando atendimento.paciente agora (dispara um 2º SELECT):")
    paciente = atendimento.paciente
    print(f"Paciente: {paciente.pessoa.nome if paciente.pessoa else paciente.id_pessoa}")


def demo_eager_joinedload(session: Session):
    print("\n========== EAGER LOADING (joinedload) ==========")
    stmt = (
        session.query(md.Atendimento)
        .options(joinedload(md.Atendimento.paciente).joinedload(md.Paciente.pessoa))
        .filter(md.Atendimento.id_atendimento == 1)
    )
    atendimento = stmt.first()
    print(">>> Atendimento + paciente já vieram juntos, em 1 único SELECT.")
    print(f"Paciente: {atendimento.paciente.pessoa.nome}")


def demo_eager_selectinload(session: Session):
    print("\n========== EAGER LOADING (selectinload) ==========")
    stmt = (
        session.query(md.Residente)
        .options(selectinload(md.Residente.atendimentos))
    )
    residentes = stmt.all()
    print(">>> Residentes + todos os atendimentos de cada um já carregados.")
    for r in residentes:
        print(f"Residente {r.id_pessoa}: {len(r.atendimentos)} atendimento(s)")


if __name__ == "__main__":
    with Session(engine) as session:
        demo_lazy(session)
        demo_eager_joinedload(session)
        demo_eager_selectinload(session)
