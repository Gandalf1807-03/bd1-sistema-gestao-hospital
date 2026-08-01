import streamlit as st

st.set_page_config(
    page_title="Hospital Dra. Yuska",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Sistema de Gestão Hospitalar")
st.subheader("Hospital Universitário Dra. Yuska Maritan Brito")

st.markdown("""
Bem-vindo ao sistema de gestão! 

Utilize o **menu lateral esquerdo** para navegar entre os módulos do sistema:
* **Cadastros:** Inserir pacientes, profissionais e atendimentos via ORM.
* **Relatórios:** Visualizar painéis de internação e estatísticas (Views).
* **Operações Avançadas:** Reajustar escalas e registrar atendimentos (Procedures).
* **Validações:** Testar as regras de negócio e bloqueios do banco (Triggers).
""")