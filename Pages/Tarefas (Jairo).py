import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import datetime as dt
import requests


if "role" not in st.session_state or st.session_state.role != "Jairo":
    st.error("⚠️ Acesso negado!")
    st.stop()

# --- CONFIGURAÇÃO---
gcp_info = st.secrets["gcp"]
planilha_chave = st.secrets["planilha"]["chave"]

# Criar credenciais
creds = Credentials.from_service_account_info(
    dict(gcp_info),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

# --- CONEXÃO COM GOOGLE SHEETS ---
cliente = gspread.authorize(creds)
planilha = cliente.open_by_key(planilha_chave)
aba = planilha.worksheet("Jairo")

def carregar_pedidos():
    dados = aba.get_all_records()
    return pd.DataFrame(dados)

st.title("📝 REG")

planilha_Dados = carregar_pedidos()

st.set_page_config(page_title="Suas tarefas",layout="wide",page_icon="👤")


if "Situação da tarefa" in planilha_Dados.columns:
    planilha_Dados["Situação da tarefa"] = planilha_Dados["Situação da tarefa"].apply(
        lambda x: True if str(x).strip().lower() == "concluído" else False
    )

editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Situação da tarefa": st.column_config.CheckboxColumn(
                "Situação da tarefa",
                help="Marque quando a tarefa for concluída",
            )
        },
        hide_index=True
    )

col1,col2,col3,col4 = st.columns(4)

with col1:
    if st.button("Confirmar tarefa ✅"):
            
        df_original = carregar_pedidos()

        st.success("Planilha atualizada!")

        for _, linha_editada in editado.iterrows():

            id_atual = linha_editada["ID"]  
            linha_original = df_original[df_original["ID"] == id_atual]

            if linha_original.empty:
                continue

            idx_sheet = linha_original.index[0] + 2  

            # --- COLUNAS CORRETAS ---
            coluna_diario = df_original.columns.get_loc("Situação da tarefa") + 1

            valor_checkbox = linha_editada["Situação da tarefa"]

            valor_salvo = "concluído" if valor_checkbox else "Pendente"

            # --- ATUALIZA AMBAS AS COLUNAS ---
            aba.update_cell(idx_sheet, coluna_diario, valor_salvo)

with col2:
    if st.button("Atualizar tarefas 🔄"):
        st.rerun()
