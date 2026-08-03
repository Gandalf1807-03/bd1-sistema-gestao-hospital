"""
Demonstração de LAZY LOADING vs EAGER LOADING (exigido no item 4 da Etapa 2).
Adaptado para o Streamlit com explicações interativas.
"""

import streamlit as st
import pandas as pd
import models as md

from sqlalchemy.orm import Session, joinedload, selectinload
from database import engine

# Configuração da página
st.set_page_config(page_title="Lazy vs Eager Loading", layout="wide")
st.title("🐢 Lazy Loading vs 🐇 Eager Loading")
st.markdown("""
Esta tela demonstra as estratégias de carregamento de relacionamentos do SQLAlchemy.
**⚠️ ATENÇÃO:** Para ver a verdadeira diferença, mantenha o **terminal aberto** (onde você rodou o Streamlit). 
Como o `engine` está configurado com `echo=True`, você verá a quantidade de `SELECTs` sendo disparados no console em tempo real.
""")

st.divider()

# Criação de abas para separar os 3 conceitos
aba_lazy, aba_joined, aba_selectin = st.tabs([
    "1️⃣ Lazy Loading (Padrão)", 
    "2️⃣ Eager Loading (joinedload)", 
    "3️⃣ Eager Loading (selectinload)"
])

with Session(engine) as session:

    # ===============================================================================
    # ABA 1: LAZY LOADING
    # ===============================================================================
    with aba_lazy:
        st.header("🐢 Lazy Loading (Carregamento Preguiçoso)")
        st.info("**Conceito:** O ORM só busca o relacionamento no banco quando você acessa o atributo, gerando um SELECT extra 'sob demanda'.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Passo 1: Buscar o atendimento**")
            atendimento = session.get(md.Atendimento, 1)
            st.code("atendimento = session.get(md.Atendimento, 1)", language="python")
            st.success("✔️ Atendimento carregado! (Olhe o terminal: 1 SELECT foi disparado. Não há JOIN com paciente).")
            
        with col2:
            st.markdown("**Passo 2: Acessar o paciente**")
            if atendimento:
                paciente = atendimento.paciente
                nome_paciente = paciente.pessoa.nome if paciente.pessoa else paciente.id_pessoa
                
                st.code("paciente = atendimento.paciente\nprint(paciente.pessoa.nome)", language="python")
                st.warning("⚠️ Um 2º SELECT acaba de ser disparado no terminal para buscar o Paciente e a Pessoa!")
                st.write(f"**Resultado:** Paciente encontrado: `{nome_paciente}`")
            else:
                st.error("Atendimento ID 1 não encontrado.")


    # ===============================================================================
    # ABA 2: EAGER LOADING (JOINEDLOAD)
    # ===============================================================================
    with aba_joined:
        st.header("🐇 Eager Loading com `joinedload`")
        st.info("**Conceito:** O ORM traz o relacionamento junto na consulta principal usando um `LEFT OUTER JOIN`. Ideal para relacionamentos 1-para-1 ou N-para-1.")
        
        st.markdown("**Executando a consulta:**")
        st.code("""
stmt = (
    session.query(md.Atendimento)
    .options(joinedload(md.Atendimento.paciente).joinedload(md.Paciente.pessoa))
    .filter(md.Atendimento.id_atendimento == 1)
)
atendimento = stmt.first()
        """, language="python")
        
        # Execução real
        stmt_joined = (
            session.query(md.Atendimento)
            .options(joinedload(md.Atendimento.paciente).joinedload(md.Paciente.pessoa))
            .filter(md.Atendimento.id_atendimento == 1)
        )
        atendimento_joined = stmt_joined.first()
        
        st.success("✔️ Consulta executada! (Olhe o terminal: Apenas 1 ÚNICO SELECT foi disparado, contendo os JOINs necessários).")
        
        if atendimento_joined:
            st.write(f"**Resultado Imediato:** Paciente: `{atendimento_joined.paciente.pessoa.nome}`")
        else:
            st.error("Atendimento ID 1 não encontrado.")


    # ===============================================================================
    # ABA 3: EAGER LOADING (SELECTINLOAD)
    # ===============================================================================
    with aba_selectin:
        st.header("🐇 Eager Loading com `selectinload`")
        st.info("**Conceito:** Ideal para relacionamentos 1-para-MUITOS (evita a duplicação de linhas de um JOIN). Dispara um 2º SELECT separadamente usando a cláusula `IN (...)`, carregando todos os filhos de uma vez.")
        
        st.markdown("**Executando a consulta:**")
        st.code("""
stmt = (
    session.query(md.Residente)
    .options(selectinload(md.Residente.atendimentos))
)
residentes = stmt.all()
        """, language="python")
        
        # Execução real
        stmt_selectin = (
            session.query(md.Residente)
            .options(selectinload(md.Residente.atendimentos))
        )
        residentes = stmt_selectin.all()
        
        st.success("✔️ Consultas executadas! (Olhe o terminal: Exatamente 2 SELECTs foram disparados, um para buscar os residentes e outro usando IN para buscar TODOS os atendimentos deles de uma vez).")
        
        if residentes:
            dados_residentes = [
                {"ID Residente": r.id_pessoa, "Qtd de Atendimentos": len(r.atendimentos)} 
                for r in residentes
            ]
            st.dataframe(pd.DataFrame(dados_residentes), use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum residente encontrado.")