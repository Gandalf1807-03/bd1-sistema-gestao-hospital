# 🏥 Sistema de Gestão Hospitalar — Dra. Yuska Maritan Brito

Sistema acadêmico de gestão hospitalar desenvolvido para o Hospital Universitário Dra. Yuska Maritan Brito, cobrindo atendimentos, profissionais, pacientes, procedimentos, internações e escalas de plantão.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Modelo de Dados](#modelo-de-dados)
- [Etapa 1 — Fundamentos](#etapa-1--fundamentos)
- [Etapa 2 — Funcionalidades Avançadas](#etapa-2--funcionalidades-avançadas)
- [Instalação e Configuração](#instalação-e-configuração)
- [Execução](#execução)
- [Dados de Teste](#dados-de-teste)
- [Consultas Implementadas](#consultas-implementadas)
- [Decisões de Implementação](#decisões-de-implementação)

---

## Visão Geral

O sistema gerencia o fluxo hospitalar completo:

- Cadastro hierárquico de pessoas (Pacientes e Profissionais)
- Profissionais divididos em Preceptores e Residentes
- Registro de atendimentos com vínculo entre paciente, residente e preceptor
- Procedimentos realizados por atendimento, com métricas de tempo
- Escalas de plantão por unidade, dia e turno
- Auditoria automática de alterações via triggers

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Banco de Dados | PostgreSQL 15+ (ou MySQL 8+) |
| Backend (Etapa 1) | SQL puro |
| Backend (Etapa 2) | Python 3.11+ com SQLAlchemy 2.x |
| ORM alternativa | Node.js + Prisma / Java + Hibernate / C# + EF Core |
| Frontend | CLI / Web (livre) |

---

## Estrutura do Projeto

```
hospital-yuska/
├── etapa1/
│   ├── schema.sql           # CREATE TABLE com todas as constraints
│   ├── seed.sql             # Dados de teste (pacientes, profissionais, etc.)
│   ├── crud.sql             # Operações CRUD em SQL puro
│   └── queries.sql          # Consultas analíticas
├── etapa2/
│   ├── procedures.sql       # Stored procedures
│   ├── triggers.sql         # Triggers de negócio e auditoria
│   ├── views.sql            # Views analíticas
│   ├── orm/
│   │   ├── models.py        # Mapeamento ORM (SQLAlchemy)
│   │   ├── session.py       # Configuração de sessão e engine
│   │   ├── crud_orm.py      # CRUD via ORM
│   │   └── queries_orm.py   # Consultas avançadas via ORM
│   └── concorrencia.py      # Cenário de transações concorrentes
├── docs/
│   ├── DER.pdf              # Diagrama Entidade-Relacionamento
│   ├── modelo_relacional.pdf
│   └── normalizacao.md      # Justificativa de normalização (3FN)
└── README.md
```

---

## Modelo de Dados

### Hierarquia de Entidades

```
PESSOA
├── PACIENTE         (num_convenio, alergias, grupo_sanguineo)
└── PROFISSIONAL     (CRM, data_admissao, especialidade)
      ├── PRECEPTOR  (titulacao)
      └── RESIDENTE  (ano_residencia: R1, R2, R3)
```

### Esquema Relacional

```
PESSOA              (id_pessoa PK, nome, CPF UNIQUE, data_nascimento,
                     is_flamengo, telefone)

PACIENTE            (id_pessoa PK → PESSOA, num_convenio, alergias,
                     grupo_sanguineo)

PROFISSIONAL        (id_pessoa PK → PESSOA, CRM UNIQUE, data_admissao,
                     especialidade)

PRECEPTOR           (id_profissional PK → PROFISSIONAL, titulacao)

RESIDENTE           (id_profissional PK → PROFISSIONAL,
                     ano_residencia CHECK IN ('R1','R2','R3'))

UNIDADE             (id_unidade PK, nome, tipo, capacidade_leitos)

ATENDIMENTO         (id_atendimento PK, data_hora, duracao_minutos,
                     id_paciente FK → PACIENTE,
                     id_residente FK → RESIDENTE,
                     id_preceptor FK → PRECEPTOR)

PROCEDIMENTO        (id_procedimento PK, codigo UNIQUE, nome,
                     tempo_medio_minutos, media_tempo_procedimento)

PROCEDIMENTO_REALIZADO
                    (id_atendimento FK, id_procedimento FK,
                     quantidade, tempo_real_minutos, observacao,
                     PK(id_atendimento, id_procedimento))

ESCALA              (id_escala PK, id_unidade FK, dia_semana, turno,
                     id_residente FK, id_preceptor FK,
                     UNIQUE(id_unidade, dia_semana, turno, id_residente))

AUDITORIA_ATENDIMENTO
                    (id_auditoria PK, id_atendimento, operacao,
                     usuario, data_hora, dados_antigos JSON,
                     dados_novos JSON)
```

---

## Etapa 1 — Fundamentos

### Requisitos

- [x] DER completo com justificativas de cardinalidade
- [x] Modelo relacional com PKs e FKs
- [x] Normalização documentada até 3FN/BCNF
- [x] Script de criação de tabelas com constraints
- [x] Dados de teste (mínimo: 5 pacientes, 5 residentes, 5 preceptores, 3 unidades, 10 atendimentos, 10 procedimentos realizados)
- [x] CRUD em SQL puro
- [x] Consultas analíticas

### CRUD Implementado (`crud.sql`)

| Operação | Descrição |
|---|---|
| INSERT atendimento | Valida existência de paciente, residente e preceptor antes de inserir |
| SELECT atendimentos por paciente | Listagem ordenada por data |
| SELECT procedimentos por atendimento | Com nome, quantidade e tempo real |
| UPDATE paciente | Atualização de convênio ou alergias |
| DELETE procedimento realizado | Somente se não houver faturamento associado (flag) |
| AVG duração por residente | Tempo médio de atendimento agrupado por residente |

### Consultas Analíticas (`queries.sql`)

1. **Ranking de residentes** — por número total de atendimentos realizados
2. **Preceptores ativos** — que supervisionaram mais de 5 atendimentos em um mês específico
3. **Plantões por unidade** — quantidade de escalas por residente no mês corrente
4. **Pacientes sem procedimentos de alto risco** — nunca realizaram procedimento classificado como risco ALTO

---

## Etapa 2 — Funcionalidades Avançadas

### Stored Procedures (`procedures.sql`)

| Procedure | Descrição |
|---|---|
| `sp_registrar_atendimento_completo` | Insere atendimento + procedimentos em transação única; reverte tudo em caso de falha |
| `sp_calcular_tempo_medio_espera` | Calcula, por unidade, o tempo médio entre chegada do paciente e início do primeiro procedimento |
| `sp_reajustar_escala` | Move todas as escalas de um residente de um dia/turno para outro, verificando conflitos |

### Triggers (`triggers.sql`)

| Trigger | Evento | Ação |
|---|---|---|
| `trg_check_sobreposicao_escala` | BEFORE INSERT/UPDATE em ESCALA | Impede que o mesmo residente apareça em dois locais no mesmo dia/turno |
| `trg_audita_atendimento` | AFTER INSERT/UPDATE/DELETE em ATENDIMENTO | Grava registro em `AUDITORIA_ATENDIMENTO` com dados antigos/novos em JSON |
| `trg_atualiza_media_procedimentos` | AFTER INSERT em PROCEDIMENTO_REALIZADO | Recalcula a coluna `media_tempo_procedimento` na tabela PROCEDIMENTO |

### Views (`views.sql`)

| View | Descrição |
|---|---|
| `vw_pacientes_internados` | Pacientes com internação ativa (`data_hora_saida IS NULL`) |
| `vw_residentes_sem_supervisor` | Residentes escalados cujo preceptor não possui titulação de doutor |
| `vw_estatisticas_atendimentos_mensal` | Agregação mensal por unidade: total de atendimentos, duração média, procedimentos mais frequentes |

### ORM — SQLAlchemy (`orm/`)

Todas as operações da Etapa 1 foram reimplementadas usando SQLAlchemy 2.x:

- **`models.py`** — mapeamento objeto-relacional com herança (`PESSOA → PACIENTE / PROFISSIONAL → PRECEPTOR / RESIDENTE`)
- **`session.py`** — configuração de engine e gerenciamento de sessão
- **`crud_orm.py`** — operações CRUD usando a DSL do SQLAlchemy
- **`queries_orm.py`** — consultas avançadas:
  - Preceptores que supervisionaram residentes que atenderam pacientes flamenguistas (`is_flamengo = TRUE`)
  - Último atendimento de cada paciente com residente, preceptor e procedimentos
  - Percentual de procedimentos de alto risco por residente

### Concorrência (`concorrencia.py`)

Simula duas transações concorrentes tentando escalar o mesmo residente para o mesmo dia/turno/unidade, demonstrando:

- Uso de **lock pessimista** (`SELECT FOR UPDATE`) ou **lock otimista** (coluna `versao`)
- Logs de conflito e rollback automático
- Garantia de integridade sem duplicidade de escala

---

## Instalação e Configuração

### Pré-requisitos

- PostgreSQL 15+ instalado e em execução
- Python 3.11+ (para a Etapa 2)
- `pip` ou `poetry`

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/hospital-yuska.git
cd hospital-yuska
```

### 2. Criar o banco de dados

```bash
psql -U postgres -c "CREATE DATABASE hospital_yuska;"
```

### 3. Executar os scripts da Etapa 1

```bash
psql -U postgres -d hospital_yuska -f etapa1/schema.sql
psql -U postgres -d hospital_yuska -f etapa1/seed.sql
```

### 4. Executar os scripts da Etapa 2

```bash
psql -U postgres -d hospital_yuska -f etapa2/views.sql
psql -U postgres -d hospital_yuska -f etapa2/triggers.sql
psql -U postgres -d hospital_yuska -f etapa2/procedures.sql
```

### 5. Instalar dependências Python (Etapa 2)

```bash
cd etapa2
pip install -r requirements.txt
```

Conteúdo do `requirements.txt`:

```
sqlalchemy>=2.0
psycopg2-binary
```

### 6. Configurar variável de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/hospital_yuska
```

---

## Execução

### Etapa 1 — SQL Puro

```bash
# Executar CRUD
psql -U postgres -d hospital_yuska -f etapa1/crud.sql

# Executar consultas analíticas
psql -U postgres -d hospital_yuska -f etapa1/queries.sql
```

### Etapa 2 — ORM e Procedures

```bash
# Operações CRUD via ORM
python etapa2/orm/crud_orm.py

# Consultas avançadas via ORM
python etapa2/orm/queries_orm.py

# Demonstração de concorrência
python etapa2/concorrencia.py
```

---

## Dados de Teste

O arquivo `etapa1/seed.sql` insere:

| Entidade | Quantidade mínima |
|---|---|
| Pacientes | 5 |
| Residentes | 5 (incluindo R1, R2 e R3) |
| Preceptores | 5 (mestres e doutores) |
| Unidades | 3 (Enfermaria, UTI, Pronto-Socorro) |
| Atendimentos | 10 |
| Procedimentos realizados | 10 |
| Escalas de plantão | 6 |

---

## Consultas Implementadas

### Etapa 1

```sql
-- Ranking de residentes por atendimentos
SELECT p.nome, COUNT(a.id_atendimento) AS total_atendimentos
FROM RESIDENTE r
JOIN PESSOA p ON p.id_pessoa = r.id_profissional
JOIN ATENDIMENTO a ON a.id_residente = r.id_profissional
GROUP BY p.nome
ORDER BY total_atendimentos DESC;
```

```sql
-- Preceptores com mais de 5 atendimentos no mês
SELECT p.nome, COUNT(*) AS total
FROM PRECEPTOR pr
JOIN PESSOA p ON p.id_pessoa = pr.id_profissional
JOIN ATENDIMENTO a ON a.id_preceptor = pr.id_profissional
WHERE DATE_TRUNC('month', a.data_hora) = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.nome
HAVING COUNT(*) > 5;
```

### Etapa 2 (ORM)

```python
# Preceptores que supervisionaram residentes de pacientes flamenguistas
session.query(Preceptor).join(Atendimento).join(Paciente).join(Pessoa).filter(
    Pessoa.is_flamengo == True
).distinct().all()
```

---

## Decisões de Implementação

### Herança de tabelas
Adotou-se **herança por tabela concreta com chave compartilhada** (Joined Table Inheritance): `PESSOA` armazena atributos comuns; `PACIENTE` e `PROFISSIONAL` reusam o mesmo `id_pessoa` como PK e FK. Isso mantém integridade referencial sem redundância.

### Triggers vs Stored Procedures
- **Triggers** foram usados para regras automáticas e transparentes ao código da aplicação (auditoria, validação de sobreposição de escala, atualização de médias).
- **Stored Procedures** foram usados para operações transacionais complexas iniciadas explicitamente pela aplicação, oferecendo maior controle sobre o fluxo.

### Escolha da ORM
SQLAlchemy 2.x foi escolhido pela maturidade, suporte nativo a PostgreSQL, controle fino de transações e ampla documentação. O padrão `Session` garante escopo de transação claro, e o sistema de `relationship()` simplifica os joins hierárquicos do modelo.

### Controle de concorrência
Optou-se por **lock pessimista** (`SELECT FOR UPDATE`) na alocação de escala, pois conflitos são esperados em cenários de carga real e o lock otimista geraria muitos rollbacks desnecessários nesse contexto.

---

## Apresentação

- **Etapa 1:** demonstração de 10 minutos cobrindo modelagem, CRUD e consultas analíticas.
- **Etapa 2:** vídeo de até 8 minutos demonstrando triggers, procedures, views, ORM e cenário de concorrência.

Repositório com commits separados por etapa:
- `etapa1/`: fundamentos e SQL puro
- `etapa2/`: funcionalidades avançadas com ORM

---

> Projeto desenvolvido para a disciplina de Banco de Dados — Hospital Universitário Dra. Yuska Maritan Brito.
