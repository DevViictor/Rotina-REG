import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image
from datetime import datetime, timedelta
import requests

def visualizar_tarefas_gvs():

    def enviar_pushover(msg):
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": st.secrets["notificacao"]["api_token"],
            "user": st.secrets["notificacao"]["user_key"],
            "message": msg,
            "priority": 1
        })

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G - GVS", page_icon=icon,layout="wide")

        # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # Controle de estado das notificações
    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = ["GVS DE VICTOR"]

    lojas_por_carteira = {
        " ": [" "],
        "GVS DE VICTOR": [
           "REGIONAL"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "REGIONAL": ["Todos","Fabiana","Felipe", "John","Chrys"],
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
    
    st.dataframe(planilha_Dados)