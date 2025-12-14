import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image


def tarefas_fabiana():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G FABIANA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GV",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GV": [
            "MINHAS TAREFAS"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "MINHAS TAREFAS": ["Todos","Fabiana"],
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
    gcp_info = st.secrets["fabi"]
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
        st.warning("Nenhum modelo encontrado.")
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




def tarefas_felipe():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G FELIPE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GV",
        
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GV": [
            "MINHAS TAREFAS"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "MINHAS TAREFAS": ["Todos","Felipe"],
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
    gcp_info = st.secrets["fel"]
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
        st.warning("Nenhum modelo encontrado.")
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



def tarefas_john():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G JOHN", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GV",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GV": [
            "MINHAS TAREFAS"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "MINHAS TAREFAS": ["Todos","John"],
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
    gcp_info = st.secrets["joh"]
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
        st.warning("Nenhum modelo encontrado.")
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


def tarefas_chyrs():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G CHRYS", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GV",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GV": [
            "MINHAS TAREFAS"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "MINHAS TAREFAS": ["Todos","Chrys"],
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

    def carregar_pedidos():
        aba = planilha.worksheet(nome)
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if planilha_Dados.empty:
        st.warning("Nenhum modelo encontrado.")
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
