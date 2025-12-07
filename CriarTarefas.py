import streamlit as st
import gspread 
from google.oauth2.service_account import Credentials
import requests
import pandas as pd
from PIL import Image 

def criar_page():

    if "role" not in st.session_state or st.session_state.role != "admin":
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- CONFIG ---
    gcp_info = st.secrets["gcp"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    st.set_page_config(page_title="R.E.G",
                    layout="wide",
                    page_icon="📝")



    # --- LISTAS ---
    nomes_por_loja = {
    # --- GV 1 - FABIANA SACRAMENTO ---
    "LOJA SSA |": ["Ana", "Francisca", "Vinicius"],
    "LOJA SSA ||": ["Vitor", "Mailan"],
    "LOJA BELA VISTA": ["Vanessa", "Danilo"],
    "LOJA PARALELA": ["Crislaine", "Neide"],
    "LOJA PARQUE SHOP": ["Denise", "Adrielle"],

    # --- GV 2 - FELIPE SILVA ---
    "LOJA IGUATEMI | BA": ["Max", "Denise"],
    "LOJA IGUATEMI || BA": ["Diego", "Andressa"],
    "LOJA NORT SHOP": ["Jairo", "Wanderlei"],

    # --- GV 1 - JOHM COITO ---
    "LOJA BARRA": ["Igor", "Carol", "Alana"],
    "LOJA PIEDADE": ["Diego", "Marcus"],
    "LOJA LAPA": ["Sara", "Rafael"],

    # --- GV 2 - CHRYS REBOUÇAS ---
    "LOJA BOULEVARD": ["Camyla", "Bruno", "Gilvania"],

    # --- ITINERANTES ---
    "ITINERANTES": ["Lázaro", "Lee", "Marcus"],
}


    lojas = [" ","LOJA IGUATEMI | BA" , "LOJA IGUATEMI || BA" , "LOJA SSA |" , "LOJA SSA ||" , "LOJA BELA VISTA" , "LOJA PARALELA", "LOJA PARQUE SHOP","LOJA NORT SHOP" , "LOJA BARRA" , "LOJA PIEDADE" , "LOJA LAPA","LOJA BOULEVARD" ]
    
    tipos_recorrencia = ["","Não recorrente", "Diária", "Semanal", "Mensal"]

    # --- FUNÇÃO NOTIFICAÇÃO ---
    def notificacao(loja):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]

        messagem = f"Novas tarefas foram criadas. \n Loja {loja}. \nVisualize o painel de tarefas."

        requests.post("https://api.pushover.net/1/messages.json", 
            data={
            "token": api_token,
            "user": user_key,
            "message": messagem
            
        })

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefas")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)

    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

    image_logo = Image.open("image/Image (2).png")

    cola,colb,colc = st.columns([4,1,1])

    with colc :
        st.image(image_logo)

    with cola:
        st.header("R.E.G")
        st.subheader("Rotina de Excelência Gerencial")

    st.divider()

    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)

    st.divider()

    loja = st.selectbox("Loja :", lojas)

    with st.form("Forms"):

        # --- Aplicar modelo ---
        if modelo_escolhido and modelo_escolhido in df_modelos["Título"].values:
            modelo = df_modelos[df_modelos["Título"] == modelo_escolhido].iloc[0]
            titulo_default = modelo["Título"]
            descricao_default = modelo["Descrição da tarefa"]
            hora_ini_default = modelo["Hora inicial"]
            hora_fim_default = modelo["Hora final"]
            recorrencia_default = modelo["Tipo de recorrência"]
        else:
            titulo_default = ""
            descricao_default = ""
            hora_ini_default = "00:00"
            hora_fim_default = "00:00"
            recorrencia_default = ""

        # --- CAMPOS ---
        
        lista_nomes = [""] + nomes_por_loja.get(loja, [])

        nome = st.selectbox("Nome do GL :", lista_nomes)

        titulo = st.text_input("Título da tarefa :", value=titulo_default)
        descricao = st.text_input("Descrição da tarefa :", value=descricao_default)

        col1, col2 = st.columns(2)
        with col1:
            hora_inicial = st.time_input(
                "Hora inicial :",
                value=pd.to_datetime(hora_ini_default).time()
            )
        with col2:
            hora_final = st.time_input(
                "Hora final :",
                value=pd.to_datetime(hora_fim_default).time()
            )

        col3, col4 = st.columns(2)
        with col3:
            data = st.date_input("Data da tarefa :")
        with col4:
            recorrencia = st.selectbox(
                "Tipo de recorrência :",
                tipos_recorrencia,
                index=tipos_recorrencia.index(recorrencia_default) if recorrencia_default in tipos_recorrencia else 0
            )

        # --- BOTÕES ---
        col1_btn, col2_btn = st.columns(2)
        enviar = col1_btn.form_submit_button("Enviar tarefa")
        salvar_tarefas = col2_btn.form_submit_button("Salvar como modelo")


    # ENVIAR TAREFA
    if enviar:

        if not nome:
            st.error("Selecione um *Nome do GL* para enviar a tarefa.")
            st.stop()

        pagina = client.open_by_key(planilha_chave).worksheet(nome)
        novo_id = len(pagina.get_all_records()) + 1

        notificacao(loja)

        pagina.append_row([
            novo_id,
            loja,
            nome,
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
            "Pendente",
        ])

        st.success("Tarefa enviada com sucesso!")

    # SALVAR MODELO
    if salvar_tarefas:

        aba_modelos.append_row([
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
        ])

        st.success("Modelo salvo com sucesso!")
