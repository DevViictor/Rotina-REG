import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image

# --- Função genérica para qualquer carteira ---
def relatorio_carteira(nome_carteira, consultores):
    # Controle de acesso
    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # Configuração Google Sheets
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
    

    # Logo
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4,1,1])
    with colc:
        st.image(image_logo)
    with cola:
        st.header(f"R.E.G - CARTEIRA {nome_carteira.upper()}")

    # Função para carregar pedidos de cada consultor
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            df = pd.DataFrame(aba.get_all_records())
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # Criar resumo por consultor
    resumo = []
    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue
        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0
        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # Mostrar resumo
    st.dataframe(pd.DataFrame(resumo))

# --- Chamadas de exemplo ---
# --- Iguatemi ---
# --- Chamadas de exemplo ---
def relatorio_ssa1():
    relatorio_carteira("SSA1", ["Ana","Francisca","Vinicius"])

def relatorio_ssa2():
    relatorio_carteira("SSA2", ["Vitor","Mailan"])

def relatorio_bela():
    relatorio_carteira("BELA VISTA", ["Vanessa","Danilo"])

def relatorio_paralela():
    relatorio_carteira("PARALELA", ["Crislaine","Neide"])

def relatorio_parque():
    relatorio_carteira("PARQUE", ["Denise_Paque","Adrielle"])

def relatorio_iguatemi1():
    relatorio_carteira("IGUATEMI1", ["Denise","Max"])

def relatorio_iguatemi2():
    relatorio_carteira("IGUATEMI2", ["Andressa","Diego"])

def relatorio_nort():
    relatorio_carteira("NORTE SHOP", ["Jairo","Wander"])

def relatorio_barra():
    relatorio_carteira("BARRA", ["Igor","Carol","Alana"])

def relatorio_piedade():
    relatorio_carteira("PIEDADE", ["DiegoL","Marcus"])

def relatorio_lapa():
    relatorio_carteira("LAPA", ["Sara","Rafel"])

def relatorio_boulevard():
    relatorio_carteira("BOULEVARD", ["Camyla","Bruno","Gilvania"])

def relatorio_intinerantes():
    relatorio_carteira("INTINERANTES", ["Lazaro","Lee","MarcusI"])