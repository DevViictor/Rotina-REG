import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image

#Fabiana

#SSA
def relatorio_ssa1():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Ana","Francisca","Vinicius"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")
        

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


def relatorio_ssa2():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Vitor","Mailan"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
       st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


def relatorio_bela():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Vanessa","Danilo"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
       st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)

def relatorio_paralela():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Crislaine","Neide"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


def relatorio_parque():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Denise_Paque","Adrielle"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)



#FELipe

#Iguatemi
def relatorio_iguatemi1():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Denise","Max"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
       st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)



def relatorio_iguatemi2():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Andressa","Diego"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


def relatorio_nort():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Jairo","Wander"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)

#Johm
def relatorio_barra():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Igor","Carol","Alana"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


def relatorio_piedade():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["DiegoL","Marcus"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
       st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


def relatorio_lapa():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Sara","Rafel"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


#Chrys

def relatorio_boulevard():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Camyla","Bruno","Gilvania"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)


#Intinerantes

def relatorio_intinerantes():

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "admin":
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

    consultores = ["Lazaro","Lee","MarcusI"]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Porcentual de conclusão")

    # --- Função para carregar dados de cada consultor ---
    def carregar_pedidos(consultor):
        try:
            aba = planilha.worksheet(consultor)
            dados = aba.get_all_records()
            df = pd.DataFrame(dados)
            if "Situação da tarefa" in df.columns:
                df["Situação da tarefa"] = df["Situação da tarefa"].apply(
                    lambda x: str(x).strip().lower() == "concluído"
                )
            return df
        except gspread.WorksheetNotFound:
            return pd.DataFrame()

    # --- Criar resumo por consultor ---
    resumo = []

    for consultor in consultores:
        df = carregar_pedidos(consultor)
        if df.empty:
            resumo.append({
                "Consultor": consultor,
                "Concluídas": 0,
                "Pendentes": 0,
                "Percentual Concluído": "0%"
            })
            continue

        concluidas = df["Situação da tarefa"].sum()
        pendentes = len(df) - concluidas
        percentual = round((concluidas / len(df)) * 100, 1) if len(df) > 0 else 0

        resumo.append({
            "Consultor": consultor,
            "Concluídas": concluidas,
            "Pendentes": pendentes,
            "Percentual Concluído": f"{percentual}%"
        })

    # --- Mostrar resumo no Streamlit ---
    resumo_df = pd.DataFrame(resumo)
    st.dataframe(resumo_df)