import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image

# --- CONFIG GOOGLE SHEETS (executa apenas uma vez) ---
if "planilha" not in st.session_state:
    st.session_state.planilha = {}

    # Credenciais e chave da planilha
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

    # Carregar todas as abas
    abas = {aba.title: pd.DataFrame(aba.get_all_records()) for aba in planilha.worksheets()}

    # Mapear cada consultor para sua aba correspondente
    st.session_state.planilha = {
        # LOJA SSA 1
        "Ana": abas.get("LOJA SSA 1", pd.DataFrame()),
        "Francisca": abas.get("LOJA SSA 1", pd.DataFrame()),
        "Vinicius": abas.get("LOJA SSA 1", pd.DataFrame()),
        # LOJA SSA 2
        "Vitor": abas.get("LOJA SSA 2", pd.DataFrame()),
        "Mailan": abas.get("LOJA SSA 2", pd.DataFrame()),
        # LOJA BELA VISTA
        "Vanessa": abas.get("LOJA BELA VISTA", pd.DataFrame()),
        "Danilo": abas.get("LOJA BELA VISTA", pd.DataFrame()),
        # LOJA PARALELA
        "Crislaine": abas.get("LOJA PARALELA", pd.DataFrame()),
        "Neide": abas.get("LOJA PARALELA", pd.DataFrame()),
        # LOJA PARQUE
        "Denise": abas.get("LOJA PARQUE", pd.DataFrame()),
        "Adriele": abas.get("LOJA PARQUE", pd.DataFrame()),
        # LOJA BOULEVARD (exemplo Chrys)
        "Camyla": abas.get("LOJA BOULEVARD", pd.DataFrame()),
        "Bruno": abas.get("LOJA BOULEVARD", pd.DataFrame()),
        "Gilvania": abas.get("LOJA BOULEVARD", pd.DataFrame()),
        # Continue adicionando todos os consultores e suas respectivas abas...
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

# --- Função para exibir cabeçalho com logo ---
def mostrar_cabecalho(titulo):
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo, width=100)
    with cola:
        st.header(titulo)

# --- Exemplo de relatório seguro ---
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

def relatorio_chrys_geral():
    if st.session_state.get("role") != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    mostrar_cabecalho("R.E.G - CHRYS REBOUÇAS")
    grupos = [
        (["Camyla", "Bruno","Gilvania"], "LOJA BOULEVARD")
    ]
    st.dataframe(pd.DataFrame([resumo_loja(cons, loja) for cons, loja in grupos]))
