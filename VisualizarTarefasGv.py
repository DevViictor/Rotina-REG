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

    gvs = ["GLS DA CARTEIRA DE FABIANA",
           "GLS DA CARTEIRA DE FELIPE",
            "GLS DA CARTEIRA DE JOHN",
            "GLS DA CARTEIRA DE CHRYS"
            ]
    lojas_por_carteira = {
            "": [""],
            "GLS DA CARTEIRA DE FABIANA": [
                "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA DIAS DAVILA","LOJA PARALELA","LOJA PARQUE SHOP"
            ],
            "GLS DA CARTEIRA DE FELIPE": [
                "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
            ],
            "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
            ],
            "GLS DA CARTEIRA DE CHRYS": [
            "LOJA BOULEVARD"
            ],
          
        }
    nomes_por_loja = {
            "": [""],
            "LOJA SSA |": ["Ana"],
            "LOJA SSA ||": ["Vitor"],
            "LOJA BELA VISTA": ["Danilo"],
            "LOJA DIAS DAVILA": ["Maise"],
            "LOJA PARALELA": ["Crislaine"],
            "LOJA PARQUE SHOP": ["Denise_Parque"],
            "LOJA IGUATEMI | BA": ["Max"],
            "LOJA IGUATEMI || BA": ["Andressa"],
            "LOJA NORT SHOP": ["Jairo"],
            "LOJA BARRA": ["Carol"],
            "LOJA PIEDADE": ["Diego"],
            "LOJA LAPA": ["Rafael"],
            "LOJA BOULEVARD": ["Bruno"],
        }

    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

   

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
    aba = planilha.worksheet("GLS(ABERTURA)")
    planilha_Dados = pd.DataFrame(aba.get_all_records())


    st.dataframe(planilha_Dados, use_container_width=True)

    st.divider()

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
  
    aba2 = planilha.worksheet("EXECUCOES(ABERTURA)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
      
    if nome:
        planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]


    if planilha_Dados2.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return
    
    contagemT = planilha_Dados2["Titulo"].count()


    planilha_Dados2["Data"] = pd.to_datetime(
        planilha_Dados2["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return

    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados2[
        (planilha_Dados2["Data"] >= data_inicio)
        & (planilha_Dados2["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_Dados2)
    st.write(f"Total de tarefas realizadas: {contagemT}")
    st.divider()
   

    #MAX
    
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

    gvs = ["GLS DA CARTEIRA DE FABIANA",
            "GLS DA CARTEIRA DE JOHN",
            "GLS DA CARTEIRA DE CHRYS"
            ]
    lojas_por_carteira = {
            "": [""],
            "GLS DA CARTEIRA DE FABIANA": [
                "LOJA SSA |","LOJA DIAS DAVILA"
            ],
            "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA",
            ],
            "GLS DA CARTEIRA DE CHRYS": [
            "LOJA BOULEVARD"
            ],
          
        }
    nomes_por_loja = {
            "": [""],
            "LOJA SSA |": ["Francisca"],
            "LOJA DIAS DAVILA": ["Maise"],
            "LOJA BARRA": ["Alana"],
            "LOJA BOULEVARD": ["Camyla"],
        }
    
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

   

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
    aba = planilha.worksheet("GLS(INTERMEDIO)")
    planilha_Dados = pd.DataFrame(aba.get_all_records())


    st.dataframe(planilha_Dados, use_container_width=True)

    st.divider()

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
  
    aba2 = planilha.worksheet("EXECUCOES(INTERMEDIO)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
      
    if nome:
        planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]
    
    contagemT = planilha_Dados2["Titulo"].count()


    if planilha_Dados2.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return


    planilha_Dados2["Data"] = pd.to_datetime(
        planilha_Dados2["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return

    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados2[
        (planilha_Dados2["Data"] >= data_inicio)
        & (planilha_Dados2["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_Dados2)
    st.write(f"Total de tarefas realizadas: {contagemT}")
    st.divider()

    st.divider()
   
    
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

    
    gvs = ["GLS DA CARTEIRA DE FABIANA",
           "GLS DA CARTEIRA DE FELIPE",
            "GLS DA CARTEIRA DE JOHN",
            "GLS DA CARTEIRA DE CHRYS"
            ]
    
    lojas_por_carteira = {
            "": [""],
            "GLS DA CARTEIRA DE FABIANA": [
                "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA DIAS DAVILA","LOJA PARALELA","LOJA PARQUE SHOP"
            ],
            "GLS DA CARTEIRA DE FELIPE": [
                "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
            ],
            "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
            ],
            "GLS DA CARTEIRA DE CHRYS": [
            "LOJA BOULEVARD"
            ],
          
        }
    nomes_por_loja = {
            "": [""],
            "LOJA SSA |": ["Vinicius"],
            "LOJA SSA ||": ["Mailan"],
            "LOJA BELA VISTA": ["Vanessa"],
            "LOJA DIAS DAVILA": ["Maise"],
            "LOJA PARALELA": ["Neide"],
            "LOJA PARQUE SHOP": ["Denise_Parque"],
            "LOJA IGUATEMI | BA": ["Denise"],
            "LOJA IGUATEMI || BA": ["Diego"],
            "LOJA NORT SHOP": ["Wanderlei"],
            "LOJA BARRA": ["Igor"],
            "LOJA PIEDADE": ["Marcusl"],
            "LOJA LAPA": ["Sara"],
            "LOJA BOULEVARD": ["Gilvania"],
        }
    
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

   

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
    aba = planilha.worksheet("GLS(INTERMEDIO)")
    planilha_Dados = pd.DataFrame(aba.get_all_records())


    st.dataframe(planilha_Dados, use_container_width=True)

    st.divider()

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
  
    aba2 = planilha.worksheet("EXECUCOES(FECHAMENTO)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
      
    if nome:
        planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]

    contagemT = planilha_Dados2["Titulo"].count()

    if planilha_Dados2.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return


    planilha_Dados2["Data"] = pd.to_datetime(
        planilha_Dados2["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return

    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados2[
        (planilha_Dados2["Data"] >= data_inicio)
        & (planilha_Dados2["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_Dados2)
    st.write(f"Total de tarefas realizadas: {contagemT}")
    st.divider()
    

    st.divider()
   

    #MAX
    
    if st.button("Atualizar"):
        st.rerun()
   




def visualizar_tarefas_itinerantes():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G - ITINERANTES", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    gvs = ["ITINERANTES"]
    lojas_por_carteira = {"ITINERANTES": ["ITINERANTES"]}
    nomes_por_loja = {"ITINERANTES": ["Lee","Marcus","Lázaro"]}

    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")

   

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
    aba = planilha.worksheet("ITINERANTES")
    planilha_Dados = pd.DataFrame(aba.get_all_records())


    st.dataframe(planilha_Dados, use_container_width=True)

    st.divider()

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
  
    aba2 = planilha.worksheet("REGISTROS(ITINERANTES)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
      
    if nome:
        planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]

    contagemT = planilha_Dados2["Titulo"].count()

    if planilha_Dados2.empty:
        st.warning("Nenhuma tarefa encontrada.")
        return


    planilha_Dados2["Data"] = pd.to_datetime(
        planilha_Dados2["Data"], dayfirst=True, errors="coerce"
    ).dt.date

    if not isinstance(data_selecionada, tuple) or len(data_selecionada) != 2:
        st.warning("⚠️ Selecione um período com data inicial e final.")
        return

    data_inicio, data_fim = data_selecionada

    planilha_filtrada = planilha_Dados2[
        (planilha_Dados2["Data"] >= data_inicio)
        & (planilha_Dados2["Data"] <= data_fim)
    ]

    if planilha_filtrada.empty:
        st.info("Nenhuma tarefa encontrada para esta data.")
        return

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_Dados2)
    st.write(f"Total de tarefas realizadas: {contagemT}")
    st.divider()
    

    st.divider()
   

    #MAX
    
    if st.button("Atualizar"):
        st.rerun()
   