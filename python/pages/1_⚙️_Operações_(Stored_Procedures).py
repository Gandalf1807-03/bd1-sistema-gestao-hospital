import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine, get_session
from pathlib import Path

# Caminho até a pasta raiz
pasta_atual = Path(__file__).parent
pasta_raiz = pasta_atual.parent

# Caminhos até os scripts das Stored Procedures
sp_registrar_atendimento_completo_sql = pasta_raiz / "call_procedures" / "sp_registrar_atendimento_completo.sql"
sp_calcular_tempo_medio_espera_sql = pasta_raiz / "call_procedures" / "sp_calcular_tempo_medio_espera.sql"
sp_reajustar_escala_sql = pasta_raiz / "call_procedures" / "sp_reajustar_escala.sql"

# ==============================
# ========= Streamlit ==========
# ==============================
# Configuração do título da página
st.set_page_config(page_title="Operações", page_icon="⚙️")
st.title("⚙️ Operações Avançadas (Stored Procedures)")

# Criação de abas para organizar as Procedures exigidas no projeto
aba_atendimento, aba_espera, aba_escala = st.tabs([
    "Registrar Atendimento", 
    "Tempo Médio de Espera", 
    "Reajustar Escala"
])

# 1. sp_registrar_atendimento_completo
with aba_atendimento:
    st.header("Novo Atendimento Completo")
    st.markdown("Insere atendimento e procedimentos em uma única transação.")
    
    with st.form("form_atendimento"):

        col1, col2 = st.columns(2)
        with col1:
            id_paciente = st.number_input("ID Paciente", min_value=1)
            id_residente = st.number_input("ID Residente", min_value=1)
            id_preceptor = st.number_input("ID Preceptor", min_value=1)
        with col2:
            data_hora = st.datetime_input("Chegada do paciente")
            id_unidade = st.number_input("ID Unidade", min_value=1)
            duracao_minutos = st.number_input("Duração (min)", min_value=1)
        
        st.subheader("Procedimentos Realizados")

        # st.data_editor permite que o usuário adicione linhas dinamicamente no front-end!
        df_procedimentos = pd.DataFrame(columns=["id_procedimento", "quantidade", "tempo_real_minutos", "observacao", "is_faturado", "data_hora_inicio"])
        procedimentos_editados = st.data_editor(
            df_procedimentos,
            num_rows="dynamic",
            column_config={
                "id_procedimento": st.column_config.NumberColumn(
                    "Cód. Procedimento",
                    min_value=1,
                    step=1
                ),
                "quantidade": st.column_config.NumberColumn(
                    "Quantidade",
                    min_value=1,
                    step=1,
                    default=1
                ),
                "tempo_real_minutos": st.column_config.NumberColumn(
                    "Tempo (min)",
                    min_value=1,
                    step=1
                ),
                "observacao": st.column_config.TextColumn(
                    "Observações",
                    max_chars=255
                ),
                "is_faturado": st.column_config.CheckboxColumn(
                    "Está faturado"
                ),
                "data_hora_inicio": st.column_config.DatetimeColumn(
                    "Data/Hora de início",
                    format="YYYY/MM/DD HH:mm:ss",
                    step=1
                )
            })
        
        btn_salvar_atendimento = st.form_submit_button("Registrar Tudo")
        
        if btn_salvar_atendimento:

            # Formatação da data
            procedimentos_editados["data_hora_inicio"] = pd.to_datetime(procedimentos_editados["data_hora_inicio"])
            procedimentos_editados["data_hora_inicio"] = procedimentos_editados["data_hora_inicio"].dt.strftime('%Y-%m-%d %H:%M:%S')

            # Criação do JSON contendo os procedimentos realizados no atendimento
            json_procedimentos = procedimentos_editados.to_json(orient="records")
            st.write("JSON gerado:")
            st.json(json_procedimentos)

            session = get_session()
            try:
                with open(sp_registrar_atendimento_completo_sql, "r", encoding="utf-8") as file:
                    script_sql = file.read()

                comando = text(script_sql)
                parametros = {
                    "p_data_hora": data_hora,
                    "p_duracao_minutos": duracao_minutos,
                    "p_id_paciente": id_paciente,
                    "p_id_residente": id_residente,
                    "p_id_preceptor": id_preceptor,
                    "p_id_unidade": id_unidade,
                    "p_procedimentos": json_procedimentos
                }

                session.execute(comando, parametros)
                session.commit()
                st.success("Atendimento e procedimentos salvos com sucesso!")

            except Exception as e:
                session.rollback()
                st.error("Erro ao salvar no banco.")
                st.warning(f"Detalhes: {e}")
            finally:
                session.close()

# 2. sp_calcular_tempo_medio_espera
with aba_espera:
    st.header("Tempo Médio de Espera por Unidade")
    st.markdown("Calcula o tempo entre a chegada e o primeiro procedimento.")
    
    if st.button("Calcular Tempos de Espera"):
        # 1. Abre a Sessão (O SQLAlchemy já inicia um "BEGIN" automático aqui)
        session = get_session()
        try:
            # 2. Chama a Procedure passando o nome do cursor
            session.execute(text("CALL sp_calcular_tempo_medio_espera('rs_tempo_espera');"))
            
            # 3. Busca os dados dentro do cursor
            resultado = session.execute(text("FETCH ALL FROM rs_tempo_espera;"))
            
            # 4. Extrai as linhas (dados) e as colunas (cabeçalhos)
            linhas = resultado.fetchall()
            colunas = resultado.keys()
            
            # 5. Converte o resultado bruto para um DataFrame do Pandas
            df_resultado = pd.DataFrame(linhas, columns=colunas)
            
            # 6. Exibe a tabela bonitona no Streamlit
            if not df_resultado.empty:
                st.success("Cálculo realizado com sucesso!")
                st.dataframe(df_resultado, use_container_width=True)
            else:
                st.info("Nenhum dado encontrado para o tempo de espera.")
                
            # 7. Confirma a transação (Executa o "COMMIT")
            session.commit()
            
        except Exception as e:
            # Cancela tudo em caso de erro
            session.rollback()
            st.error("Erro ao processar o cursor no banco de dados.")
            st.warning(f"Detalhes: {e}")
        finally:
            session.close()

# 3. sp_reajustar_escala
with aba_escala:
    st.header("Reajustar Escala de Residente")
    st.markdown("Muda todas as escalas de um dia/turno para outro, validando conflitos.")
    
    with st.form("form_reajuste"):
        id_residente = st.number_input("ID do Residente", min_value=1, step=1)
        id_nova_unidade = st.number_input("ID da Nova Unidade", min_value=1)
        col_atual, col_novo = st.columns(2)
        
        with col_atual:
            dia_antigo = st.selectbox("Dia Atual", ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA"])
            turno_antigo = st.selectbox("Turno Atual", ["MANHA", "TARDE", "NOITE"])
            
        with col_novo:
            dia_novo = st.selectbox("Novo Dia", ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA"])
            turno_novo = st.selectbox("Novo Turno", ["MANHA", "TARDE", "NOITE"])
            
        btn_reajuste = st.form_submit_button("Executar Reajuste")
        
        if btn_reajuste:
            session = get_session()
            try:
                with open(sp_reajustar_escala_sql, "r", encoding="utf-8") as file:
                    script_sql = file.read()
    
                comando = text(script_sql)
                parametros = {
                    "p_id_residente": id_residente,
                    "p_dia_semana_antigo": dia_antigo,
                    "p_turno_antigo": turno_antigo,
                    "p_id_nova_unidade": id_nova_unidade,
                    "p_novo_dia_semana": dia_novo,
                    "p_novo_turno": turno_novo,
                }
                session.execute(comando, parametros)
                session.commit()
                st.success("Escala reajustada com sucesso!")

            except Exception as e:
                session.rollback()
                st.error("Erro ao reajustar a escala no banco.")
                st.warning(f"Detalhes: {e}")
            finally:
                session.close()
