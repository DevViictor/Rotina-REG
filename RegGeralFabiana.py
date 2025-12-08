import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image

# --- Configuração Google Sheets ---
gcp_info = st.secrets["gcp"]
planilha_chave = st.secrets["planilha"]["chave"]

creds = Credentials.from_service_account_info(
    dict(gcp_info),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)


cliente = gspread.authorize(creds)
planilha = cliente.open_by_key(planilha_chave)

image_logo = Image.open("image/Image (2).png")

if "role" not in st.session_state:
    st.session_state["role"] = "Victor" 

# --- Função genérica para qualquer carteira ---
def relatorio_fabiana_loja(nome_carteira, consultores):
    # Controle de acesso
    
    if st.session_state.get("role") != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # Cabeçalho
    cola, colb, colc = st.columns([4,1,1])
    with colc: st.image(image_logo)
    with cola: st.header(f"R.E.G - {nome_carteira}")

    # Função interna para ler aba
    def carregar_pedidos(consultor):
        try:
            df = pd.DataFrame(planilha.worksheet(consultor).get_all_records())
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].str.strip().str.lower() == "concluído"
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # Gerar resumo
    resumo = []
    for c in consultores:
        df = carregar_pedidos(c)
        total = len(df)
        concluidas = df["Situação da tarefa"].sum() if not df.empty else 0
        percentual = round((concluidas / total) * 100, 1) if total > 0 else 0
        resumo.append({
            "Consultor": c,
            "Concluídas": int(concluidas),
            "Pendentes": int(total - concluidas),
            "Percentual Concluído": f"{percentual}%"
        })

    st.dataframe(pd.DataFrame(resumo))


relatorio_fabiana_loja("CARTEIRA SSA1", ["Ana","Francisca","Vinicius"])
relatorio_fabiana_loja("CARTEIRA SSA2", ["Vitor","Mailan"])
relatorio_fabiana_loja("CARTEIRA BELA VISTA", ["Vanessa","Danilo"])
relatorio_fabiana_loja("CARTEIRA PARALELA", ["Crislaine","Neide"])
relatorio_fabiana_loja("CARTEIRA PARQUE", ["Denise_Paque","Adrielle"])