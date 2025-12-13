import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image
from datetime import datetime, timedelta

icon = Image.open("image/vivo.png")



def tarefas_max():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "GLS DA CARTEIRA DE FELIPE",
            ]
        
    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
                "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
        ]
        }

    nomes_por_loja = {
        " ": [" "],
      
        "LOJA IGUATEMI | BA": ["Todos Iguatemi |","Max","Denise"],
        "LOJA IGUATEMI || BA": ["Todos Iguatemi ||","Diego","Andressa"],
        "LOJA NORT SHOP": ["Jairo","Wanderlei"],
        }



    st.set_page_config(page_title="R.E.G MAX", page_icon=icon,layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Felipe":
        st.error("⚠️ Acesso negado!")
        st.stop()
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

    contagemT = planilha_Dados["Situação da tarefa"].count()
    contagemC = planilha_Dados["Situação da tarefa"].astype(str).str.contains("Concluído",case=False,na=False).sum()
    contagemP = planilha_Dados["Situação da tarefa"].astype(str).str.contains("Pendente",case=False,na=False).sum()

    col11,col12,col13 = st.columns(3)
    with col11:
        st.text(f"📝 Total de Tarefas : {contagemT}")

    with col12:
        st.text(f" 🟢 Tarefas Concluídas : {contagemC}")

    with col13:
        st.text(f" 🟡 Tarefas Pendentes: {contagemP}")


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
    

    st.dataframe(planilha_Dados)


def tarefas_denise():

    st.set_page_config(page_title="R.E.G DENISE", page_icon=icon,layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Felipe":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- Configuração Google Sheets ---
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


    # --- Função de notificação ---
    def notificacao(mensagem):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": api_token,
            "user": user_key,
            "message": f"Olá {"Denise"}, {mensagem}"
        })


    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
         st.title("📝 R.E.G - DENISE")

 
    # --- Função para carregar pedidos de uma aba ---
    def carregar_pedidos():
        try:
            aba = planilha.worksheet("Denise")
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(lambda x: str(x).strip().lower() == "concluído")
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Função para verificar tarefas prestes a vencer e enviar notificação ---
   

    # --- Carregar dados do consultor selecionado ---
    df_consultor = carregar_pedidos()

    if df_consultor.empty:
        st.warning("Nenhuma tarefa encontrada para este consultor.")
    else:
        # --- Verificar e notificar automaticamente ---

        # --- Contagem de pendentes e concluídas ---
        concluidas = df_consultor["Situação da tarefa"].sum()
        pendentes = len(df_consultor) - concluidas
        st.markdown(f"**Consultor:** Denise")
        st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

        # --- Mostrar DataFrame ---
        st.dataframe(df_consultor)


#IGUATEMI2

def tarefas_diego():

    st.set_page_config(page_title="R.E.G DIEGO", page_icon=icon,layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Felipe":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- Configuração Google Sheets ---
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


    # --- Função de notificação ---
    def notificacao(mensagem):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": api_token,
            "user": user_key,
            "message": f"Olá {"DIEGO"}, {mensagem}"
        })


    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
         st.title("📝 R.E.G - DIEGO")

 
    # --- Função para carregar pedidos de uma aba ---
    def carregar_pedidos():
        try:
            aba = planilha.worksheet("Diego")
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(lambda x: str(x).strip().lower() == "concluído")
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Função para verificar tarefas prestes a vencer e enviar notificação ---
   
    # --- Carregar dados do consultor selecionado ---
    df_consultor = carregar_pedidos()

    if df_consultor.empty:
        st.warning("Nenhuma tarefa encontrada para este consultor.")
    else:
        # --- Verificar e notificar automaticamente ---

        # --- Contagem de pendentes e concluídas ---
        concluidas = df_consultor["Situação da tarefa"].sum()
        pendentes = len(df_consultor) - concluidas
        st.markdown(f"**Consultor:** DIEGO")
        st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

        # --- Mostrar DataFrame ---
        st.dataframe(df_consultor)

def tarefas_andressa():

    st.set_page_config(page_title="R.E.G ANDRESSA", page_icon=icon,layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Felipe":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- Configuração Google Sheets ---
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


    # --- Função de notificação ---
    def notificacao(mensagem):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": api_token,
            "user": user_key,
            "message": f"Olá {"Vanessa"}, {mensagem}"
        })


    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
         st.title("📝 R.E.G - ANDRESSA")

 
    # --- Função para carregar pedidos de uma aba ---
    def carregar_pedidos():
        try:
            aba = planilha.worksheet("Andressa")
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(lambda x: str(x).strip().lower() == "concluído")
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Função para verificar tarefas prestes a vencer e enviar notificação ---
    def verificar_e_notificar(df, consultor):
        agora = dt.datetime.now()
        avisos = []
        for _, row in df.iterrows():
            if not row.get("Situação da tarefa", False) and "Hora final" in row:
                try:
                    hora_limite = dt.datetime.strptime(str(row["Hora final"]), "%H:%M")
                    hora_limite = hora_limite.replace(year=agora.year, month=agora.month, day=agora.day)
                    if 0 <= (hora_limite - agora).total_seconds() <= 1800:  # próximas 30 min
                        avisos.append(f"Tarefa '{row['Tarefa']}' vence às {row['Hora final']}")
                except:
                    continue
        if avisos:
            mensagem = "Você tem tarefas prestes a vencer! " + " | ".join(avisos)
            notificacao(consultor, mensagem)
        return avisos

    # --- Carregar dados do consultor selecionado ---
    df_consultor = carregar_pedidos()

    if df_consultor.empty:
        st.warning("Nenhuma tarefa encontrada para este consultor.")
    else:
        # --- Verificar e notificar automaticamente ---

        # --- Contagem de pendentes e concluídas ---
        concluidas = df_consultor["Situação da tarefa"].sum()
        pendentes = len(df_consultor) - concluidas
        st.markdown(f"**Consultor:** Andressa")
        st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

        # --- Mostrar DataFrame ---
        st.dataframe(df_consultor)

#NORTH

def tarefas_jairo():

    st.set_page_config(page_title="R.E.G JAIRO", page_icon=icon,layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Felipe":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- Configuração Google Sheets ---
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


    # --- Função de notificação ---
    def notificacao(mensagem):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": api_token,
            "user": user_key,
            "message": f"Olá {"Vanessa"}, {mensagem}"
        })


    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
         st.title("📝 R.E.G - JAIRO")

 
    # --- Função para carregar pedidos de uma aba ---
    def carregar_pedidos():
        try:
            aba = planilha.worksheet("Jairo")
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(lambda x: str(x).strip().lower() == "concluído")
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Função para verificar tarefas prestes a vencer e enviar notificação ---
    def verificar_e_notificar(df, consultor):
        agora = dt.datetime.now()
        avisos = []
        for _, row in df.iterrows():
            if not row.get("Situação da tarefa", False) and "Hora final" in row:
                try:
                    hora_limite = dt.datetime.strptime(str(row["Hora final"]), "%H:%M")
                    hora_limite = hora_limite.replace(year=agora.year, month=agora.month, day=agora.day)
                    if 0 <= (hora_limite - agora).total_seconds() <= 1800:  # próximas 30 min
                        avisos.append(f"Tarefa '{row['Tarefa']}' vence às {row['Hora final']}")
                except:
                    continue
        if avisos:
            mensagem = "Você tem tarefas prestes a vencer! " + " | ".join(avisos)
            notificacao(consultor, mensagem)
        return avisos

    # --- Carregar dados do consultor selecionado ---
    df_consultor = carregar_pedidos()

    if df_consultor.empty:
        st.warning("Nenhuma tarefa encontrada para este consultor.")
    else:
        # --- Verificar e notificar automaticamente ---

        # --- Contagem de pendentes e concluídas ---
        concluidas = df_consultor["Situação da tarefa"].sum()
        pendentes = len(df_consultor) - concluidas
        st.markdown(f"**Consultor:** Jairo")
        st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

        # --- Mostrar DataFrame ---
        st.dataframe(df_consultor)

def tarefas_wanderlei():

    st.set_page_config(page_title="R.E.G WANDERLEI", page_icon=icon,layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Felipe":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- Configuração Google Sheets ---
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


    # --- Função de notificação ---
    def notificacao(mensagem):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": api_token,
            "user": user_key,
            "message": f"Olá {"Vanessa"}, {mensagem}"
        })


    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
         st.title("📝 R.E.G - WANDERLEI")

 
    # --- Função para carregar pedidos de uma aba ---
    def carregar_pedidos():
        try:
            aba = planilha.worksheet("Wanderlei")
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(lambda x: str(x).strip().lower() == "concluído")
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Função para verificar tarefas prestes a vencer e enviar notificação ---
    def verificar_e_notificar(df, consultor):
        agora = dt.datetime.now()
        avisos = []
        for _, row in df.iterrows():
            if not row.get("Situação da tarefa", False) and "Hora final" in row:
                try:
                    hora_limite = dt.datetime.strptime(str(row["Hora final"]), "%H:%M")
                    hora_limite = hora_limite.replace(year=agora.year, month=agora.month, day=agora.day)
                    if 0 <= (hora_limite - agora).total_seconds() <= 1800:  # próximas 30 min
                        avisos.append(f"Tarefa '{row['Tarefa']}' vence às {row['Hora final']}")
                except:
                    continue
        if avisos:
            mensagem = "Você tem tarefas prestes a vencer! " + " | ".join(avisos)
            notificacao(consultor, mensagem)
        return avisos

    # --- Carregar dados do consultor selecionado ---
    df_consultor = carregar_pedidos()

    if df_consultor.empty:
        st.warning("Nenhuma tarefa encontrada para este consultor.")
    else:
        # --- Verificar e notificar automaticamente ---

        # --- Contagem de pendentes e concluídas ---
        concluidas = df_consultor["Situação da tarefa"].sum()
        pendentes = len(df_consultor) - concluidas
        st.markdown(f"**Consultor:** Wanderlei")
        st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

        # --- Mostrar DataFrame ---
        st.dataframe(df_consultor)


































