import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt

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

consultores = ["Andressa","Denise","Jairo","Max","Vanderlei","Diego"]

# --- Função de notificação ---
def notificacao(consultor, mensagem):
    user_key = st.secrets["notificacao"]["user_key"]
    api_token = st.secrets["notificacao"]["api_token"]
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": api_token,
        "user": user_key,
        "message": f"Olá {consultor}, {mensagem}"
    })

st.title("📝 REG - GERAL")

# --- Sidebar: seleção de consultor ---
consultor_selecionado = st.sidebar.selectbox("Selecione o consultor:", consultores)

# --- Função para carregar pedidos de uma aba ---
def carregar_pedidos(consultor):
    try:
        aba = planilha.worksheet(consultor)
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
df_consultor = carregar_pedidos(consultor_selecionado)

if df_consultor.empty:
    st.warning("Nenhuma tarefa encontrada para este consultor.")
else:
    # --- Verificar e notificar automaticamente ---
    avisos = verificar_e_notificar(df_consultor, consultor_selecionado)

    # --- Contagem de pendentes e concluídas ---
    concluidas = df_consultor["Situação da tarefa"].sum()
    pendentes = len(df_consultor) - concluidas
    st.markdown(f"**Consultor:** {consultor_selecionado}")
    st.markdown(f"**✅ Concluídas:** {concluidas}   |   **🕒 Pendentes:** {pendentes}")

    # --- Mostrar avisos ---
    if avisos:
        st.warning("\n".join(avisos))
    else:
        st.info("Nenhuma tarefa próxima do vencimento.")

    # --- Mostrar DataFrame ---
    st.dataframe(df_consultor)
