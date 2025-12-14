import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import datetime as dt
from PIL import Image
from datetime import datetime

icon = Image.open("image/vivo.png") 



def tarefas_carteira_felipe():
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



    st.set_page_config(page_title="R.E.G", page_icon=icon,layout="wide")

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
        data_selecionada = st.date_input(
            "Selecione o período:",
            value=(datetime.today(), datetime.today())
        )
    # ---------------------------
    # CONFIGURAÇÃO GOOGLE SHEETS
    # ---------------------------
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

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return
    # Converter data da planilha
    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio) &
        (planilha_Dados["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    
    contagemT = planilha_filtrada["Situação da tarefa"].count()
    contagemC = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Concluído",case=False,na=False).sum()
    contagemP = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Pendente",case=False,na=False).sum()

    col11,col12,col13 = st.columns(3)
    with col11:
        st.text(f"📝 Total de Tarefas : {contagemT}")

    with col12:
        st.text(f" 🟢 Tarefas Concluídas : {contagemC}")

    with col13:
        st.text(f" 🟡 Tarefas Pendentes: {contagemP}")
    # Padronizar colunas para evitar erro
    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    # ---------------------------
    # 🔥 NOTIFICAÇÕES
    # --------------------------

    st.dataframe(planilha_filtrada)
    
    if st.button("Atualizar"):
        st.rerun()




def tarefas_carteira_fabiana():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA"
            ]
        
    lojas_por_carteira = {
        " ": [" "],
         "GLS DA CARTEIRA DE FABIANA": [
            "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA PARALELA","LOJA PARQUE SHOP"
        ],

        }

    nomes_por_loja = {
        " ": [" "],
      
        "LOJA SSA |": ["Ana","Francisca","Vinicius"],
        "LOJA SSA ||": ["Vitor","Mailan"],
        "LOJA BELA VISTA": ["Vanessa","Danilo"],
        "LOJA PARALELA": ["Crislaine","Neide"],
        "LOJA PARQUE SHOP": ["Denise_Parque","Adrielle"],
        }


    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Fabiana":
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
         data_selecionada = st.date_input(
            "Selecione o período:",
            value=(datetime.today(), datetime.today())
        )

    # ---------------------------
    # CONFIGURAÇÃO GOOGLE SHEETS
    # ---------------------------
    gcp_info = st.secrets["fabi"]
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




    # Padronizar colunas para evitar erro
    planilha_Dados.columns = planilha_Dados.columns.str.strip()
    
    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date
    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return
    # Converter data da planilha
    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio) &
        (planilha_Dados["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    contagemT = planilha_filtrada["Situação da tarefa"].count()
    contagemC = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Concluído",case=False,na=False).sum()
    contagemP = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Pendente",case=False,na=False).sum()

    col11,col12,col13 = st.columns(3)
    with col11:
        st.text(f"📝 Total de Tarefas : {contagemT}")

    with col12:
        st.text(f" 🟢 Tarefas Concluídas : {contagemC}")

    with col13:
        st.text(f" 🟡 Tarefas Pendentes: {contagemP}")
    

    st.dataframe(planilha_filtrada)
    
    if st.button("Atualizar"):
        st.rerun()




def tarefas_carteira_john():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "GLS DA CARTEIRA DE JOHN"
            ]
        
    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
        ],

        }

    nomes_por_loja = {
        " ": [" "],
        "LOJA BARRA": ["Igor","Carol","Alana"],
        "LOJA PIEDADE": ["DiegoL","Marcusl"],
        "LOJA LAPA": ["Sara","Rafael"],
        }



    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "John":
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
        data_selecionada = st.date_input(
            "Selecione o período:",
            value=(datetime.today(), datetime.today())
        )
    # ---------------------------
    # CONFIGURAÇÃO GOOGLE SHEETS
    # ---------------------------
    gcp_info = st.secrets["joh"]
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

    contagemT = planilha_filtrada["Situação da tarefa"].count()
    contagemC = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Concluído",case=False,na=False).sum()
    contagemP = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Pendente",case=False,na=False).sum()

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

    planilha_Dados.columns = planilha_Dados.columns.str.strip()

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return
    # Padronizar colunas para evitar erro
    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio) &
        (planilha_Dados["Data"] <= data_fim)
    ]

    # Filtrar pela data escolhida
    planilha_filtrada = planilha_Dados[planilha_Dados["Data"] == data_selecionada]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # 🔥 NOTIFICAÇÕES
    # ---------------------------
    

    st.dataframe(planilha_filtrada)
    
    if st.button("Atualizar"):
        st.rerun()



def tarefas_carteira_chrys():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS",
            ]
        
    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE CHRYS": [
            "LOJA BOULEVARD"
        ],
        }

    nomes_por_loja = {
        " ": [" "],
        "LOJA BOULEVARD": ["Camyla","Bruno","Gilvania"],
        }



    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Chrys":
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
        data_selecionada = st.date_input(
            "Selecione o período:",
            value=(datetime.today(), datetime.today())
        )

    # ---------------------------
    # CONFIGURAÇÃO GOOGLE SHEETS
    # ---------------------------
    gcp_info = st.secrets["chr"]
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

    contagemT = planilha_filtrada["Situação da tarefa"].count()
    contagemC = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Concluído",case=False,na=False).sum()
    contagemP = planilha_filtrada["Situação da tarefa"].astype(str).str.contains("Pendente",case=False,na=False).sum()

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

    planilha_Dados["Data"] = pd.to_datetime(
        planilha_Dados["Data"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return
    # Converter data da planilha
    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados[
        (planilha_Dados["Data"] >= data_inicio) &
        (planilha_Dados["Data"] <= data_fim)
    ]
    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    # ---------------------------
    # 🔥 NOTIFICAÇÕES
    # ---------------------------
    

    st.dataframe(planilha_filtrada)
    
    if st.button("Atualizar"):
        st.rerun()































































































