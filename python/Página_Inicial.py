import streamlit as st

st.set_page_config(
    page_title="Hospital Dra. Yuska",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Sistema de Gestão Hospitalar")
st.subheader("Hospital Universitário Dra. Yuska Maritan Brito")

st.markdown("""
Projeto desenvolvido para a cadeira de Banco de Dados I

Equipe:
- Gabriel Lorenzo Xavier
- Jennifer Freire da Costa Silva
- Luis Eduardo Pereira Nunes da Costa
- Thiago Sergio Lima de Oliveira

Utilize o **menu lateral esquerdo** para navegar entre os módulos do sistema:
* **`Operações Avançadas`:** Reajustar escalas e registrar atendimentos (Procedures).
* **`Validações`:** Testar as regras de negócio e bloqueios do banco (Triggers).
* **`Relatórios`:** Visualizar painéis de internação e estatísticas (Views).
* **`Cadastros`:** Inserir pacientes, profissionais e atendimentos via ORM.
""")