import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text
from database import engine, get_session

st.set_page_config(page_title="Validações e Testes", page_icon="🚨")
st.title("🚨 Validações do Banco de Dados")

aba_sobreposicao_escala, aba_audita_atendimento, aba_atualiza_media_procedimentos = st.tabs(["Sobreposição de Escala", "Audita atendimento", "Atualiza média dos procedimentos"])

# 1. Teste da trg_check_sobreposicao_escala
with aba_sobreposicao_escala:
    st.header("1. Validação de Sobreposição de Escala")
    st.markdown("Impede que o mesmo residente seja escalado no mesmo dia/turno em unidades diferentes.")

    st.divider()

    col1, col2 = st.columns(2)

    with st.form("form_teste_bloqueio"):

        with col1:
            with st.container(border=True):

                st.subheader("Teste de bloqueio (deve gerar erro)")
                st.markdown("""
O residente 11 já está escalado na unidade 1 na SEGUNDA MANHA.
""")    
                col11, col12 = st.columns(2)
                with col11:
                    id_unidade_col1 = st.number_input("ID Unidade", min_value=1, value=2, key="id_unidade_primeira_coluna")
                    dia_semana_col1 = st.selectbox("Dia da Semana", ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA"], index=0, key="dia_semana_primeira_coluna")
                    turno_col1 = st.selectbox("Turno", ["MANHA", "TARDE", "NOITE"], index=0, key="turno_primeira_coluna")
                with col12:
                    id_residente_col1 = st.number_input("ID Residente", min_value=1, value=11, key="id_residente_primeira_coluna")
                    id_preceptor_col1 = st.number_input("ID Preceptor", min_value=1, value=7, key="id_preceptor_primeira_coluna")

                if st.button("Testar bloqueio"):
                    session = get_session()
                    try:
                        # Script SQL
                        # =====================
                        sql_script = text(f"""INSERT INTO Escala (id_unidade, dia_semana, turno, id_residente, id_preceptor)
                                          VALUES (:p_id_unidade_col1, :p_dia_semana_col1, :p_turno_col1, :p_id_residente_col1, :p_id_preceptor_col1);
                                          """)
                        # =====================
                        parametros = {
                            "p_id_unidade_col1": id_unidade_col1,
                            "p_dia_semana_col1": dia_semana_col1,
                            "p_turno_col1": turno_col1,
                            "p_id_residente_col1": id_residente_col1,
                            "p_id_preceptor_col1": id_preceptor_col1
                        }
                        session.execute(sql_script, parametros)
                        session.commit()
                        st.success("Plantão agendado (Não houve bloqueio da Trigger).")
            
                    except Exception as e:
                        session.rollback()
                        st.error("🚨 Inserção bloqueada pela Trigger no PostgreSQL!")
                        st.warning(f"Detalhes: {e}")

                    finally:
                        session.close()

    with st.form("form_teste_permissao"):

        with col2:
            with st.container(border=True):
                st.subheader("Teste de permissão (deve executar com sucesso)")
                st.markdown("""
A combinação QUARTA MANHA para o residente 11 não existe na tabela.
""")
                col21, col22 = st.columns(2)
                with col21:
                    id_unidade_col2 = st.number_input("ID Unidade", min_value=1, value=1, key="id_unidade_segunda_coluna")
                    dia_semana_col2 = st.selectbox("Dia da Semana", ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA"], index=2, key="dia_semana_segunda_coluna")
                    turno_col2 = st.selectbox("Turno", ["MANHA", "TARDE", "NOITE"], index=0, key="turno_segunda_coluna")
                with col22:
                    id_residente_col2 = st.number_input("ID Residente", min_value=1, value=11, key="id_residente_segunda_coluna")
                    id_preceptor_col2 = st.number_input("ID Preceptor", min_value=1, value=7, key="id_preceptor_segunda_coluna")
                
                if st.button("Testar permissão"):
                    session = get_session()
                    try:
                        # Script SQL
                        # =====================
                        sql_script = text(f"""INSERT INTO Escala (id_unidade, dia_semana, turno, id_residente, id_preceptor)
                                                                 VALUES (:p_id_unidade_col2, :p_dia_semana_col2, :p_turno_col2, :p_id_residente_col2, :p_id_preceptor_col2);
                                                                 """)
                        # =====================
                        parametros = {
                            "p_id_unidade_col2": id_unidade_col2,
                            "p_dia_semana_col2": dia_semana_col2,
                            "p_turno_col2": turno_col2,
                            "p_id_residente_col2": id_residente_col2,
                            "p_id_preceptor_col2": id_preceptor_col2
                        }
                        session.execute(sql_script, parametros)
                        session.commit()
                        st.success("✅ Plantão agendado com sucesso!")
            
                    except Exception as e:
                        session.rollback()
                        st.error("Inserção bloqueada.")
                        st.warning(f"Detalhes: {e}")

                    finally:
                        session.close()
    
    st.subheader("Verificação do estado")
    st.markdown("""```sql
SELECT * FROM Escala WHERE id_residente = 11 ORDER BY id_escala
```
""")

    # Script SQL
    # =====================
    df_estado = pd.read_sql("SELECT * FROM Escala WHERE id_residente = 11 ORDER BY id_escala;", engine)
    # =====================
    st.dataframe(df_estado)

with aba_audita_atendimento:
    st.header("2. Auditoria de Atendimentos")
    st.markdown("Registra automaticamente operações INSERT, UPDATE e DELETE na tabela Atendimento, armazenando o histórico na tabela Auditoria_Atendimento com dados em JSON.")

    st.subheader("Consulta ao estado atual da auditoria")

    # Script SQL
    # =====================
    df_estado_auditoria = pd.read_sql("SELECT * FROM Auditoria_Atendimento ORDER BY id_auditoria DESC;", engine)
    # =====================
    st.dataframe(df_estado_auditoria)

    sub_visao = st.radio(
        "Selecione a operação:", 
        ["INSERT", "UPDATE", "DELETE"], 
        horizontal=True
    )

    if sub_visao == "INSERT":
        st.subheader("2.1 Teste de INSERT")
        st.markdown("""
Insere um novo atendimento e verifica o registro na auditoria.

Dados a serem inseridos:

- `data_hora`: CURRENT_TIMESTAMP
- `duracao_minutos`: 30
- `id_paciente`: 1
- `id_residente`: 11
- `id_preceptor`: 6
- `id_unidade`: 1
""")
        if st.button("Testar INSERT"):
            session = get_session()
            try:

                # Script SQL
                # =====================
                comando = text("INSERT INTO Atendimento (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade) VALUES (CURRENT_TIMESTAMP, 30, 1, 11, 6, 1);")
                # =====================

                session.execute(comando)
                session.commit()
                st.success("Operação de INSERT executada com sucesso!")

                df_trg_insert = pd.read_sql("SELECT * FROM Auditoria_Atendimento WHERE operacao = 'INSERT' ORDER BY id_auditoria DESC LIMIT 3;", engine)
                st.dataframe(df_trg_insert)

            except Exception as e:
                session.rollback()
                st.error("Erro ao realizar o INSERT.")
                st.warning(f"Detalhes: {e}")
            finally:
                session.close()

    if sub_visao == "UPDATE":
        st.subheader("2.2 Teste de UPDATE")
        st.markdown("""
Atualiza a duração de um atendimento e verifica o registro na auditoria.

Dado a ser atualizado:

`id_atendimento`: 1

- `duracao_minutos` -> 45
""")
        if st.button("Testar UPDATE"):
            session = get_session()
            try:

                # Script SQL
                # =====================
                comando = text("UPDATE Atendimento SET duracao_minutos = 45 WHERE id_atendimento = 1;")
                # =====================

                session.execute(comando)
                session.commit()
                st.success("Operação de UPDATE executada com sucesso!")

                df_trg_update = pd.read_sql("SELECT * FROM Auditoria_Atendimento WHERE operacao = 'UPDATE' ORDER BY id_auditoria DESC LIMIT 3;", engine)
                st.dataframe(df_trg_update)

            except Exception as e:
                session.rollback()
                st.error("Erro ao atualizar dado no banco.")
                st.warning(f"Detalhes: {e}")
            finally:
                session.close()

    if sub_visao == "DELETE":
        st.subheader("2.3 Teste de DELETE")
        st.markdown("""
Remove o último atendimento e verifica o registro na auditoria""")
        if st.button("Testar DELETE"):
            session = get_session()
            try:

                # Script SQL
                # =====================
                comando = text("DELETE FROM Atendimento WHERE id_atendimento = (SELECT MAX(id_atendimento) FROM Atendimento);")
                # =====================

                session.execute(comando)
                session.commit()
                st.success("Operação de DELETE executada com sucesso!")

                df_trg_delete = pd.read_sql("SELECT * FROM Auditoria_Atendimento WHERE operacao = 'DELETE' ORDER BY id_auditoria DESC LIMIT 3;", engine)
                st.dataframe(df_trg_delete)

            except Exception as e:
                session.rollback()
                st.error("Erro ao tentar deletar dado do banco.")
                st.warning(f"Detalhes: {e}")
            finally:
                session.close()

with aba_atualiza_media_procedimentos:
    st.header("3. Atualização da Média dos Procedimentos")
    st.markdown("Mantém a média real de tempo dos procedimentos atualizada automaticamente após cada inserção em Procedimento_Realizado.")

    st.subheader("Inserção de um novo registro")
    with st.form("form_atualiza_media_procedimentos"):
        col1, col2, col3 = st.columns(3)
        with col1:
            id_atendimento = st.number_input("ID Atendimento", min_value=1, value=2, key="trg_id_atend")
            id_procedimento = st.number_input("ID Procedimento", min_value=1, value=2, key="trg_id_proc")
            quantidade = st.number_input("Quantidade", min_value=1, value=1, key="trg_qtd")
        with col2:
            tempo_real_minutos = st.number_input("Tempo real (min)", min_value=1, value=25, key="trg_tempo_real_min")
            data_hora_inicio = st.datetime_input("Data/hora de início", value=datetime.datetime.now(), key="trg_data_hora_inicio")
            is_faturado = st.checkbox("Está faturado", value=True, key="trg_is_faturado")
        with col3:
            btn_inserir_proc_realizado = st.form_submit_button("Inserir Procedimento Realizado")

    if btn_inserir_proc_realizado:
        session = get_session()
        try:
            # Parametrização do script SQL de inserção
            sql_script = text("""
                INSERT INTO Procedimento_Realizado 
                (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, data_hora_inicio, is_faturado) 
                VALUES (:p_atendimento, :p_procedimento, :p_qtd, :p_tempo, :p_data, :p_faturado);
            """)

            # Definição dos parâmetros para serem usados no script
            parametros = {
                "p_atendimento": id_atendimento,
                "p_procedimento": id_procedimento,
                "p_qtd": quantidade,
                "p_tempo": tempo_real_minutos,
                "p_data": data_hora_inicio, 
                "p_faturado": is_faturado   
            }
            session.execute(sql_script, parametros)
            session.commit()
            st.success("Procedimento Realizado salvo com sucesso!")

        except Exception as e:
            session.rollback()
            st.error("Erro ao salvar no banco.")
            st.warning(f"Detalhes: {e}")
        finally:
            session.close()


    st.subheader("Verificação da média de um procedimento específico")
    st.markdown("""
```sql
SELECT id_procedimento, nome, media_tempo_procedimento 
FROM Procedimento 
WHERE id_procedimento = 2;
```
""")
    df_media_proc = pd.read_sql("SELECT id_procedimento, nome, media_tempo_procedimento FROM Procedimento WHERE id_procedimento = 2;", engine)
    st.dataframe(df_media_proc)

    st.subheader("Relatório completo das médias")
    st.markdown("""
```sql
SELECT 
id_procedimento, nome, 
tempo_medio_minutos AS estimado, 
media_tempo_procedimento AS real_medio 
FROM Procedimento 
ORDER BY id_procedimento;
```
""")
    df_relatorio_medias = pd.read_sql("SELECT id_procedimento, nome, tempo_medio_minutos AS estimado, media_tempo_procedimento AS real_medio FROM Procedimento ORDER BY id_procedimento;", engine)
    st.dataframe(df_relatorio_medias)

