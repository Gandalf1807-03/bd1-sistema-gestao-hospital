import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

load_dotenv()

class Base(DeclarativeBase):
    pass

usuario = os.getenv("DB_USER")
senha = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
banco = os.getenv("DB_NAME")

engine = create_engine(f"postgresql://{usuario}:{senha}@{host}/{banco}", echo=True)

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()
