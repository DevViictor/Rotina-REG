import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image


icon = Image.open("image/vivo.png")

def tarefas_max():

    st.set_page_config(page_title="R.E.G MAX", page_icon=icon,layout="wide")

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

    cola,colb,colc = st.columns([7,1,1])

    with colc :
        st.image(image_logo)

    with cola:
         st.title("📝 R.E.G - MAX")

 
    # --- Função para carregar pedidos de uma aba ---
    def carregar_pedidos():
        try:
            aba = planilha.worksheet("Max")
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
        st.markdown(f"**Consultor:** Max")
        st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

        # --- Mostrar DataFrame ---
        st.dataframe(df_consultor)


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

    cola,colb,colc = st.columns([7,1,1])

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

    cola,colb,colc = st.columns([7,1,1])

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

    cola,colb,colc = st.columns([7,1,1])

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

    cola,colb,colc = st.columns([7,1,1])

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

    cola,colb,colc = st.columns([7,1,1])

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


































