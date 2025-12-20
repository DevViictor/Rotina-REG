import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image
from datetime import datetime, timedelta


def tarefas_iguatemi_abertura():


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
            "GLS DA CARTEIRA DE FELIPE",
                ]
            
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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Max",
            "Iguatemi |",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Denise",
            "Iguatemi |",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Andressa",
            "Iguatemi ||",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
            aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
            agora = datetime.now()

            aba_exec.append_row([
                row["ID"],
                row["Título"],
                row["Descrição da tarefa"],
                "Diego",
                "Iguatemi ||",
                agora.strftime("%d/%m/%Y"),
                agora.strftime("%H:%M:%S")
            ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()







def tarefas_nort_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G NORT", page_icon=icon, layout="wide")

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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Jairo",
            "NORT SHOP",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Wanderlei",
            "NORT SHOP",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Mércia",
            "SSA |",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(INTERMEDIO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Francisca",
            "SSA |",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Vinicicus",
            "SSA |",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Vitor",
            "SSA ||",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Mailan",
            "SSA ||",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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

    colunas_desejadas = ["ID", "Criada", "Título","Descrição da tarefa","Hora inicial","Hora final", "Tipo de recorrência","Mailan"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Danilo",
            "BELA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Vanessa",
            "BELA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Crislaine",
            "PARALELA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Neide",
            "PARALELA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "DENISE_PARQUE",
            "PARQUE",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "ADRIELLE",
            "PARQUE",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Carol",
            "BARRA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(INTERMEDIO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Alana",
            "BARRA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Igor",
            "BARRA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Marcus",
            "PIEDADE",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Diego",
            "PIEDADE",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "RAFAEL",
            "LAPA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Sara",
            "LAPA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Maise",
            "DIAS DAVILA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])
    
    def registrar_execucao2(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(INTERMEDIO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Maise",
            "DIAS DAVILA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])
    
    def registrar_execucao3(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Maise",
            "DIAS DAVILA",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                        registrar_execucao2(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                        registrar_execucao3(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Bruno",
            "BOULEVARD",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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

    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Gilvania",
            "BOULEVARD",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

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
    
    "LOJA BOULEVARD": ["GLS(INTERMEDIO)"],
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
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(FECHAMENTO)")
        agora = datetime.now()

        aba_exec.append_row([
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Camyla",
            "BOULEVARD",
            agora.strftime("%d/%m/%Y"),
            agora.strftime("%H:%M:%S")
        ])

    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]


    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = False

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

  

    # ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )

                st.success("✔️ Execução registrada com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()







def tarefas_itinerante_lee():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LEE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerantes","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],

    "ITINERANTES": [
         "ITINERANTES"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["ITINERANTES"],
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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Tipo de recorrência","Lee"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Lee"].astype(str).str.lower() == "concluído"
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

    df_editado["Lee"] = df_editado["Concluir"].apply(
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

                    coluna_status = df_original.columns.get_loc("Lee") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Lee"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()





def tarefas_itinerante_marcus():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G Marcus", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerantes","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],

    "ITINERANTES": [
         "ITINERANTES"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["ITINERANTES"],
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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Tipo de recorrência","Marcus"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

   
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Marcus"].astype(str).str.lower() == "concluído"
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

    df_editado["Marcus"] = df_editado["Concluir"].apply(
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

                    coluna_status = df_original.columns.get_loc("Marcus") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Marcus"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()





def tarefas_itinerante_lazaro():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G Lázaro", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerantes","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],

    "ITINERANTES": [
         "ITINERANTES"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["ITINERANTES"],
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

    colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final", "Tipo de recorrência","Lázaro"]
    planilha_Dados = planilha_Dados[colunas_desejadas]

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    planilha_Dados["Concluir"] = (
        planilha_Dados["Lázaro"].astype(str).str.lower() == "concluído"
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

    df_editado["Lázaro"] = df_editado["Concluir"].apply(
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

                    coluna_status = df_original.columns.get_loc("Lázaro") + 1
                    aba.update_cell(linha_sheet, coluna_status, row["Lázaro"])

            st.success("✔️ Alterações salvas com sucesso!")

    with col12:
        if st.button("Atualizar"):
            st.rerun()














