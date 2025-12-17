import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image
from datetime import datetime, timedelta


def tarefas_iguatemi_abertura():


    # Controle de estado das notificações
    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = ["GLS DA CARTEIRA DE FELIPE"]

    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI | BA"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "LOJA IGUATEMI | BA": ["GLS(ABERTURA)"],
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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Max"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


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
    planilha_filtrada["Concluir"] = (
        planilha_filtrada["Max"].astype(str).str.lower() == "concluído"
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

    df_editado["Max"] = df_editado["Concluir"].apply(
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
                    coluna_status = df_original.columns.get_loc("Max") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Max"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()

    # 🔄 Atualiza a página a cada 60s para verificar notificações


def tarefas_iguatemi_fechamento():



    # Controle de estado das notificações
    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = ["GLS DA CARTEIRA DE FELIPE"]

    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI | BA"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "LOJA IGUATEMI | BA": ["GLS(FECHAMENTO)"],
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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Denise"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


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
    planilha_filtrada["Concluir"] = (
        planilha_filtrada["Denise"].astype(str).str.lower() == "concluído"
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

    df_editado["Denise"] = df_editado["Concluir"].apply(
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
                    coluna_status = df_original.columns.get_loc("Denise") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Denise"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_iguatemi2_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi2","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GLS DA CARTEIRA DE FELIPE",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI || BA"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "LOJA IGUATEMI || BA": ["GLS(ABERTURA)"],
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Andressa"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Andressa"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Andressa"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Andressa") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Andressa"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_iguatemi2_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi2","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GLS DA CARTEIRA DE FELIPE",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI || BA"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "LOJA IGUATEMI || BA": ["GLS(FECHAMENTO)"],
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Diego"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Diego"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Diego"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Diego") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Diego"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()






def tarefas_nort_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Norte","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            
        "GLS DA CARTEIRA DE FELIPE",
    ]
           
        
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE FELIPE": [
            "LOJA NORT SHOP"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA NORT SHOP": ["GLS(ABERTURA)"]
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Jairo"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Jairo"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Jairo"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Jairo") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Jairo"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_nort_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G NORTE SHOP", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Norte","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            
        "GLS DA CARTEIRA DE FELIPE",
    ]
           
        
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE FELIPE": [
            "LOJA NORT SHOP"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA NORT SHOP": ["GLS(FECHAMENTO)"]
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Wanderlei"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Wanderlei"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Wanderlei"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Wanderlei") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Wanderlei"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


#Fabiana


def tarefas_ssa1_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["GLS(ABERTURA)"],   
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Ana"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Ana"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Ana"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Ana") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Ana"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()




def tarefas_ssa1_intermedio():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["GLS(INTERMEDIO)"],   
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Francisca"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Francisca"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Francisca"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Francisca") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Francisca"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()




def tarefas_ssa1_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["GLS(FECHAMENTO)"],   
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Vinicius"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Vinicius"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Vinicius"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Vinicius") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Vinicius"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_ssa2_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador2","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["GLS(ABERTURA)"],   
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Vitor"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Vitor"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Vitor"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Vitor") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Vitor"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_ssa2_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador2", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA SSA ||"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA ||": ["GLS(ABERTURA)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título" ,"Descrição da tarefa","Hora inicial","Hora final", "Data","Wanderlei"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Wanderlei"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Wanderlei"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Wanderlei") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Wanderlei"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_ssa2_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador2", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA SSA ||"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA ||": ["GLS(FECHAMENTO)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Mailan"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Mailan"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Mailan"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Mailan") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Mailan"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_bela_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BELA VISTA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Bela", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
                "GLS DA CARTEIRA DE FABIANA",
                ]
            
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA BELA VISTA"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BELA VISTA": ["GLS(ABERTURA)"]
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa", "Hora inicial","Hora final","Data","Danilo"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Danilo"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Danilo"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Danilo") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Danilo"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_bela_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BELA VISTA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Bela","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
                "GLS DA CARTEIRA DE FABIANA",
                ]
            
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA BELA VISTA"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BELA VISTA": ["GLS(FECHAMENTO)"]
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Vanessa"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Vanessa"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Vanessa"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Vanessa") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Vanessa"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_parela_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARALELA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Paralela", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()
   
    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        "GLS DA CARTEIRA DE FABIANA",]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA PARALELA"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PARALELA": ["GLS(ABERTURA)"]
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
        data = st.date_input("Selecione a data:")

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

    
    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Crislaine"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Crislaine"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Crislaine"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Crislaine") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Crislaine"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_parela_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARALELA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Paralela", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        "GLS DA CARTEIRA DE FABIANA",]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA PARALELA"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PARALELA": ["GLS(FECHAMENTO)"]
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
        data = st.date_input("Selecione a data:")

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
    
    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Neide"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Neide"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Neide"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Neide") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Neide"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



    
def tarefas_parque_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARQUE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Parque", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
           ]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA PARQUE SHOP"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA PARQUE SHOP": ["GLS(ABERTURA)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Denise_Parque"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Denise_Parque"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Denise_Parque"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Denise_Parque") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Denise_Parque"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_parque_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARQUE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Parque", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
           ]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA PARQUE SHOP"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA PARQUE SHOP": ["GLS(FECHAMENTO)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Adrielle"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Adrielle"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Adrielle"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Adrielle") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Adrielle"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()






#LOJAS JOHN

def tarefas_barra_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Barra", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
           ]
    
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA"
    ],
    
    }

    nomes_por_loja = {
    " ": [" "],

    "LOJA BARRA": ["GLS(ABERTURA)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Data","Carol"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Carol"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Carol"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Carol") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Carol"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_barra_intermedio():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Barra", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
           ]
    
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA"
    ],
    
    }

    nomes_por_loja = {
    " ": [" "],

    "LOJA BARRA": ["GLS(INTERMEDIO)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Alana"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Alana"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Alana"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Alana") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Alana"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()





def tarefas_barra_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Barra", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
           ]
    
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA"
    ],
    
    }

    nomes_por_loja = {
    " ": [" "],

    "LOJA BARRA": ["GLS(FECHAMENTO)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Igor"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Igor"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Igor"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Igor") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Igor"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()








def tarefas_piedade_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PIEDADE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in  ["Piedade","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        
            "GLS DA CARTEIRA DE JOHN",
            ]
        
    lojas_por_carteira = {
    " ": [" "],
    "TODOS OS GLS": [
                "LOJA PIEDADE",
            
    ],
  
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA PIEDADE"
    ]     
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PIEDADE": ["GLS(ABERTURA)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","DiegoP"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["DiegoP"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["DiegoP"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("DiegoP") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["DiegoP"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()




def tarefas_piedade_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PIEDADE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in  ["Piedade","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        
            "GLS DA CARTEIRA DE JOHN",
            ]
        
    lojas_por_carteira = {
    " ": [" "],
    "TODOS OS GLS": [
                "LOJA PIEDADE",
            
    ],
  
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA PIEDADE"
    ]     
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PIEDADE": ["GLS(FECHAMENTO)"],
    
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Marcosl"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Marcosl"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Marcosl"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Marcosl") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Marcosl"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()


def tarefas_lapa_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LAPA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Lapa", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
                ]
            
    lojas_por_carteira = {
    " ": [" "],
    
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA LAPA"
    
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA LAPA": ["GLS(ABERTURA)"],
   
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
        data = st.date_input("Selecione a data:")

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
    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Rafael"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Rafael"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Rafael"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Rafael") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Rafael"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()




def tarefas_lapa_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LAPA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Lapa", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
                ]
            
    lojas_por_carteira = {
    " ": [" "],
    
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA LAPA"
    
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA LAPA": ["GLS(FECHAMENTO)"],
   
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
        data = st.date_input("Selecione a data:")

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
    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Sara"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Sara"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Sara"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Sara") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Sara"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()





def tarefas_itinerante():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G ITINERANTE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerante", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "TODOS OS ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],
    
    "TODOS OS ITINERANTES": [
            "ITINERANTES"
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["Todos Itinerantes","Lázaro","Lee","Marcus"],
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
        data = st.date_input("Selecione a data:")

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

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Situação da tarefa"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
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
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Situação da tarefa") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Situação da tarefa"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()
        

def tarefas_diasdavila():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G DIAS DAVILA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Davila", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA DIAS DAVILA"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA DIAS DAVILA": ["GLS(ABERTURA)","GLS(INTERMEDIO)","GLS(FECHAMENTO)"],
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Maise"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Maise"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Maise"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Maise") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Maise"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_boulevard_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Boulevard","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE CHRYS": [
         "LOJA BOULEVARD"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BOULEVARD": ["GLS(ABERTURA)"],
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa", "Hora inicial","Hora final", "Data","Bruno"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Bruno"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Bruno"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Bruno") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Bruno"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()



def tarefas_boulevard_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Boulevard","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE CHRYS": [
         "LOJA BOULEVARD"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BOULEVARD": ["GLS(FECHAMENTO)"],
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Gilvania"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Gilvania"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Gilvania"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Gilvania") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Gilvania"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()




def tarefas_boulevard_intermedio():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Boulevard","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE CHRYS": [
         "LOJA BOULEVARD"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BOULEVARD": ["GLS(FECHAMENTO)"],
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
        data = st.date_input("Selecione a data:")

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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Data","Bruno"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

    if planilha_Dados.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Bruno"].astype(str).str.lower() == "concluído"
    )

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Concluir tarefa",
                help="Marque para concluir a tarefa"
            )
        },
        disabled=["Data", "ID"]
    )

    df_editado["Bruno"] = df_editado["Concluir"].apply(
        lambda x: "Concluído" if x else "Pendente"
    )

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
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
                    linha_sheet = linhas[0] + 2  # Cabeçalho + index base 1

                    coluna_status = df_original.columns.get_loc("Bruno") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Bruno"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()











