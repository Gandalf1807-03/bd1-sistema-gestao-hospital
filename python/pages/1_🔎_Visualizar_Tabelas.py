import pandas as pd
import streamlit as st
from database import engine

st.set_page_config(page_title="Visualizador de Tabelas", page_icon="🔍")
st.title("🔍 Visualização de Tabelas")

st.markdown(
    "Selecione as tabelas abaixo. Elas aparecerão automaticamente na tela:"
)

# Lista de tabelas oficiais do seu projeto hospitalar
tabelas_disponiveis = [
    "Pessoa",
    "Pessoa_Telefones",
    "Paciente",
    "Paciente_Alergias",
    "Profissional",
    "Residente",
    "Preceptor",
    "Unidade",
    "Escala",
    "Atendimento",
    "Procedimento",
    "Procedimento_Realizado",
    "Auditoria_Atendimento",
    "Internacao"
]

# 1. O multiselect fica solto na tela, sem formulário
tabelas_selecionadas = st.multiselect(
    label="Escolha as tabelas:",
    options=tabelas_disponiveis,
    placeholder="Clique aqui para escolher...",
)

# 2. Assim que o usuário escolhe, o código abaixo roda sozinho na mesma hora!
if tabelas_selecionadas:

  # Faz um loop pelas tabelas que o usuário marcou
  for tabela in tabelas_selecionadas:
    st.divider()
    st.subheader(f"📊 Tabela: `{tabela}`")

    try:
      # Busca os dados no PostgreSQL imediatamente
      df = pd.read_sql(f"SELECT * FROM {tabela}", con=engine)

      if not df.empty:
        st.dataframe(df, use_container_width=True)
      else:
        st.info(f"A tabela `{tabela}` está vazia no momento.")

    except Exception as e:
      st.error(f"Erro ao buscar os dados da tabela `{tabela}`: {e}")
else:
  st.info("👈 Nenhuma tabela selecionada. Escolha alguma acima para visualizar.")