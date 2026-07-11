CREATE TABLE Pessoa (

    id_pessoa SERIAL PRIMARY KEY,
    nome    VARCHAR(100) NOT NULL,
    cpf        CHAR(11)  NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    is_flamengo BOOLEAN  DEFAULT FALSE
);

CREATE TABLE Pessoa_Telefones (

    id_pessoa INT NOT NULL,
    telefone VARCHAR(20) NOT NULL,

    PRIMARY KEY (id_pessoa, telefone),
    FOREIGN KEY (id_pessoa)
        REFERENCES Pessoa(id_pessoa)
);

CREATE TABLE Paciente (

    id_pessoa  INT NOT NULL,
    num_convenio VARCHAR(20),
    grupo_sanguineo CHAR(3),

    PRIMARY KEY (id_pessoa),
    FOREIGN KEY (id_pessoa)
        REFERENCES Pessoa(id_pessoa),

    CHECK (grupo_sanguineo IN (
        'A+','A-',
        'B+','B-',
        'AB+','AB-',
        'O+','O-'
        )
    )    
);


CREATE TABLE Paciente_Alergias (

    id_pessoa INT NOT NULL,
    alergia  TEXT NOT NULL,

    PRIMARY KEY (id_pessoa, alergia),
    FOREIGN KEY (id_pessoa)
        REFERENCES Paciente(id_pessoa)
);

CREATE TABLE Profissional (

    id_pessoa INT NOT NULL,
    crm VARCHAR(20) NOT NULL UNIQUE,
    data_admissao DATE NOT NULL,
    especialidade VARCHAR(100) NOT NULL,

    PRIMARY KEY (id_pessoa),

    FOREIGN KEY (id_pessoa)
        REFERENCES Pessoa(id_pessoa)
);

CREATE TABLE Residente (

    id_pessoa INT NOT NULL,
    ano_residencia VARCHAR(2) NOT NULL,

    PRIMARY KEY (id_pessoa),

    FOREIGN KEY (id_pessoa)
        REFERENCES Profissional(id_pessoa),

    CHECK (ano_residencia IN ('R1', 'R2', 'R3'))
);

CREATE TABLE Preceptor (

    id_pessoa INT NOT NULL,
    titulacao VARCHAR(100) NOT NULL,

    PRIMARY KEY (id_pessoa),

    FOREIGN KEY (id_pessoa)
        REFERENCES Profissional(id_pessoa),

    CHECK (titulacao IN (
        'Especialista',
        'Mestre',
        'Doutor'
    ))
);

CREATE TABLE Unidade (

    id_unidade SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    capacidade_leitos INT NOT NULL,

     CHECK (tipo IN (
        'Enfermaria',
        'UTI',
        'Pronto-Socorro',
        'Ambulatorio'
    )),

    CHECK (capacidade_leitos >= 0)
);

CREATE TABLE Escala (

    id_escala SERIAL PRIMARY KEY,

    id_unidade INT NOT NULL,
    dia_semana VARCHAR(15) NOT NULL,
    turno VARCHAR(10) NOT NULL,

    id_residente INT NOT NULL,
    id_preceptor INT NOT NULL,

    FOREIGN KEY (id_unidade)
        REFERENCES Unidade(id_unidade),

    FOREIGN KEY (id_residente)
        REFERENCES Residente(id_pessoa),

    FOREIGN KEY (id_preceptor)
        REFERENCES Preceptor(id_pessoa),

    UNIQUE (id_unidade, dia_semana, turno, id_residente),

    CHECK (dia_semana IN (
        'SEGUNDA',
        'TERCA',
        'QUARTA',
        'QUINTA',
        'SEXTA',
        'SABADO',
        'DOMINGO'
    )),

    CHECK (turno IN ('MANHA', 'TARDE', 'NOITE'))
);


CREATE TABLE Atendimento (

    id_atendimento SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL,
    duracao_minutos INT NOT NULL,

    id_paciente INT NOT NULL,
    id_residente INT NOT NULL,
    id_preceptor INT NOT NULL,

    FOREIGN KEY (id_paciente)
        REFERENCES Paciente(id_pessoa),

    FOREIGN KEY (id_residente)
        REFERENCES Residente(id_pessoa),

    FOREIGN KEY (id_preceptor)
        REFERENCES Preceptor(id_pessoa),

    CHECK (duracao_minutos > 0)
);


CREATE TABLE Procedimento (

    id_procedimento SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    tempo_medio_minutos INT NOT NULL,
    nivel_risco VARCHAR(10) NOT NULL, -- ADICIONADO: Necessário para a consulta analítica 4
    
    CHECK (tempo_medio_minutos > 0),
    CHECK (nivel_risco IN ('BAIXO', 'MEDIO', 'ALTO'))  --ADICIONADO: Restrição de risco
);

CREATE TABLE Procedimento_Realizado (

    id_atendimento INT NOT NULL,
    id_procedimento INT NOT NULL,
    quantidade INT NOT NULL,
    tempo_real_minutos INT NOT NULL,
    observacao TEXT,
    is_faturado BOOLEAN DEFAULT FALSE NOT NULL, -- ADICIONADO: Flag necessária para o CRUD de remoção

    PRIMARY KEY (id_atendimento, id_procedimento),

    FOREIGN KEY (id_atendimento)
        REFERENCES Atendimento(id_atendimento),

    FOREIGN KEY (id_procedimento)
        REFERENCES Procedimento(id_procedimento),

    CHECK (quantidade > 0),
    CHECK (tempo_real_minutos > 0)
);