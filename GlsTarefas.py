import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image
from datetime import datetime, timedelta


def tarefas_iguatemi():

    def enviar_pushover(msg):
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": st.secrets["notificacao"]["api_token"],
            "user": st.secrets["notificacao"]["user_key"],
            "message": msg,
            "priority": 1
        })

    # Controle de estado das notificações
    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Iguatemi1":
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
        "LOJA IGUATEMI | BA": ["GLS","Todos Iguatemi |","Max", "Denise"],
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
        st.warning("Nenhum modelo encontrado.")
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
    agora = datetime.now()

    for _, linha in planilha_filtrada.iterrows():

        titulo = linha["Título"]
        loja_tarefa = linha["Loja"]
        gls_nome = linha["GL"]

        data_str = linha["Data"]
        inicio_str = linha["Hora inicial"]
        fim_str = linha["Hora final"]

        # Converter para datetime
        try:
            inicio = datetime.combine(
                data_str,
                datetime.strptime(inicio_str, "%H:%M").time()
            )

            fim = datetime.combine(
                data_str,
                datetime.strptime(fim_str, "%H:%M").time()
            )
        except:
            continue

        chave_inicio = f"{titulo}_{inicio}_ANTES"
        chave_fim = f"{titulo}_{fim}_DEPOIS"

        # 🔥 1) Notificação 15 minutos ANTES
        if inicio - timedelta(minutes=15) <= agora < inicio:
            if chave_inicio not in st.session_state.notificados:
                enviar_pushover(
                    f"⏳ Em 15 minutos começa o periodo de realização da tarefa: {titulo} na loja {gls_nome}"
                )
                st.session_state.notificados[chave_inicio] = True

        # 🔥 2) Notificação 15 minutos DEPOIS
        # Notificação 15 minutos DEPOIS (janela de 5 minutos)
        if fim - timedelta(minutes=15) <= agora < fim:
            if chave_fim not in st.session_state.notificados:
                enviar_pushover(
                    f"⏰ Faltam 15 minutos para terminar a tarefa: {titulo} \n GL: {gls_nome}\n Loja: {loja_tarefa}"
                )
                st.session_state.notificados[chave_fim] = True
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

    # 🔄 Atualiza a página a cada 60s para verificar notificações


def tarefas_iguatemi2():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Iguatemi2":
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
        "LOJA IGUATEMI || BA": ["GLS","Todos Iguatemi ||""Diego","Andressa"],
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



def tarefas_nort():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Nort":
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
    "LOJA NORT SHOP": ["GLS","Todos Norte","Jairo","Wanderlei"],
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

#Fabiana


def tarefas_ssa1():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR1", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Salvador1":
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
    "LOJA SSA |": ["GLS","Todos SSA |","Ana","Francisca","Vinicius"],   
    
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


def tarefas_ssa2():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Salvador2":
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
    "LOJA SSA ||": ["Vitor","Mailan","Todos SSA ||"],
    
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


def tarefas_bela():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BELA VISTA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Bela":
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
    
    "LOJA BELA VISTA": ["Todos SSA |","Todos Bela","Vanessa","Danilo"]
    
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


def tarefas_parela():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARALELA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Paralela":
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
        "LOJA BELA VISTA"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA BELA VISTA": ["GLS","Todos Paralela","Vanessa","Danilo"]
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


def tarefas_parque():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARQUE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Parque":
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
    
    "LOJA PARQUE SHOP": ["GLS","Todos Parque","Denise_Parque","Neide"],
    
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


#LOJAS JOHN

def tarefas_barra():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Barra":
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

    "LOJA BARRA": ["GLS","Todos Barra","Igor","Carol","Alana"],
    
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



def tarefas_piedade():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PIEDADE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Piedade":
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
    "LOJA PIEDADE": ["GLS","Todos Piedade","DiegoL","Marcus"],
    
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


def tarefas_lapa():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LAPA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Lapa":
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
    
    "LOJA LAPA": ["GLS","Todos Lapa","Sara","Rafael"],
   
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



def tarefas_itinerante():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G ITINERANTE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Itinerante":
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
    
    "ITINERANTES": ["Lázaro","Lee","Marcus","Todos Itinerantes"],
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
        

def tarefas_boulevard():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Boulevard":
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
    
    "LOJA BOULEVARD": ["GLS","Todos Boulevard","Camyla","Bruno","Gilvania"],
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



