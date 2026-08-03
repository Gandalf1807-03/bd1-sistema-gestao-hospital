import streamlit as st
import pandas as pd
import models as md
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database import engine

import crud_orm as crud

st.set_page_config(page_title="Painel CRUD", layout="centered")
st.title("🛠️ Painel de Operações (CRUD)")
st.write("Selecione a operação que deseja realizar no banco de dados:")

opcoes_crud = [
    "1. Inserir Atendimento (Create)",
    "2. Listar Atendimentos do Paciente (Read)",
    "3. Listar Procedimentos de um Atendimento (Read)",
    "4. Atualizar Convênio do Paciente (Update)",
    "5. Remover Procedimento Realizado (Delete)",
    "6. Tempo Médio por Residente (Analytics)"
]

escolha = st.selectbox("Operação:", opcoes_crud, label_visibility="collapsed")
st.divider()

with Session(engine) as session:
    
    # --- OPÇÃO 1: CREATE ---
    if escolha == opcoes_crud[0]:
        st.subheader("Novo Atendimento")
        with st.form("form_inserir_atendimento"):
            col1, col2 = st.columns(2)
            with col1:
                dt_input = st.date_input("Data do Atendimento")
                tm_input = st.time_input("Hora do Atendimento")
                duracao = st.number_input("Duração (minutos)", min_value=1, value=60)
            with col2:
                id_pac = st.number_input("ID Paciente", min_value=1, value=1)
                id_res = st.number_input("ID Residente", min_value=1, value=1)
                id_prec = st.number_input("ID Preceptor", min_value=1, value=1)
                id_uni = st.number_input("ID Unidade", min_value=1, value=1)
                
            submit_insert = st.form_submit_button("Inserir Atendimento", type="primary")
            
            if submit_insert:
                try:
                    data_hora_completa = datetime.combine(dt_input, tm_input)
                    novo_atend = crud.inserir_atendimento_verificado(
                        session, data_hora_completa, duracao, id_pac, id_res, id_prec, id_uni
                    )
                    session.commit() 
                    st.success(f"Atendimento criado com sucesso! ID Gerado: {novo_atend.id_atendimento}")
                except ValueError as e:
                    session.rollback()
                    st.error(f"Erro de Validação: {e}")
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro no Banco de Dados: {e}")

    # --- OPÇÃO 2: READ (Atendimentos) ---
    elif escolha == opcoes_crud[1]:
        st.subheader("Buscar Atendimentos")
        id_busca = st.number_input("Digite o ID do Paciente", min_value=1, value=1)
        
        if st.button("Buscar"):
            atendimentos = crud.listar_atendimentos_paciente(session, id_busca)
            if atendimentos:
                # Extraindo os atributos do objeto SQLAlchemy para uma lista de dicionários
                dados = [{"ID Atendimento": a.id_atendimento, 
                          "Data/Hora": a.data_hora, 
                          "Duração (min)": a.duracao_minutos} for a in atendimentos]
                st.dataframe(pd.DataFrame(dados), use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum atendimento encontrado para este paciente.")

    # --- OPÇÃO 3: READ (Procedimentos) ---
    elif escolha == opcoes_crud[2]:
        st.subheader("Detalhes do Atendimento")
        id_atend_busca = st.number_input("Digite o ID do Atendimento", min_value=1, value=1)
        
        if st.button("Listar Procedimentos"):
            procedimentos = crud.listar_procedimentos_do_atendimento(session, id_atend_busca)
            if procedimentos:
                df = pd.DataFrame(procedimentos, columns=["Nome do Procedimento", "Quantidade", "Tempo Real (min)"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum procedimento registrado neste atendimento.")

    # --- OPÇÃO 4: UPDATE ---
    elif escolha == opcoes_crud[3]:
        st.subheader("Atualizar Convênio")
        with st.form("form_atualizar"):
            id_paciente_upd = st.number_input("ID do Paciente", min_value=1, value=1)
            novo_convenio = st.text_input("Novo Número do Convênio")
            
            submit_update = st.form_submit_button("Salvar Alteração")
            
            if submit_update:
                try:
                    crud.atualizar_convenio_paciente(session, id_paciente_upd, novo_convenio)
                    session.commit()
                    st.success(f"Convênio do paciente {id_paciente_upd} atualizado com sucesso!")
                except ValueError as e:
                    session.rollback()
                    st.error(f"Erro: {e}")
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro no Banco de Dados: {e}")

    # --- OPÇÃO 5: DELETE ---
    elif escolha == opcoes_crud[4]:
        st.subheader("🗑️ Remover Procedimento Realizado")
        st.warning("Atenção: Procedimentos já faturados não podem ser removidos pelas regras de negócio.")
        
        with st.form("form_delete"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                id_atend_del = st.number_input("ID do Atendimento", min_value=1, value=1)
            with col_d2:
                id_proc_del = st.number_input("ID do Procedimento", min_value=1, value=1)
                
            submit_delete = st.form_submit_button("Remover Registro", type="primary")
            
            if submit_delete:
                try:
                    crud.remover_procedimento_realizado(session, id_atend_del, id_proc_del)
                    session.commit()
                    st.success("Procedimento removido com sucesso!")
                except ValueError as e:
                    session.rollback()
                    st.error(f"Operação Bloqueada: {e}")
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro no Banco de Dados: {e}")

    # --- OPÇÃO 6: ANALYTICS ---
    elif escolha == opcoes_crud[5]:
        st.subheader("⏱️ Tempo Médio por Residente")
        dados_tempo = crud.tempo_medio_por_residente(session)
        
        if dados_tempo:
            df = pd.DataFrame(dados_tempo, columns=["Residente", "ID", "Média (min)", "Total Atendimentos"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Não há dados suficientes para gerar a média.")
