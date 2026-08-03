from datetime import date, datetime

from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    Boolean,
    Text,
    Numeric,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from database import Base, engine

#Base = declarative_base()

class Pessoa(Base):
    __tablename__ = "pessoa"

    id_pessoa       : Mapped[int]  = mapped_column(primary_key=True)
    nome            : Mapped[str]  = mapped_column(String(100), 
                                                   nullable=False)
    cpf             : Mapped[str]  = mapped_column(String(11), 
                                                   nullable=False, 
                                                   unique=True)
    data_nascimento : Mapped[date] = mapped_column(Date, 
                                                   nullable=False)
    is_flamengo     : Mapped[bool] = mapped_column(Boolean, 
                                                   default=False)

    #============================================================
    #Relationships (Etapa 2 - necessário p/ demonstrar lazy/eager loading)
    #============================================================
    telefones : Mapped[list["Pessoa_Telefone"]] = relationship(
        back_populates="pessoa", lazy="select"  # lazy: só busca telefones quando acessado
    )
    #Ligação 1-para-1 com o "papel" que essa pessoa ocupa (pode não existir nenhum dos dois)
    paciente : Mapped["Paciente"] = relationship(back_populates="pessoa", uselist=False)
    profissional : Mapped["Profissional"] = relationship(back_populates="pessoa", uselist=False)


class Pessoa_Telefone(Base):
    __tablename__ = "pessoa_telefones"

    id_pessoa: Mapped[int] = mapped_column(ForeignKey("pessoa.id_pessoa"), 
                                           primary_key=True)
    
    telefone : Mapped[str] = mapped_column(String(20), 
                                           primary_key=True)

    pessoa : Mapped["Pessoa"] = relationship(back_populates="telefones")


class Paciente(Base):
    __tablename__ = "paciente"

    id_pessoa       : Mapped[int] = mapped_column(ForeignKey("pessoa.id_pessoa"), 
                                                  primary_key=True)
    num_convenio    : Mapped[str] = mapped_column(String(20), 
                                                  nullable=True)
    grupo_sanguineo : Mapped[str] = mapped_column(String(3), 
                                                  nullable=True)

    __table_args__ = (
        CheckConstraint(
            "grupo_sanguineo IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')",
            name="check_grupo_sanguineo",
        ),
    )

    pessoa    : Mapped["Pessoa"] = relationship(back_populates="paciente")
    alergias  : Mapped[list["Paciente_Alergia"]] = relationship(back_populates="paciente")
    #Todos os atendimentos desse paciente (útil pro CRUD #2 e p/ demonstrar lazy loading)
    atendimentos : Mapped[list["Atendimento"]] = relationship(back_populates="paciente")


class Paciente_Alergia(Base):
    __tablename__ = "paciente_alergias"

    id_pessoa : Mapped[int] = mapped_column(ForeignKey("paciente.id_pessoa"), 
                                            primary_key=True)
    alergia   : Mapped[str] = mapped_column(Text, 
                                            primary_key=True)

    paciente : Mapped["Paciente"] = relationship(back_populates="alergias")


class Profissional(Base):
    __tablename__ = "profissional"

    id_pessoa      : Mapped[int] = mapped_column(ForeignKey("pessoa.id_pessoa"), 
                                                 primary_key=True)
    crm            : Mapped[str] = mapped_column(String(20), 
                                                 nullable=False, 
                                                 unique=True)
    data_admissao  : Mapped[date] = mapped_column(Date, 
                                                 nullable=False)
    especialidade  : Mapped[str] = mapped_column(String(100), 
                                                 nullable=False)

    pessoa     : Mapped["Pessoa"] = relationship(back_populates="profissional")
    residente  : Mapped["Residente"] = relationship(back_populates="profissional", uselist=False)
    preceptor  : Mapped["Preceptor"] = relationship(back_populates="profissional", uselist=False)


class Residente(Base):
    __tablename__ = "residente"

    id_pessoa       : Mapped[int] = mapped_column(ForeignKey("profissional.id_pessoa"), 
                                                  primary_key=True)
    ano_residencia  : Mapped[str] = mapped_column(String(2), 
                                                  nullable=False)

    __table_args__ = (
        CheckConstraint("ano_residencia IN ('R1','R2','R3')", name="check_ano_residencia"),
    )

    profissional : Mapped["Profissional"] = relationship(back_populates="residente")
    escalas      : Mapped[list["Escala"]] = relationship(back_populates="residente")
    #eager por padrão (joinedload) -> pensado p/ comparar com o "atendimentos" do Preceptor, que fica lazy
    atendimentos : Mapped[list["Atendimento"]] = relationship(
        back_populates="residente", lazy="joined"
    )


class Preceptor(Base):
    __tablename__ = "preceptor"

    id_pessoa   : Mapped[int] = mapped_column(ForeignKey("profissional.id_pessoa"), 
                                              primary_key=True)
    titulacao   : Mapped[str] = mapped_column(String(100), 
                                              nullable=False)

    __table_args__ = (
        CheckConstraint(
            "titulacao IN ('Especialista','Mestre','Doutor')",
            name="check_titulacao",
        ),
    )

    profissional : Mapped["Profissional"] = relationship(back_populates="preceptor")
    escalas      : Mapped[list["Escala"]] = relationship(back_populates="preceptor")
    atendimentos : Mapped[list["Atendimento"]] = relationship(back_populates="preceptor")


class Unidade(Base):
    __tablename__ = "unidade"

    id_unidade         : Mapped[int] = mapped_column(primary_key=True)
    nome               : Mapped[str] = mapped_column(String(100), 
                                                    nullable=False)
    tipo               : Mapped[str] = mapped_column(String(50), 
                                                    nullable=False)
    capacidade_leitos  : Mapped[int] = mapped_column(Integer, 
                                                    nullable=False)

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Enfermaria','UTI','Pronto-Socorro','Ambulatorio')",
            name="check_tipo_unidade",
        ),
        CheckConstraint("capacidade_leitos >= 0", name="check_capacidade_leitos"),
    )

    escalas       : Mapped[list["Escala"]] = relationship(back_populates="unidade")
    atendimentos  : Mapped[list["Atendimento"]] = relationship(back_populates="unidade")


class Escala(Base):
    __tablename__ = "escala"

    id_escala    : Mapped[int] = mapped_column(primary_key=True)
    id_unidade   : Mapped[int] = mapped_column(ForeignKey("unidade.id_unidade"), 
                                               nullable=False)
    dia_semana   : Mapped[str] = mapped_column(String(15), 
                                               nullable=False)
    turno        : Mapped[str] = mapped_column(String(10), 
                                               nullable=False)
    id_residente : Mapped[int] = mapped_column(ForeignKey("residente.id_pessoa"), 
                                               nullable=False)
    id_preceptor : Mapped[int] = mapped_column(ForeignKey("preceptor.id_pessoa"), 
                                               nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id_unidade", "dia_semana", "turno", "id_residente",
            name="unique_escala",
        ),
        CheckConstraint(
            "dia_semana IN ('SEGUNDA','TERCA','QUARTA','QUINTA','SEXTA','SABADO','DOMINGO')",
            name="check_dia_semana",
        ),
        CheckConstraint("turno IN ('MANHA','TARDE','NOITE')", name="check_turno"),
    )

    unidade   : Mapped["Unidade"] = relationship(back_populates="escalas")
    residente : Mapped["Residente"] = relationship(back_populates="escalas")
    preceptor : Mapped["Preceptor"] = relationship(back_populates="escalas")


class Atendimento(Base):
    __tablename__ = "atendimento"

    id_atendimento  : Mapped[int] = mapped_column(primary_key=True)
    data_hora       : Mapped[datetime] = mapped_column(DateTime, 
                                                  nullable=False)
    duracao_minutos : Mapped[int] = mapped_column(Integer, 
                                                  nullable=False)
    id_paciente     : Mapped[int] = mapped_column(ForeignKey("paciente.id_pessoa"), 
                                                  nullable=False)
    id_residente    : Mapped[int] = mapped_column(ForeignKey("residente.id_pessoa"), 
                                                  nullable=False)
    id_preceptor    : Mapped[int] = mapped_column(ForeignKey("preceptor.id_pessoa"), 
                                                  nullable=False)
    
    #ADICIONADO na Etapa 2 (changes-etapa-2.sql)
    id_unidade      : Mapped[int] = mapped_column(ForeignKey("unidade.id_unidade"), 
                                                  nullable=False)

    __table_args__ = (
        CheckConstraint("duracao_minutos > 0", name="check_duracao_minutos"),
    )

    paciente   : Mapped["Paciente"] = relationship(back_populates="atendimentos")
    residente  : Mapped["Residente"] = relationship(back_populates="atendimentos")
    preceptor  : Mapped["Preceptor"] = relationship(back_populates="atendimentos")
    unidade    : Mapped["Unidade"] = relationship(back_populates="atendimentos")
    internacao : Mapped["Internacao"] = relationship(back_populates="atendimento", uselist=False)
    #Procedimentos feitos nesse atendimento (join com Procedimento via Procedimento_Realizado)
    procedimentos_realizados : Mapped[list["Procedimento_Realizado"]] = relationship(
        back_populates="atendimento"
    )


class Procedimento(Base):
    __tablename__ = "procedimento"

    id_procedimento          : Mapped[int] = mapped_column(primary_key=True)
    codigo                   : Mapped[str] = mapped_column(String(20), 
                                                      nullable=False, 
                                                      unique=True)
    nome                     : Mapped[str] = mapped_column(String(100), 
                                                      nullable=False)
    tempo_medio_minutos      : Mapped[int] = mapped_column(Integer, 
                                                      nullable=False)
    nivel_risco              : Mapped[str] = mapped_column(String(10), 
                                                      nullable=False)
    
    #ADICIONADO na Etapa 2: preenchida pela trigger trg_atualiza_media_procedimentos
    media_tempo_procedimento : Mapped[float] = mapped_column(Numeric(10, 2), 
                                                             nullable=True)

    __table_args__ = (
        CheckConstraint("tempo_medio_minutos > 0", name="check_tempo_medio_minutos"),
        CheckConstraint("nivel_risco IN ('BAIXO','MEDIO','ALTO')", name="check_nivel_risco"),
    )

    realizacoes : Mapped[list["Procedimento_Realizado"]] = relationship(back_populates="procedimento")


class Procedimento_Realizado(Base):
    __tablename__ = "procedimento_realizado"

    id_atendimento      : Mapped[int] = mapped_column(ForeignKey("atendimento.id_atendimento"), 
                                                      primary_key=True)
    id_procedimento     : Mapped[int] = mapped_column(ForeignKey("procedimento.id_procedimento"), 
                                                      primary_key=True)
    quantidade          : Mapped[int] = mapped_column(Integer, 
                                                      nullable=False)
    tempo_real_minutos  : Mapped[int] = mapped_column(Integer, 
                                                      nullable=False)
    observacao          : Mapped[str] = mapped_column(Text, 
                                                      nullable=True)
    is_faturado         : Mapped[bool] = mapped_column(Boolean, 
                                                      default=False, 
                                                      nullable=False)
    
    #ADICIONADO na Etapa 2: usada por sp_calcular_tempo_medio_espera
    data_hora_inicio    : Mapped[datetime] = mapped_column(DateTime, 
                                                           nullable=False)

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="check_quantidade"),
        CheckConstraint("tempo_real_minutos > 0", name="check_tempo_real_minutos"),
    )

    atendimento  : Mapped["Atendimento"] = relationship(back_populates="procedimentos_realizados")
    procedimento : Mapped["Procedimento"] = relationship(back_populates="realizacoes")


#============================================================
#Tabelas novas da Etapa 2 (criadas em changes-etapa-2.sql)
#============================================================


class Auditoria_Atendimento(Base):
    __tablename__ = "auditoria_atendimento"

    id_auditoria    : Mapped[int] = mapped_column(primary_key=True)
    id_atendimento  : Mapped[int] = mapped_column(Integer, 
                                                  nullable=True)
    operacao        : Mapped[str] = mapped_column(String(10), 
                                                  nullable=False)
    usuario         : Mapped[str] = mapped_column(String(100), 
                                                  nullable=False)
    data_hora       : Mapped[datetime] = mapped_column(DateTime, 
                                                  nullable=False)
    dados_antigos   : Mapped[dict] = mapped_column(JSONB, 
                                                  nullable=True)
    dados_novos     : Mapped[dict] = mapped_column(JSONB, 
                                                  nullable=True)

    __table_args__ = (
        CheckConstraint("operacao IN ('INSERT','UPDATE','DELETE')", name="check_operacao"),
    )


class Internacao(Base):
    __tablename__ = "internacao"

    id_internacao     : Mapped[int] = mapped_column(primary_key=True)
    id_atendimento    : Mapped[int] = mapped_column(ForeignKey("atendimento.id_atendimento"), 
                                                    nullable=False,
                                                    unique=True)
    data_hora_entrada : Mapped[datetime] = mapped_column(DateTime, 
                                                        nullable=False)
    data_hora_saida   : Mapped[datetime] = mapped_column(DateTime, 
                                                        nullable=True)

    __table_args__ = (
        CheckConstraint(
            "data_hora_saida IS NULL OR data_hora_saida >= data_hora_entrada",
            name="check_data_hora_saida",
        ),
    )

    atendimento : Mapped["Atendimento"] = relationship(back_populates="internacao")


Base.metadata.create_all(engine)