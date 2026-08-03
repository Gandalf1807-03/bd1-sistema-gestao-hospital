import streamlit as st
import pandas as pd
from database import engine, get_session
import consultas_orm as c_orm

st.set_page_config(page_title="Consultas Analíticas", layout="wide")
st.title("📈 Consultas Analíticas")
st.markdown("Selecione a consulta abaixo para gerar o relatório em tempo real baseado no banco de dados.")

opcoes_relatorio = [
    "1. Ranking de Residentes",
    "2. Preceptores com +5 atendimentos (Mensal)",
    "3. Plantões por Unidade/Residente (Mês Corrente)",
    "4. Pacientes sem procedimentos de alto risco",
    "5. Preceptores de pacientes flamenguistas",
    "6. Último atendimento por paciente",
    "7. Percentual de alto risco por residente"
]

escolha = st.selectbox("Escolha o Relatório:", opcoes_relatorio)
st.divider()

# Inicia a sessão e exibe o relatório selecionado
session = get_session()
with session:
    
    if escolha == opcoes_relatorio[0]:
        st.subheader("Ranking de Residentes")
        dados = c_orm.ranking_residentes(session)
        if dados:
            df = pd.DataFrame(dados, columns=["ID", "Nome do Residente", "Total de Atendimentos"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado encontrado.")

    elif escolha == opcoes_relatorio[1]:
        st.subheader("Preceptores (+5 atendimentos)")
        
        col1, col2 = st.columns(2)
        mes = col1.number_input("Mês", min_value=1, max_value=12, value=5)
        ano = col2.number_input("Ano", min_value=2000, max_value=2100, value=2026)
        
        dados = c_orm.preceptores_acima_de_5_atendimentos(session, mes, ano)
        if dados:
            df = pd.DataFrame(dados, columns=["ID", "Nome do Preceptor", "Total de Atendimentos"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Nenhum preceptor atingiu mais de 5 atendimentos em {mes}/{ano}.")

    elif escolha == opcoes_relatorio[2]:
        st.subheader("Plantões por Unidade/Residente (Mês Corrente)")
        dados = c_orm.plantoes_por_unidade_residente_mes_corrente(session)
        if dados:
            df = pd.DataFrame(dados)
            df = df.rename(columns={"unidade": "Unidade", "residente": "Residente", "qtd_plantoes": "Qtd Plantões"})
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum plantão agendado para o mês corrente.")

    elif escolha == opcoes_relatorio[3]:
        st.subheader("Pacientes (Sem procedimentos de alto risco)")
        dados = c_orm.pacientes_sem_procedimento_alto_risco(session)
        if dados:
            df = pd.DataFrame(dados, columns=["Nome do Paciente"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Todos os pacientes realizaram procedimentos de alto risco.")

    elif escolha == opcoes_relatorio[4]:
        st.subheader("🔴⚫ Preceptores de pacientes flamenguistas")
        dados = c_orm.preceptores_de_flamenguistas(session)
        if dados:
            df = pd.DataFrame(dados, columns=["Nome do Preceptor"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum preceptor supervisionou atendimento a este grupo.")

    elif escolha == opcoes_relatorio[5]:
        st.subheader("Último atendimento por paciente")
        dados = c_orm.ultimo_atendimento_por_paciente(session)
        if dados:

            dados_formatados = [
                (pac, dt, res, prec, ", ".join(procs) if procs else "(Nenhum)") 
                for pac, dt, res, prec, procs in dados
            ]
            df = pd.DataFrame(dados_formatados, columns=["Paciente", "Data/Hora", "Residente", "Preceptor", "Procedimentos"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum atendimento registrado.")

    elif escolha == opcoes_relatorio[6]:
        st.subheader("Percentual de Alto Risco por Residente")
        dados = c_orm.percentual_alto_risco_por_residente(session)
        if dados:
            df = pd.DataFrame(dados, columns=["ID", "Nome do Residente", "Total Procedimentos", "Alta Complexidade", "Percentual (%)"])
            
            st.dataframe(
                df.style.format({"Percentual (%)": "{:.2f}%"}), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Nenhum procedimento registrado.")