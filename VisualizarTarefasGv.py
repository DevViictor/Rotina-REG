import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image
from datetime import datetime


# =========================================================
# ===================== GLS ABERTURA ======================
# =========================================================
def visualizar_tarefas_gvs():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    gvs = ["TODOS OS GLS(ABERTURA)"]
    lojas_por_carteira = {"TODOS OS GLS(ABERTURA)": ["GLS(ABERTURA)"]}
    nomes_por_loja = {"GLS(ABERTURA)": ["GLS(ABERTURA)"]}

    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_por_carteira.get(carteira, []))
    with col3:
        nome = st.selectbox("Nome:", nomes_por_loja.get(loja, []))
    with col4:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )

    gcp_info = st.secrets["tafgl"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_key(planilha_chave)
    aba = planilha.worksheet(nome)
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return

    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio)
        & (planilha_Dados["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    colunas_principais = [
        "ID",
        "Criada",
        "Título",
        "Descrição da tarefa",
        "Data",
        "Hora inicial",
        "Hora final",
    ]

    planilha_principal = planilha_filtrada[
        [c for c in colunas_principais if c in planilha_filtrada.columns]
    ]

    st.dataframe(planilha_principal, use_container_width=True)

    colunas_extras = ["Max","Ana","Andressa","Vitor",	"Rafael",	"Carol",	"Danilo",	"Jairo",	"Maise",	"Camyla",	"Denise_Parque"	,"Crislaine"	,"DiegoP"	,"Bruno"]
    colunas_extras = [c for c in colunas_extras if c in planilha_filtrada.columns]

    if colunas_extras:
        st.divider()
        st.subheader("📌 GLS ABERTURA")
        st.dataframe(
            planilha_filtrada[["ID"] + colunas_extras],
            use_container_width=True,
        )

    if st.button("Atualizar"):
        st.rerun()


# =========================================================
# ==================== GLS INTERMEDIO =====================
# =========================================================
def visualizar_tarefas_intermedio():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G - GVS", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    gvs = ["TODOS OS GLS(INTERMEDIO)"]
    lojas_por_carteira = {"TODOS OS GLS(INTERMEDIO)": ["GLS(INTERMEDIO)"]}
    nomes_por_loja = {"GLS(INTERMEDIO)": ["GLS(INTERMEDIO)"]}

    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_por_carteira.get(carteira, []))
    with col3:
        nome = st.selectbox("Nome:", nomes_por_loja.get(loja, []))
    with col4:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )

    gcp_info = st.secrets["tafgl"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_key(planilha_chave)
    aba = planilha.worksheet(nome)
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return

    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio)
        & (planilha_Dados["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    colunas_principais = [
        "ID",
        "Criada",
        "Título",
        "Descrição da tarefa",
        "Data",
        "Hora inicial",
        "Hora final",
    ]

    planilha_principal = planilha_filtrada[
        [c for c in colunas_principais if c in planilha_filtrada.columns]
    ]

    st.dataframe(planilha_principal, use_container_width=True)

    colunas_extras = ["Maise", "Francisca", "Alana"]
    colunas_extras = [c for c in colunas_extras if c in planilha_filtrada.columns]

    if colunas_extras:
        st.divider()
        st.subheader("📌 GLS INTERMEDIO")
        st.dataframe(
            planilha_filtrada[["ID"] + colunas_extras],
            use_container_width=True,
        )

    if st.button("Atualizar"):
        st.rerun()


# =========================================================
# ==================== GLS FECHAMENTO =====================
# =========================================================
def visualizar_tarefas_fechamento():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G - GVS", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    gvs = ["TODOS OS GLS(FECHAMENTO)"]
    lojas_por_carteira = {"TODOS OS GLS(FECHAMENTO)": ["GLS(FECHAMENTO)"]}
    nomes_por_loja = {"GLS(FECHAMENTO)": ["GLS(FECHAMENTO)"]}

    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_por_carteira.get(carteira, []))
    with col3:
        nome = st.selectbox("Nome:", nomes_por_loja.get(loja, []))
    with col4:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )

    gcp_info = st.secrets["tafgl"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_key(planilha_chave)
    aba = planilha.worksheet(nome)
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    if planilha_Dados.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return

    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return


    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio)
        & (planilha_Dados["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    colunas_principais = [
        "ID",
        "Criada",
        "Título",
        "Descrição da tarefa",
        "Data",
        "Hora inicial",
        "Hora final",
    ]

    planilha_principal = planilha_filtrada[
        [c for c in colunas_principais if c in planilha_filtrada.columns]
    ]

    st.dataframe(planilha_principal, use_container_width=True)

    colunas_extras = [
        "Mailan",
        "Vinicius",
        "Denise",
        "Diego",
        "Marcosl",
        "Sara",
        "Igor",
        "Vanessa",
        "Neide",
        "Wanderlei",
        "Adrielle",
        "Gilvania",
        "Maise",
    ]

    colunas_extras = [c for c in colunas_extras if c in planilha_filtrada.columns]

    if colunas_extras:
        st.divider()
        st.subheader("📌 GLS FECHAMENTO")
        st.dataframe(
            planilha_filtrada[["ID"] + colunas_extras],
            use_container_width=True,
        )

    if st.button("Atualizar"):
        st.rerun()
