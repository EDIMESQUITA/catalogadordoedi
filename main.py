import streamlit as st
import sqlite3

# Configuração da página
st.set_page_config(page_title="Catalogador BacBo", layout="centered")

# Banco de Dados
conn = sqlite3.connect("dados.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS historico (azul INT, vermelho INT, jogo TEXT)")
conn.commit()

st.title("⚽ Catalogador de Jogos")

# Escolha do Jogo
jogo = st.segmented_control("Escolha o Jogo", ["BACBO", "FOOTBALL"], default="BACBO")

# Interface de Entrada (Botões)
st.subheader("Registrar Resultado")
col1, col2 = st.columns(2)

with col1:
    valor_azul = st.number_input("Azul", 2, 14, key="az")
with col2:
    valor_vermelho = st.number_input("Vermelho", 2, 14, key="vm")

if st.button("SALVAR RESULTADO", use_container_width=True):
    c.execute("INSERT INTO historico VALUES (?, ?, ?)", (valor_azul, valor_vermelho, jogo))
    conn.commit()
    st.toast("Registrado com sucesso!")

# Exibição do Histórico
st.divider()
st.subheader(f"Histórico: {jogo}")

dados = c.execute("SELECT azul, vermelho FROM historico WHERE jogo = ? ORDER BY rowid DESC", (jogo,)).fetchall()

# Mostrar como uma lista de cards coloridos
for az, vm in dados:
    if az > vm:
        st.info(f"🔵 AZUL VENCEU: {az} vs {vm}")
    elif vm > az:
        st.error(f"🔴 VERMELHO VENCEU: {vm} vs {az}")
    else:
        st.warning(f"🟡 EMPATE: {az} vs {vm}")

# Botão para limpar
if st.sidebar.button("Limpar Histórico"):
    c.execute("DELETE FROM historico WHERE jogo = ?", (jogo,))
    conn.commit()
    st.rerun()
