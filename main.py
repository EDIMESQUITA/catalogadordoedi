import streamlit as st
import sqlite3

# Configuração da página
st.set_page_config(page_title="Catalogador BacBo/Football", layout="wide")

# ===== BANCO DE DADOS =====
def conectar_db():
    conn = sqlite3.connect("bacbo_streamlit.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            azul INTEGER,
            vermelho INTEGER,
            jogo TEXT
        )
    """)
    conn.commit()
    return conn, cursor

conn, cursor = conectar_db()

# ===== CONSTANTES E LÓGICA =====
FOOTBALL_CARTAS = [(n, str(n)) for n in range(2, 11)] + [(11, "J"), (12, "Q"), (13, "K"), (14, "A")]
CARTA_TEXTO = {11: "J", 12: "Q", 13: "K", 14: "A"}

def classificar_bacbo(v):
    if v in [3, 4, 5, 6]: return "Nb"
    if v in [8, 9, 10, 11]: return "NA"
    if v == 7: return "N"
    return str(v)

def classificar_football(v):
    if v in [4, 5, 6, 7]: return "Nb"
    if v in [9, 10]: return "NA"
    if v in [11, 12, 13]: return "L"
    if v == 8: return "N"
    return CARTA_TEXTO.get(v, str(v))

# ===== ESTADO DA SESSÃO (SESSION STATE) =====
if 'jogo_atual' not in st.session_state:
    st.session_state.jogo_atual = "BACBO"
if 'modo_visualizacao' not in st.session_state:
    st.session_state.modo_visualizacao = "Nb"
if 'azul_temp' not in st.session_state:
    st.session_state.azul_temp = None

# ===== FUNÇÕES DE AÇÃO =====
def salvar_resultado(azul, vermelho):
    cursor.execute(
        "INSERT INTO historico (azul, vermelho, jogo) VALUES (?, ?, ?)",
        (azul, vermelho, st.session_state.jogo_atual)
    )
    conn.commit()
    st.session_state.azul_temp = None

def limpar_tudo():
    cursor.execute("DELETE FROM historico WHERE jogo = ?", (st.session_state.jogo_atual,))
    conn.commit()

def desfazer_ultimo():
    cursor.execute(
        "DELETE FROM historico WHERE id = (SELECT MAX(id) FROM historico WHERE jogo = ?)",
        (st.session_state.jogo_atual,)
    )
    conn.commit()

# ===== INTERFACE UI =====
st.title(f"🎮 Catalogador: {st.session_state.jogo_atual}")

# --- Sidebar (Menu) ---
with st.sidebar:
    st.header("Configurações")
    
    if st.button("Trocar Jogo"):
        st.session_state.jogo_atual = "FOOTBALL" if st.session_state.jogo_atual == "BACBO" else "BACBO"
        st.rerun()
        
    if st.button("Alternar Modo Visual"):
        st.session_state.modo_visualizacao = "NUM" if st.session_state.modo_visualizacao == "Nb" else "Nb"
        st.rerun()

    st.divider()
    if st.button("Desfazer Última"):
        desfazer_ultimo()
        st.rerun()
        
    if st.button("Limpar Histórico"):
        limpar_tudo()
        st.rerun()

# --- Área de Histórico ---
st.subheader("Histórico Recente")
cursor.execute(
    "SELECT azul, vermelho FROM historico WHERE jogo = ? ORDER BY id DESC LIMIT 20",
    (st.session_state.jogo_atual,)
)
dados = cursor.fetchall()

# Exibição horizontal do histórico
cols_hist = st.columns(len(dados) if len(dados) > 0 else 1)
for i, (azul, vermelho) in enumerate(dados):
    maior, menor = (azul, vermelho) if azul >= vermelho else (vermelho, azul)
    
    # Lógica de cor e texto
    cor = "#FFD700" if azul == vermelho else "#1E90FF" if azul > vermelho else "#FF4B4B"
    
    if st.session_state.modo_visualizacao == "NUM":
        txt = f"{CARTA_TEXTO.get(maior, maior)} x {CARTA_TEXTO.get(menor, menor)}"
    else:
        txt = f"{classificar_football(maior) if st.session_state.jogo_atual == 'FOOTBALL' else classificar_bacbo(maior)} x {classificar_football(menor) if st.session_state.jogo_atual == 'FOOTBALL' else classificar_bacbo(menor)}"

    cols_hist[i].markdown(
        f"""<div style="background-color:{cor}; padding:10px; border-radius:5px; text-align:center; font-weight:bold; color:white; min-width:60px; margin-bottom:20px">
        {txt}
        </div>""", 
        unsafe_allow_html=True
    )

st.divider()

# --- Botões de Entrada ---
st.write(f"**Selecionando para:** {'🔴 VERMELHO' if st.session_state.azul_temp else '🔵 AZUL'}")

valores = range(2, 13) if st.session_state.jogo_atual == "BACBO" else [v[0] for v in FOOTBALL_CARTAS]

# Grid de botões
cols = st.columns(6)
for i, val in enumerate(valores):
    label = CARTA_TEXTO.get(val, str(val))
    if cols[i % 6].button(label, key=f"btn_{val}", use_container_width=True):
        if st.session_state.azul_temp is None:
            st.session_state.azul_temp = val
            st.rerun()
        else:
            salvar_resultado(st.session_state.azul_temp, val)
            st.rerun()

# Feedback de seleção
if st.session_state.azul_temp:
    st.info(f"Valor Azul selecionado: {CARTA_TEXTO.get(st.session_state.azul_temp, st.session_state.azul_temp)}. Agora selecione o Vermelho.")
