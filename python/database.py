from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

"""
[Explicação] - Todas as classes/tabelas vão herdar des-
               sa Base. É ela quem sabe "quais classes
               existem" quando for na hora de gerar o 
               CREATE TABLE.
"""
class Base(DeclarativeBase):
    pass

engine = create_engine("postgresql://luis:edu91814115@localhost/hospital", echo = True)