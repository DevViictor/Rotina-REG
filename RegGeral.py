import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image

# --- CONFIG GOOGLE SHEETS (somente uma vez) ---
if "planilha" not in st.session_state:
    gcp_info = st.secrets["gcp"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    st.session_state.planilha = {}
    
    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_key(planilha_chave)

    # Carregar todas as abas de uma vez
    st.session_state.planilha = {
        aba.title: pd.DataFrame(aba.get_all_records()) for aba in planilha.worksheets()
    }

# --- Função genérica para carregar dados de cada consultor ---
def carregar_pedidos(consultor):
    df = st.session_state.planilha.get(consultor, pd.DataFrame())
    if not df.empty and "Situação da tarefa" in df.columns:
        df["Situação da tarefa"] = df["Situação da tarefa"].apply(
            lambda x: str(x).strip().lower() == "concluído"
        )
    return df

# --- Função genérica para criar resumo de uma loja ---
def resumo_loja(lista_consultores, nome_loja):
    total_concluidas = 0
    total_pendentes = 0
    total_geral = 0

    for consultor in lista_consultores:
        df = carregar_pedidos(consultor)
        if not df.empty:
            concluidas = df["Situação da tarefa"].sum()
            pendentes = len(df) - concluidas
            total_concluidas += concluidas
            total_pendentes += pendentes
            total_geral += len(df)

    percentual = round((total_concluidas / total_geral) * 100, 1) if total_geral > 0 else 0
    return {
        "Loja": nome_loja,
        "Concluídas": total_concluidas,
        "Pendentes": total_pendentes,
        "Percentual Concluído": f"{percentual}%"
    }

# --- Função genérica para exibir cabeçalho com logo ---
def mostrar_cabecalho(titulo):
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.header(titulo)

# --- RELATÓRIOS ---
def relatorio_fabiana_geral():
    if st.session_state.get("role") != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    mostrar_cabecalho("R.E.G - FABIANA SACRAMENTO")
    grupos = [
        (["Ana", "Francisca", "Vinicius"], "LOJA SSA 1"),
        (["Vitor", "Mailan"], "LOJA SSA 2"),
        (["Vanessa", "Danilo"], "LOJA BELA VISTA"),
        (["Crislaine", "Neide"], "LOJA PARALELA"),
        (["Denise", "Adriele"], "LOJA PARQUE")
    ]
    st.dataframe(pd.DataFrame([resumo_loja(cons, loja) for cons, loja in grupos]))

def relatorio_felipe_geral():
    if st.session_state.get("role") != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop() 

    mostrar_cabecalho("R.E.G - FELIPE SILVA")
    grupos = [
        (["Max", "Denise"], "LOJA IGUATEMI 1"),
        (["Diego", "Andressa"], "LOJA IGUATEMI 2"),
        (["Jairo", "Wanderlei"], "LOJA NORTE SHOP")
    ]
    st.dataframe(pd.DataFrame([resumo_loja(cons, loja) for cons, loja in grupos]))

def relatorio_john_geral():
    if st.session_state.get("role") != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    mostrar_cabecalho("R.E.G - JOHN COITO")
    grupos = [
        (["Igor", "Carol","Alana"], "LOJA BARRA"),
        (["DiegoL", "Marcus"], "LOJA PIEDADE"),
        (["Sara", "Rafael"], "LOJA LAPA")
    ]
    st.dataframe(pd.DataFrame([resumo_loja(cons, loja) for cons, loja in grupos]))

def relatorio_chrys_geral():
    if st.session_state.get("role") != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    mostrar_cabecalho("R.E.G - CHRYS REBOUÇAS")
    grupos = [
        (["Camyla", "Bruno","Gilvania"], "LOJA BOULEVARD")
    ]
    st.dataframe(pd.DataFrame([resumo_loja(cons, loja) for cons, loja in grupos]))
