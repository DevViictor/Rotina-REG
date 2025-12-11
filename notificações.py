import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime, timedelta


def verificar_notificacoes(abas):
    # Configuração Google Sheets
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

    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    agora = datetime.now()

    def enviar_pushover(msg):
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": st.secrets["notificacao"]["api_token"],
            "user": st.secrets["notificacao"]["user_key"],
            "message": msg,
            "priority": 1
        })

    # Checar todas as abas
    for nome in abas:
        aba = planilha.worksheet(nome)
        dados = aba.get_all_records()
        df = pd.DataFrame(dados)
        if not dados:
            continue
        df.columns = df.columns.map(lambda x: str(x).strip())
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce").dt.date

        for _, linha in df.iterrows():

            titulo = linha["Título"]
            loja_tarefa = linha["Loja"]
            gls_nome = linha["GL"]

            data_str = linha["Data"]
            inicio_str = linha["Hora inicial"]
            fim_str = linha["Hora final"]

            # Filtro: somente tarefas do dia atual
            hoje = datetime.now().date()
            if data_str != hoje:
                continue

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

            # Notificação 15 minutos antes do início
            if inicio - timedelta(minutes=15) <= agora < inicio:
                if chave_inicio not in st.session_state.notificados:
                    enviar_pushover(
                        f"⏳ Em 15 minutos começa o periodo de realização da tarefa: {titulo} na loja {gls_nome}"
                    )
                    st.session_state.notificados[chave_inicio] = True

            # Notificação 15 minutos antes do fim
            if fim - timedelta(minutes=15) <= agora < fim:
                if chave_fim not in st.session_state.notificados:
                    enviar_pushover(
                        f"⏰ Faltam 15 minutos para terminar a tarefa: {titulo} \n GL: {gls_nome}\n Loja: {loja_tarefa}"
                    )
                    st.session_state.notificados[chave_fim] = True


def notificacoes_fabiana():
    verificar_notificacoes(["Ana", "Francisca", "Vinicius","Vitor","Mailan","Vanessa","Danilo","Crislaine","Neide","Denise_Parque"])

def notificacoes_felipe():
    verificar_notificacoes(["Max", "Denise", "Felipe","Diego","Andressa","Jairo","Wanderlei"])

def notificacoes_john():
    verificar_notificacoes(["Igor","Carol","Alana","DiegoL","Marcusl","Sara","Rafel"])

def notificacoes_chrys():
    verificar_notificacoes(["Camyla","Bruno","Gilvania"])

def notificacoes_itinerantes():
    verificar_notificacoes(["Lázaro","Lee","Marcus"])

