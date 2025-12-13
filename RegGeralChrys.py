import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image


def obter_resumo(planilha, consultores):
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            df = pd.DataFrame(aba.get_all_records())
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except:
            return pd.DataFrame()

    resumo = []
    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual": 0
            })
        else:
            concluidas = df["Situação da tarefa"].sum()
            pendentes = len(df) - concluidas
            percentual = round((concluidas / len(df)) * 100, 1)

            resumo.append({
                "Consultor": consultor,
                "Concluídas": concluidas,
                "Pendentes": pendentes,
                "Percentual": percentual
            })

    return pd.DataFrame(resumo)



# --- Função genérica para qualquer carteira ---
def relatorio_carteira(nome_carteira, consultores):
    # Controle de acesso
    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # Configuração Google Sheets
    gcp_info = st.secrets["chr"]
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


def relatorio_boulevard():
    relatorio_carteira("BOULEVARD", ["Camyla","Bruno","Gilvania"])
