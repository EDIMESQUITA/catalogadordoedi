import streamlit as st
import sqlite3

# Configuração para ocupar a tela toda
st.set_page_config(layout="wide")

# ===== CSS PARA DEIXAR IGUAL AO PYDROID 3 =====
st.markdown("""
    <style>
    /* Remove padding excessivo do Streamlit */
    .block-container { padding: 10px !important; }
    
    /* Força os botões a ficarem lado a lado e sem margem */
    [data-testid="column"] {
        padding: 0px !important;
        margin: 0px !important;
        min-width: 0px !important;
    }
    
    /* Estilo Geral dos Botões */
    div.stButton > button {
        width: 100% !important;
        border-radius: 0px !important;
        border: 0.5px solid #111 !important;
        color: white !important;
        font-weight: bold !important;
        height: 60px !important;
    }

    /* Cores das Fileiras */
    .st-key-btn_azul button { background-color: #0d1b3e !important; }
    .st-key-btn_verm button { background-color: #5a1010 !important; }
    
    /* Botão Menu e Rodapé */
    .st-key-btn_menu button { background-color: #444 !important; height: 45px !important; }
    .st-key-btn_footer button { background-color: #333 !important; font-size: 10px !important; height: 70px !important; }

    /* Histórico (Quadradinhos no topo) */
    .hist-container { display: flex; overflow-x: auto; gap: 2px; padding-bottom: 10px; }
    .hist-item {
        min-width: 50px; height: 70px; 
        display: flex; align-items: center; justify-content: center;
        text-align: center; font-size: 12px; font-weight: bold; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ===== BANCO DE DADOS =====
def iniciar_db():
    conn = sqlite3.connect("dados.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, a INT, v INT, jogo TEXT)")
    conn.commit()
    return conn, c

conn, cursor = iniciar_db()

# ===== ESTADOS DA SESSÃO =====
if 'jogo' not in st.session_state: st.session_state.jogo = "BACBO"
if 'modo' not in st.session_state: st.session_state.modo = "Nb / NA"
if 'azul' not in st.session_state: st.session_state.azul = None

# 1. EXIBIÇÃO DO HISTÓRICO (Igual à imagem)
cursor.execute("SELECT a, v FROM logs WHERE jogo = ? ORDER BY id DESC LIMIT 15", (st.session_state.jogo,))
dados = cursor.fetchall()

hist_html = '<div class="hist-container">'
for a, v in dados:
    cor = "#706a12" if a == v else "#0d1b3e" if a > v else "#5a1010"
    txt = f"{a}<br>X<br>{v}" if st.session_state.modo == "NUM" else "NA<br>X<br>Nb" # Exemplo de lógica
    hist_html += f'<div class="hist-item" style="background-color: {cor};">{txt}</div>'
hist_html += '</div>'
st.markdown(hist_html, unsafe_allow_html=True)

# 2. BOTÕES DE ENTRADA (Lado a lado)
cartas = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
if st.session_state.jogo == "BACBO": cartas = [str(i) for i in range(2, 13)]

# Fileira Azul
cols_a = st.columns(len(cartas))
for i, c in enumerate(cartas):
    if cols_a[i].button(c, key=f"btn_azul_{i}"):
        st.session_state.azul = c

# Fileira Vermelha
cols_v = st.columns(len(cartas))
for i, c in enumerate(cartas):
    if cols_v[i].button(c, key=f"btn_verm_{i}"):
        if st.session_state.azul:
            cursor.execute("INSERT INTO logs (a, v, jogo) VALUES (?,?,?)", (st.session_state.azul, c, st.session_state.jogo))
            conn.commit()
            st.session_state.azul = None
            st.rerun()

# 3. MENU E BOTÕES INFERIORES
st.write("")
st.button("MENU", use_container_width=True, key="btn_menu")

f1, f2, f3, f4 = st.columns(4)
if f1.button("Limpar Histórico", key="btn_footer_1"):
    cursor.execute("DELETE FROM logs WHERE jogo = ?", (st.session_state.jogo,))
    conn.commit()
    st.rerun()

if f2.button("Desfazer Última", key="btn_footer_2"):
    cursor.execute("DELETE FROM logs WHERE id = (SELECT MAX(id) FROM logs)")
    conn.commit()
    st.rerun()

if f3.button(f"VER: {st.session_state.modo}", key="btn_footer_3"):
    st.session_state.modo = "NUM" if st.session_state.modo == "Nb / NA" else "Nb / NA"
    st.rerun()

if f4.button(f"JOGO: {st.session_state.jogo}", key="btn_footer_4"):
    st.session_state.jogo = "FOOTBALL" if st.session_state.jogo == "BACBO" else "BACBO"
    st.rerun()
