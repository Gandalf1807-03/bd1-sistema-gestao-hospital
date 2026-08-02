"""
Demonstração de LAZY LOADING vs EAGER LOADING (exigido no item 4 da Etapa 2).

Conceito, em uma frase:
- LAZY  = o ORM só busca o relacionamento no banco quando você acessa o atributo
          (gera um SELECT extra, "sob demanda").
- EAGER = o ORM já traz o relacionamento junto na consulta principal
          (um único SELECT com JOIN, ou um SELECT adicional já disparado de propósito).

Para ver a diferença de verdade, rodamos com echo=True no engine (já está
configurado em database.py) e olhamos quantos SELECTs aparecem no console.
"""

import models as md

from sqlalchemy.orm import Session, joinedload, selectinload
from database import engine


def demo_lazy(session: Session):
    print("\n========== LAZY LOADING ==========")
    # Busca só o atendimento. Repare no SQL: NÃO tem join com paciente.
    atendimento = session.get(md.Atendimento, 1)
    print(">>> Atendimento carregado. Ainda NÃO buscamos o paciente.")

    # Só quando acessamos ".paciente" o SQLAlchemy dispara um SELECT novo.
    print(">>> Acessando atendimento.paciente agora (dispara um 2º SELECT):")
    paciente = atendimento.paciente
    print(f"Paciente: {paciente.pessoa.nome if paciente.pessoa else paciente.id_pessoa}")


def demo_eager_joinedload(session: Session):
    print("\n========== EAGER LOADING (joinedload) ==========")
    # Aqui pedimos explicitamente para já trazer o paciente (e a pessoa dele)
    # na MESMA consulta, via LEFT OUTER JOIN. Repare que só aparece 1 SELECT.
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
    # selectinload é melhor quando o relacionamento é 1-para-MUITOS (evita
    # duplicar linhas como o joinedload faria). Ainda é "eager": os dados já
    # vêm carregados antes de você precisar deles, só que em um 2º SELECT
    # separado (com IN), disparado de forma antecipada e única (não um por linha).
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
