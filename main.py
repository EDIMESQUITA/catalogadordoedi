import streamlit as st
import sqlite3

# Configuração da página para remover margens excessivas
st.set_page_config(page_title="Catalogador", layout="centered")

# ===== CSS PARA COPIAR O DESIGN DO PYDROID =====
st.markdown("""
    <style>
    /* Esconde o menu padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Estilo dos botões de valor */
    div.stButton > button {
        height: 50px;
        border-radius: 2px;
        border: 1px solid #333;
        color: white;
        font-weight: bold;
        font-size: 18px;
        margin: 1px;
    }

    /* Cores específicas */
    .st-key-azul button { background-color: #1a237e !important; }
    .st-key-vermelho button { background-color: #b71c1c !important; }
    .st-key-menu button { background-color: #555 !important; height: 40px !important; }
    .st-key-footer button { background-color: #444 !important; font-size: 12px !important; height: 60px !important; }

    /* Container do histórico */
    .hist-box {
        display: inline-block;
        width: 55px;
        height: 80px;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        color: white;
        margin-right: 5px;
        border-radius: 4px;
        padding-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ===== LOGICA DE BANCO =====
def conectar_db():
    conn = sqlite3.connect("bacbo_v2.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS hist (id INTEGER PRIMARY KEY, azul INT, verm INT, jogo TEXT)")
    conn.commit()
    return conn, c

conn, cursor = conectar_db()

# ===== ESTADO =====
if 'jogo' not in st.session_state: st.session_state.jogo = "BACBO"
if 'modo' not in st.session_state: st.session_state.modo = "Nb"
if 'temp_azul' not in st.session_state: st.session_state.temp_azul = None

# ===== COMPONENTES DA INTERFACE =====

# 1. HISTÓRICO (No topo como na imagem)
st.write("###") # Espaçamento
cursor.execute("SELECT azul, verm FROM hist WHERE jogo = ? ORDER BY id DESC LIMIT 10", (st.session_state.jogo,))
dados = cursor.fetchall()

hist_html = '<div style="display: flex; flex-direction: row; overflow-x: auto; padding-bottom: 20px;">'
for a, v in dados:
    cor = "#FFD700" if a == v else "#1a237e" if a > v else "#b71c1c"
    # Lógica simplificada de tradução para o exemplo
    txt = f"{a}<br>X<br>{v}" if st.session_state.modo == "NUM" else "NA<br>X<br>Nb" 
    hist_html += f'<div class="hist-box" style="background-color: {cor};">{txt}</div>'
hist_html += '</div>'
st.markdown(hist_html, unsafe_allow_html=True)

st.divider()

# 2. BOTÕES DE ENTRADA (Azul em cima, Vermelho embaixo)
valores = range(2, 13) if st.session_state.jogo == "BACBO" else range(2, 15)

# Linha Azul
cols_a = st.columns(len(valores))
for i, v in enumerate(valores):
    label = str(v) if v < 11 else {11:"J", 12:"Q", 13:"K", 14:"A"}[v]
    if cols_a[i].button(label, key=f"a_{v}", help="Azul"):
        st.session_state.temp_azul = v
        st.toast(f"Azul: {label}")

# Linha Vermelha
cols_v = st.columns(len(valores))
for i, v in enumerate(valores):
    label = str(v) if v < 11 else {11:"J", 12:"Q", 13:"K", 14:"A"}[v]
    if cols_v[i].button(label, key=f"v_{v}", help="Vermelho"):
        if st.session_state.temp_azul:
            cursor.execute("INSERT INTO hist (azul, verm, jogo) VALUES (?,?,?)", 
                           (st.session_state.temp_azul, v, st.session_state.jogo))
            conn.commit()
            st.session_state.temp_azul = None
            st.rerun()
        else:
            st.error("Selecione o azul primeiro!")

# 3. MENU INFERIOR
st.button("MENU", use_container_width=True, key="menu")

m1, m2, m3, m4 = st.columns(4)
if m1.button("Limpar Histórico", key="f1"):
    cursor.execute("DELETE FROM hist WHERE jogo = ?", (st.session_state.jogo,))
    conn.commit()
    st.rerun()

if m2.button("Desfazer Última", key="f2"):
    cursor.execute("DELETE FROM hist WHERE id = (SELECT MAX(id) FROM hist)")
    conn.commit()
    st.rerun()

if m3.button(f"VER: {st.session_state.modo}", key="f3"):
    st.session_state.modo = "NUM" if st.session_state.modo == "Nb" else "Nb"
    st.rerun()

if m4.button(f"JOGO: {st.session_state.jogo}", key="f4"):
    st.session_state.jogo = "FOOTBALL" if st.session_state.jogo == "BACBO" else "BACBO"
    st.rerun()
