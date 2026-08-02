from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

"""
[Explicação] - Todas as classes/tabelas vão herdar des-
               sa Base. É ela quem sabe "quais classes
               existem" quando for na hora de gerar o 
               CREATE TABLE.
"""
class Base(DeclarativeBase):
    pass

engine = create_engine("postgresql://postgres:123@localhost/hospital", echo = True)

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()
