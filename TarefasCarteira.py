import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import datetime as dt
from PIL import Image
from datetime import datetime

icon = Image.open("image/vivo.png") 

gcp_info = st.secrets["gcp"]
planilha_chave_execucoes = st.secrets["planilha_execucoes"]["chave2"]

creds = Credentials.from_service_account_info(
    dict(gcp_info),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

cliente = gspread.authorize(creds)
planilha_exc = cliente.open_by_key(planilha_chave_execucoes)


def tarefas_carteira_felipe():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "EXECUCOES(ABERTURA)",
            "EXECUCOES(FECHAMENTO)",

            ]
        
    lojas_por_carteira = {
        " ": [" "],
        "EXECUCOES(ABERTURA)": [
                "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
        ],
        "EXECUCOES(FECHAMENTO)": [
                "LOJA IGUATEMI | (FECHAMENTO) BA","LOJA IGUATEMI || (FECHAMENTO) BA","LOJA NORT SHOP (FECHAMENTO)"
        ]
        }

    nomes_por_loja = {
        " ": [" "],
      
        "LOJA IGUATEMI | BA": ["Max"],
        "LOJA IGUATEMI || BA": ["Andressa"],
        "LOJA NORT SHOP": ["Jairo"],

        "LOJA IGUATEMI | (FECHAMENTO) BA": ["Denise"],
        "LOJA IGUATEMI || (FECHAMENTO) BA": ["Diego"],
        "LOJA NORT SHOP (FECHAMENTO)": ["Wanderlei"],
        }



    st.set_page_config(page_title="R.E.G", page_icon=icon,layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Felipe":
                st.error("⚠️ Acesso negado!")
                st.stop()

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

    aba2 = planilha_exc.worksheet(carteira)
    
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
    if nome:
            planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]


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

    contagemT = planilha_filtrada["Titulo"].count()

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_filtrada)
    st.write(f"Total de tarefas realizadas: {contagemT}")

    st.divider()
    if st.button("Atualizar"):
            st.rerun()



def tarefas_carteira_fabiana():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "EXECUCOES(ABERTURA)",
            "EXECUCOES(INTERMEDIO)",
            "EXECUCOES(FECHAMENTO)",

            ]
        
    lojas_por_carteira = {
        " ": [" "],
         "EXECUCOES(ABERTURA)": [
            "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA PARALELA","LOJA PARQUE SHOP"
        ],
         "EXECUCOES(INTERMEDIO)": [
            "LOJA SSA | (INTERMEDIO)"
        ],
         "EXECUCOES(FECHAMENTO)": [
            "LOJA SSA | (FECHAMENTO)","LOJA SSA || (FECHAMENTO)","LOJA BELA VISTA (FECHAMENTO)","LOJA PARALELA (FECHAMENTO)","LOJA PARQUE SHOP (FECHAMENTO)"
        ],

        
        

        }
  

    nomes_por_loja = {
        " ": [" "],
      
        "LOJA SSA |": ["Mércia"],
        "LOJA SSA ||": ["Vitor"],
        "LOJA BELA VISTA": ["Danilo"],
        "LOJA PARALELA": ["Crislaine"],
        "LOJA PARQUE SHOP": ["Denise_Parque"],

        "LOJA SSA | (INTERMEDIO)": ["Francisca"],

        "LOJA SSA | (FECHAMENTO)": ["Vinicius"],
        "LOJA SSA || (FECHAMENTO)": ["Mailan"],
        "LOJA BELA VISTA (FECHAMENTO)": ["Vanessa"],
        "LOJA PARALELA (FECHAMENTO)": ["Neide"],
        "LOJA PARQUE SHOP (FECHAMENTO)": ["Adrielle"],
       
        }

    

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Fabiana":
        st.error("⚠️ Acesso negado!")
        st.stop()
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

    aba2 = planilha_exc.worksheet(carteira)
    
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
    if nome:
            planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]


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

    contagemT = planilha_filtrada["Titulo"].count()

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_filtrada)
    st.write(f"Total de tarefas realizadas: {contagemT}")

    st.divider()
    if st.button("Atualizar"):
            st.rerun()



def tarefas_carteira_john():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "EXECUCOES(ABERTURA)",
            "EXECUCOES(INTERMEDIO)",
            "EXECUCOES(FECHAMENTO)",
            ]
        
    lojas_por_carteira = {
        " ": [" "],
        "EXECUCOES(ABERTURA)": [
            "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
        ],
        "EXECUCOES(INTERMEDIO)": [
            "LOJA BARRA (INTERMEDIO)"
        ],
        "EXECUCOES(FECHAMENTO)": [
            "LOJA BARRA (FECHAMENTO)","LOJA PIEDADE (FECHAMENTO)","LOJA LAPA (FECHAMENTO)"
        ],

        }

    nomes_por_loja = {
        " ": [" "],
        "LOJA BARRA": ["Carol"],
        "LOJA PIEDADE": ["Marcus"],
        "LOJA LAPA": ["Rafael"],

        "LOJA BARRA (INTERMEDIO)": ["Alana"],

        "LOJA BARRA (FECHAMENTO)": ["Carol"],
        "LOJA PIEDADE (FECHAMENTO)": ["DiegoP"],
        "LOJA LAPA (FECHAMENTO)": ["Igor"],

       
        }



    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "John":
        st.error("⚠️ Acesso negado!")
        st.stop()
    
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

    aba2 = planilha_exc.worksheet(carteira)
    
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
    if nome:
            planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]


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

    contagemT = planilha_filtrada["Titulo"].count()

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_filtrada)
    st.write(f"Total de tarefas realizadas: {contagemT}")

    st.divider()
    if st.button("Atualizar"):
            st.rerun()



def tarefas_carteira_chrys():
    icon = Image.open("image/vivo.png")

    gvs = [ 
            "EXECUCOES(ABERTURA)",
            "EXECUCOES(INTERMEDIO)",
            "EXECUCOES(FECHAMENTO)",
            ]
        
    lojas_por_carteira = {
        " ": [" "],
        "EXECUCOES(ABERTURA)": [
            "LOJA BOULEVARD (ABERTURA)"
        ],
        "EXECUCOES(INTERMEDIO)": [
            "LOJA BOULEVARD (INTERMEDIO)"
        ],
        "EXECUCOES(FECHAMENTO)": [
            "LOJA BOULEVARD (FECHAMENTO)"
        ],
        }

    nomes_por_loja = {
        " ": [" "],
        "LOJA BOULEVARD (ABERTURA)": ["Bruno"],

        "LOJA BOULEVARD (INTERMEDIO)": ["Camyla"],

        "LOJA BOULEVARD (FECHAMENTO)": ["Gilvania"],


        }



    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role != "Chrys":
        st.error("⚠️ Acesso negado!")
        st.stop()
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

    aba2 = planilha_exc.worksheet(carteira)
    
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())
    if nome:
            planilha_Dados2 = planilha_Dados2[planilha_Dados2["GL"].str.contains(nome,case =False)]


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

    contagemT = planilha_filtrada["Titulo"].count()

    st.subheader("📌 COMPARATIVO DE TAREFAS")
    st.dataframe(planilha_filtrada)
    st.write(f"Total de tarefas realizadas: {contagemT}")

    st.divider()
    if st.button("Atualizar"):
            st.rerun()































































































