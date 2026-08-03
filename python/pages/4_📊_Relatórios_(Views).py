import pandas as pd
import streamlit as st
from database import engine 

st.set_page_config(page_title="Relatórios", page_icon="📊")

st.title("📊 Painéis Gerenciais (Views)")

st.subheader("Teste 1: Pacientes atualmente internados")
st.markdown("""```sql
SELECT * FROM vw_pacientes_internados
```
""")
df = pd.read_sql("SELECT * FROM vw_pacientes_internados", engine)
st.dataframe(df)

st.subheader("Teste 2: Residentes sem supervisor Doutor")
st.markdown("""```sql
SELECT * FROM vw_residentes_sem_supervisor
```
""")
df = pd.read_sql("SELECT * FROM vw_residentes_sem_supervisor", engine)
st.dataframe(df)

st.subheader("Teste 3: Estatísticas mensais dos atendimentos")
st.markdown("""```sql
SELECT * FROM vw_estatisticas_atendimentos_mensal
```
""")
df = pd.read_sql("SELECT * FROM vw_estatisticas_atendimentos_mensal", engine)
st.dataframe(df)

st.subheader("Teste 4: Quantidade de pacientes internados")
st.markdown("""```sql
SELECT COUNT(*) AS total_internados
FROM vw_pacientes_internados
```
""")
df = pd.read_sql("""
SELECT COUNT(*) AS total_internados
FROM vw_pacientes_internados""", engine)
st.dataframe(df)
