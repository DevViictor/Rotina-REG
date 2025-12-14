import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image

icon = Image.open("image/vivo.png")


def tarefas_itinerantes():


    # Controle de estado das notificações
    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Itinerantes":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = ["TODOS OS ITINERANTES"]

    lojas_por_carteira = {
        " ": [" "],
        "TODOS OS ITINERANTES": [
            "ITINERANTES"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "ITINERANTES": ["Lázaro","Lee","Marcus"],
    }

    # ---------------------------
    # INTERFACE
    # ---------------------------
    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data_selecionada = st.date_input("Selecione a data:")

    # ---------------------------
    # CONFIGURAÇÃO GOOGLE SHEETS
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

    def carregar_pedidos():
        aba = planilha.worksheet(nome)
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    # Padronizar colunas para evitar erro
    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    # Converter data da planilha
    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    # Filtrar pela data escolhida
    planilha_filtrada = planilha_Dados[planilha_Dados["Data"] == data_selecionada]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # 🔥 NOTIFICAÇÕES
    # ---------------------------
    # ---------------------------
    planilha_filtrada["Concluir"] = (
        planilha_filtrada["Situação da tarefa"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_filtrada,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Situação da tarefa"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
        if st.button("Salvar alterações"):
            aba = planilha.worksheet(nome)
            dados_atual = aba.get_all_records()
            df_original = pd.DataFrame(dados_atual)

            for _, row in df_editado.iterrows():
                tarefa_id = row["ID"]

                linhas = df_original.index[df_original["ID"] == tarefa_id].tolist()

                if linhas:
                    linha_sheet = linhas[0] + 2
                    coluna_status = df_original.columns.get_loc("Situação da tarefa") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Situação da tarefa"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()