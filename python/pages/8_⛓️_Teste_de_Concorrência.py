import streamlit as st
import threading
import queue 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

# Presumo que essas importações estejam corretas no seu projeto:
from database import engine
import models as md
from insert import inserir_escala

#==================================================
# CENÁRIO OTIMISTA (Adaptado para Streamlit)
#==================================================
def tentar_escalar_otimista(nome_processo, barreira, fila):
    engine.dispose()
    with Session(engine) as session:
        try:
            barreira.wait()
            fila.put(f"[{nome_processo}] (OTIMISTA) Tentando escalar...")

            escala = inserir_escala(
                session,
                id_unidade=1,
                dia_semana="SEGUNDA",
                turno="MANHA",
                id_residente=11,
                id_preceptor=6
            )
            session.commit()
            fila.put(f"[{nome_processo}] SUCESSO — escala id={escala.id_escala} criada")

        except IntegrityError as e:
            session.rollback()
            fila.put(f"[{nome_processo}] FALHOU — violação de unique_escala: {e.orig}")


#==================================================
# CENÁRIO PESSIMISTA (Adaptado para Streamlit)
#==================================================
def tentar_escalar_pessimista(nome_processo, barreira, fila):
    engine.dispose()
    with Session(engine) as session:
        barreira.wait()
        fila.put(f"[{nome_processo}] (PESSIMISTA) Tentando escalar...")

        stmt = select(md.Unidade).where(md.Unidade.id_unidade == 1).with_for_update()
        session.execute(stmt).scalar_one()

        fila.put(f"[{nome_processo}] Lock adquirido, verificando conflito...")

        ja_existe = session.execute(
            select(md.Escala).where(
                md.Escala.id_unidade == 1,
                md.Escala.dia_semana == "SEGUNDA",
                md.Escala.turno == "MANHA",
                md.Escala.id_residente == 11,
            )
        ).first()

        if ja_existe:
            fila.put(f"[{nome_processo}] Já existe escala — abortando")
            session.rollback()
            return

        escala = inserir_escala(session, 1, "SEGUNDA", "MANHA", 11, 6)
        session.commit()
        fila.put(f"[{nome_processo}] SUCESSO — escala id={escala.id_escala} criada")


#==================================================
# ORQUESTRAÇÃO
#==================================================
CENARIOS = {
    "otimista": tentar_escalar_otimista,
    "pessimista": tentar_escalar_pessimista,
}

#==================================================
# INTERFACE DO STREAMLIT (Substitui o __main__)
#==================================================
st.title("⚙️ Simulação de Concorrência (Otimista vs Pessimista)")

st.write("Teste os bloqueios do banco de dados executando processos paralelos.")

# Seletor do cenário
cenario = st.radio("Escolha o cenário para simular:", ["otimista", "pessimista"])

if st.button("Executar Simulação"):
    st.subheader(f"=== Executando cenário: {cenario.upper()} ===")
    
    status_text = st.info("Iniciando execução paralela...")
    
    funcao_alvo = CENARIOS[cenario]
    
    # Gerenciador para compartilhar a Fila e a Barreira entre processos
    fila = queue.Queue()
    barreira = threading.Barrier(2)

    # Passando a "fila" como o terceiro argumento!
    p1 = threading.Thread(target=funcao_alvo, args=("Thread A", barreira, fila))
    p2 = threading.Thread(target=funcao_alvo, args=("Thread B", barreira, fila))

    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    status_text.success("Simulação concluída!")

    # Lendo o correio (fila) e mostrando na tela
    st.markdown("### 📝 Resultados do Banco de Dados:")
    
    while not fila.empty():
        mensagem = fila.get()
        # st.code deixa o texto formatado como código (igual no terminal), fica bem legal!
        st.code(mensagem, language="text")
