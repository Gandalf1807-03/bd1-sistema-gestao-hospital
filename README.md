# 🏥 Sistema de Gestão Hospitalar — Dra. Yuska Maritan Brito

Sistema acadêmico de gestão hospitalar desenvolvido para o Hospital Universitário Dra. Yuska Maritan Brito, cobrindo atendimentos, profissionais, pacientes, procedimentos e escalas de plantão.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Modelo de Dados](#modelo-de-dados)
- [Etapa 1 — Fundamentos](#etapa-1--fundamentos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Executar](#como-executar)
- [Dados de Teste](#dados-de-teste)

---

## Visão Geral

O sistema gerencia o fluxo hospitalar completo:

- Cadastro hierárquico de pessoas (Pacientes e Profissionais)
- Profissionais divididos em Preceptores e Residentes
- Registro de atendimentos com vínculo entre paciente, residente e preceptor
- Procedimentos realizados por atendimento, com métricas de tempo
- Escalas de plantão por unidade, dia e turno

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Banco de Dados | PostgreSQL 15+ |
| Etapa 1 | SQL puro |

---

## Estrutura do Projeto

```
bd1-sistema-gestao-hospital/
├── sql/
│   ├── create_tables.sql   — criação de todas as tabelas com constraints
│   ├── inserts.sql         — dados de teste
│   ├── crud.sql            — operações CRUD em SQL puro
│   └── consultas.sql       — consultas analíticas
└── README.md
```

---

## Modelo de Dados

### Hierarquia de Entidades

```
PESSOA
├── PACIENTE        (num_convenio, grupo_sanguineo)
│   └── PACIENTE_ALERGIAS   (relação 1:N de alergias)
└── PROFISSIONAL    (CRM, data_admissao, especialidade)
      ├── PRECEPTOR (titulacao)
      └── RESIDENTE (ano_residencia: R1, R2, R3)
```

### Esquema Relacional

```
PESSOA                  (id_pessoa PK, nome, CPF UNIQUE, data_nascimento, is_flamengo)

PESSOA_TELEFONES        (id_pessoa FK → PESSOA, telefone, PK(id_pessoa, telefone))

PACIENTE                (id_pessoa PK → PESSOA, num_convenio, grupo_sanguineo)

PACIENTE_ALERGIAS       (id_pessoa FK → PACIENTE, alergia, PK(id_pessoa, alergia))

PROFISSIONAL            (id_pessoa PK → PESSOA, CRM UNIQUE, data_admissao, especialidade)

PRECEPTOR               (id_pessoa PK → PROFISSIONAL, titulacao)

RESIDENTE               (id_pessoa PK → PROFISSIONAL, ano_residencia CHECK IN ('R1','R2','R3'))

UNIDADE                 (id_unidade PK, nome, tipo, capacidade_leitos)

ATENDIMENTO             (id_atendimento PK, data_hora, duracao_minutos,
                         id_paciente FK → PACIENTE,
                         id_residente FK → RESIDENTE,
                         id_preceptor FK → PRECEPTOR)

PROCEDIMENTO            (id_procedimento PK, codigo UNIQUE, nome,
                         tempo_medio_minutos, nivel_risco)

PROCEDIMENTO_REALIZADO  (id_atendimento FK, id_procedimento FK,
                         quantidade, tempo_real_minutos, observacao,
                         is_faturado, PK(id_atendimento, id_procedimento))

ESCALA                  (id_escala PK, id_unidade FK, dia_semana, turno,
                         id_residente FK, id_preceptor FK,
                         UNIQUE(id_unidade, dia_semana, turno, id_residente))
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

### CRUD (`crud.sql`)

| Operação | Descrição |
|----------|-----------|
| INSERT | Inserir novo atendimento validando paciente, residente e preceptor |
| SELECT | Listar atendimentos de um paciente ordenados por data |
| SELECT | Listar procedimentos de um atendimento com nome, quantidade e tempo real |
| UPDATE | Atualizar convênio de um paciente |
| DELETE | Remover procedimento realizado apenas se `is_faturado = FALSE` |
| AVG | Calcular tempo médio de atendimento por residente |

### Consultas Analíticas (`consultas.sql`)

| Consulta | Descrição |
|----------|-----------|
| Ranking | Residentes por número total de atendimentos realizados |
| Preceptores ativos | Que supervisionaram mais de 5 atendimentos em um mês |
| Plantões por unidade | Quantidade de escalas por residente por unidade |
| Pacientes sem risco ALTO | Nunca realizaram procedimento de nível ALTO |

---

## Instalação e Configuração

### Pré-requisitos

PostgreSQL instalado no WSL/Linux. Caso não tenha:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Baixar a extensão PostgreSQL por Chris Kolkman. Para conseguir se conectar: 

```bash

sudo -u postgres psql
ALTER USER postgres PASSWORD '123';

```
---

## Como Executar

**1. Ligar o PostgreSQL**
```bash
sudo service postgresql start
```
**2. Conectar a extensão (transforma os resultados do banco em tabelas visuais e organizadas)**
Deve clicar no ícone de Banco de Dados (elefante) à esquerda do VS Code, clicar no botão "+" e preencher os campos: 

Host: localhost
User: postgres
Password: 123 (ou a senha que você definiu)
Port: 5432

**3. Criar o banco (apenas na primeira vez)**
```bash
sudo -u postgres psql -c "CREATE DATABASE hospital;"
```

**4. Entrar na pasta sql**
```bash
cd sql
```

**5. Criar as tabelas**
```bash
sudo -u postgres psql -d hospital -f create_tables.sql
```

**6. Inserir os dados de teste**
```bash
sudo -u postgres psql -d hospital -f inserts.sql
```

**7. Verificar se tudo foi criado**
```bash
sudo -u postgres psql -d hospital -c "\dt"
```

**8. Executar as consultas analíticas e operações CRUD pelo VS Code**

Para rodar qualquer comando dentro dos arquivos crud.sql ou consultas.sql de forma visual:

1. Abra o arquivo desejado no VS Code.

2. Selecione (grife) com o mouse exatamente a query que deseja executar.

3. Pressione as teclas Ctrl + Shift + E no seu teclado.

O resultado formatado em colunas abrirá instantaneamente na aba da direita (PostgreSQL Results).

---

## Resetar o banco do zero

Se precisar recriar tudo (ex: ao atualizar o schema):

```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS hospital;"
sudo -u postgres psql -c "CREATE DATABASE hospital;"
cd sql
sudo -u postgres psql -d hospital -f create_tables.sql
sudo -u postgres psql -d hospital -f inserts.sql
```

---

## Dados de Teste

O `inserts.sql` popula o banco com:

| Entidade | Quantidade |
|----------|-----------|
| Pessoas | 15 |
| Pacientes | 5 |
| Preceptores | 5 |
| Residentes | 5 |
| Unidades | 4 |
| Escalas | 10 |
| Atendimentos | 10 |
| Procedimentos | 6 |
| Procedimentos Realizados | 11 |

**Destaques dos dados para testes:**
- Paciente 1 possui dois telefones — demonstra a tabela `Pessoa_Telefones`
- Paciente 5 possui três alergias — demonstra a tabela `Paciente_Alergias`
- Paciente 3 sem grupo sanguíneo e paciente 4 sem convênio — demonstra campos opcionais
- Atendimento 1 possui dois procedimentos — permite testar listagem por atendimento
- Paciente 1 aparece em dois atendimentos (01/05 e 06/05) — permite testar listagem por paciente ordenada por data
- Preceptor 6 supervisiona 6 atendimentos em maio — satisfaz a consulta de "mais de 5 atendimentos no mês"
- `is_faturado = FALSE` no registro (atendimento 1, procedimento 1) — pode ser deletado no CRUD
- `is_faturado = TRUE` no registro (atendimento 1, procedimento 2) — bloqueado contra deleção
- Pacientes 1, 2 e 5 nunca realizaram procedimento de risco ALTO — retornam na consulta analítica

---

> Projeto desenvolvido para a disciplina de Banco de Dados I — UFPB.
