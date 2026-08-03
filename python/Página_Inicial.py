import streamlit as st

st.set_page_config(
    page_title="Hospital Dra. Yuska",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Sistema de Gestão Hospitalar")
st.subheader("Hospital Universitário Dra. Yuska Maritan Brito")

st.markdown("""
Projeto desenvolvido para a disciplina de Banco de Dados I

Equipe:
- Gabriel Lorenzo Xavier
- Jennifer Freire da Costa Silva
- Luis Eduardo Pereira Nunes da Costa
- Thiago Sergio Lima de Oliveira

Utilize o **menu lateral esquerdo** para navegar entre os módulos do sistema:
* **`1. Visualizar Tabelas`:** Visualização dinâmica das tabelas do BD.
* **`2. Operações Avançadas`:** Reajustar escalas e registrar atendimentos (Procedures).
* **`3. Validações`:** Testar as regras de negócio e bloqueios do banco (Triggers).
* **`4. Relatórios`:** Visualizar painéis de internação e estatísticas (Views).
* **`5. Consultas Analíticas:`** Consultas complexas da etapa 1 reimplementadas com ORM.
* **`6. CRUD`:** Operações básicas da etapa 1 reimplementadas com ORM.
* **`7. Lazy vs Eager Loading`:** Estratégias de carregamento de relacionamentos do SQLAlchemy.
* **`8. Teste de Concorrência`:** Aplicação de processos concorrentes ao BD.
""")