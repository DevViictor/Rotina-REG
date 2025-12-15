import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image
from datetime import datetime

def visualizar_tarefas_gvs():

    # ---------------------------
    # CONFIGURAÇÃO DA PÁGINA
    # ---------------------------
    icon = Image.open("image/vivo.png")
    st.set_page_config(
        page_title="R.E.G - GVS",
        page_icon=icon,
        layout="wide"
    )

    # ---------------------------
    # CONTROLE DE ACESSO
    # ---------------------------
    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GVS DE VICTOR",
        "TODOS OS GLS(GERAL)",
        "TODOS OS GLS(ABERTURA)",
        "TODOS OS GLS(INTERMEDIO)",
        "TODOS OS GLS(FECHAMENTO)",
        "GLS DA CARTEIRA DE FABIANA",
        "GLS DA CARTEIRA DE FELIPE",
        "GLS DA CARTEIRA DE CHRYS",
        "GLS DA CARTEIRA DE JOHN",
        "TODOS OS ITINERANTES"
        ]

    lojas_por_carteira = {
        "GVS DE VICTOR": ["REGIONAL"],
        "TODOS OS GLS(GERAL)": ["GLS(GERAL)"],
        "TODOS OS GLS(ABERTURA)":["GLS(ABERTURA)"],
        "TODOS OS GLS(INTERMEDIO)":["GLS(INTERMEDIO)"],
        "TODOS OS GLS(FECHAMENTO)":["GLS(FECHAMENTO)"],
        "GLS DA CARTEIRA DE FABIANA": [
            "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA PARALELA","LOJA PARQUE SHOP"
        ],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
        ],
        "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
        ],
        "GLS DA CARTEIRA DE CHRYS": [
            "LOJA BOULEVARD"
        ],
        "TODOS OS ITINERANTES": ["ITINERANTES"]                 
    }

    nomes_por_loja = {
        "REGIONAL": ["Todos","Fabiana", "Felipe", "John", "Chrys"],
        "GLS(GERAL)":["GLS(GERAL)"],
        "GLS(ABERTURA)":["GLS(ABERTURA)"],
        "GLS(INTERMEDIO)":["GLS(INTERMEDIO)"],
        "GLS(FECHAMENTO)":["GLS(FECHAMENTO)"],
        "TODOS OS ITINERANTES": ["ITINERANTES"],
        "LOJA SSA |": ["Ana","Francisca","Vinicius"],
        "LOJA SSA ||": ["Vitor","Mailan"],
        "LOJA BELA VISTA": ["Vanessa","Danilo"],
        "LOJA PARALELA": ["Crislaine","Neide"],
        "LOJA PARQUE SHOP": ["Denise_Parque","Adrielle"],
        "LOJA IGUATEMI | BA": ["Max","Denise"],
        "LOJA IGUATEMI || BA": ["Diego","Andressa"],
        "LOJA NORT SHOP": ["Jairo","Wanderlei"],
        "LOJA BARRA": ["Igor","Carol","Alana"],
        "LOJA PIEDADE": ["DiegoL","Marcusl"],
        "LOJA LAPA": ["Sara","Rafael"],
        "LOJA BOULEVARD": ["Camyla","Bruno","Gilvania"],
        "ITINERANTES": ["Lázaro","Lee","Marcus"],
    }

    # ---------------------------
    # INTERFACE
    # ---------------------------
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    with col2:
        loja = st.selectbox(
            "Selecione a loja:",
            lojas_por_carteira.get(carteira, [])
        )

    with col3:
        nome = st.selectbox(
            "Nome:",
            nomes_por_loja.get(loja, [])
        )

    with col4:
        data_selecionada = st.date_input(
            "Selecione o período:",
            value=(datetime.today(), datetime.today())
        )

    # ---------------------------
    # GOOGLE SHEETS
    # ---------------------------
    gcp_info = st.secrets["tafgl"]
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

    aba = planilha.worksheet(nome)
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    # ---------------------------
    # TRATAMENTO DOS DADOS
    # ---------------------------
    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return
    # ---------------------------
    # FILTRO POR DATA
    # ---------------------------
    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio) &
        (planilha_Dados["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CONTAGENS (COM FILTRO)
    # ---------------------------
    contagemT = planilha_filtrada["Situação da tarefa"].count()

    contagemC = (
        planilha_filtrada["Situação da tarefa"]
        .astype(str)
        .str.contains("Concluído", case=False, na=False)
        .sum()
    )

    contagemP = (
        planilha_filtrada["Situação da tarefa"]
        .astype(str)
        .str.contains("Pendente", case=False, na=False)
        .sum()
    )

    col11, col12, col13 = st.columns(3)
    with col11:
        st.text(f"📝 Total de Tarefas: {contagemT}")
    with col12:
        st.text(f"🟢 Concluídas: {contagemC}")
    with col13:
        st.text(f"🟡 Pendentes: {contagemP}")

    

    # ---------------------------
    # TABELA FINAL
    # ---------------------------
    st.dataframe(planilha_filtrada, use_container_width=True)

    if st.button("Atualizar"):
        st.rerun()