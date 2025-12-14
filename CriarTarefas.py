import streamlit as st
import gspread 
from google.oauth2.service_account import Credentials
import requests
import pandas as pd
from PIL import Image 

def criar_page():

    if "role" not in st.session_state or st.session_state.role not in ["Victor","Felipe","John","Fabiana","Chrys"]:
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

    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G",
                       layout="wide",
                       page_icon=icon)

    # --- LISTAS ---
    gvs = ["",
        "TODOS OS GVS",
        "TODOS OS GLS",
        "TODOS OS GLS(ABERTURA)",
        "TODOS OS GLS(INTERMEDIO)",
        "TODOS OS GLS(FECHAMENTO)",
        "GLS DA CARTEIRA DE FABIANA",
        "GLS DA CARTEIRA DE FELIPE",
        "GLS DA CARTEIRA DE CHRYS",
        "GLS DA CARTEIRA DE JOHN",
        "TODOS OS ITINERANTES"
    ]
        
    lojas_por_carteira = {
        "": [""],
        "TODOS OS GVS": ["GVS"],

        "TODOS OS GLS": ["TODOS OS GLS"],

        "TODOS OS GLS(INTERMEDIO)": ["GLS(INTERMEDIO)"],

        "TODOS OS GLS(ABERTURA)": ["GLS(ABERTURA)"],

        "TODOS OS GLS(FECHAMENTO)": ["GLS(FECHAMENTO)"],

        "GLS DA CARTEIRA DE FABIANA": [
            "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA PARALELA","LOJA PARQUE SHOP"
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
        "TODOS OS ITINERANTES": ["ITINERANTES"]
    }

    nomes_por_loja = {
        "": [""],
        "GVS": ["Todos","Fabiana","Felipe","John","Chrys"],
        "TODOS OS GLS": ["GLS(GERAL)"],
        "GLS(ABERTURA)":["GLS(ABERTURA)"],
        "GLS(INTERMEDIO)":["GLS(INTERMEDIO)"],
        "GLS(FECHAMENTO)":["GLS(FECHAMENTO)"],
        "TODOS OS ITINERANTES": ["ITINERANTES"],
        "LOJA SSA |": ["Ana","Francisca","Vinicius"],
        "LOJA SSA ||": ["Vitor","Mailan"],
        "LOJA BELA VISTA": ["Vanessa","Danilo"],
        "LOJA PARALELA": ["Crislaine","Neide"],
        "LOJA PARQUE SHOP": ["Denise_Parque","Adrielle"],
        "LOJA IGUATEMI | BA": ["Max","Denise"],
        "LOJA IGUATEMI || BA": ["Diego","Andressa"],
        "LOJA NORT SHOP": ["Jairo","Wanderlei"],
        "LOJA BARRA": ["Igor","Carol","Alana"],
        "LOJA PIEDADE": ["DiegoL","Marcusl"],
        "LOJA LAPA": ["Sara","Rafael"],
        "LOJA BOULEVARD": ["Camyla","Bruno","Gilvania"],
        "ITINERANTES": ["Lázaro","Lee","Marcus"],
    }

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    # --- FUNÇÃO NOTIFICAÇÃO ---



    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefas")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)
    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

    # --- HEADER / LOGO ---
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Rotina de Excelência Gerencial")

    st.divider()
    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)
    st.divider()

    # ===================================================
    # SELEÇÃO DINÂMICA - CORRIGIDA
    # ===================================================
    cola,colb = st.columns(2)
    # 1) Escolhe carteira
    with cola:
        envio = st.selectbox("Carteira :", gvs)

    # 2) Filtra lojas da carteira
    lojas = [""] + lojas_por_carteira.get(envio, [])

    # 3) Escolhe loja
    with colb:
        loja_selecionada = st.selectbox("Loja :", lojas)

    # 4) Filtra nomes daquela loja
    lista_nomes = [""] + nomes_por_loja.get(loja_selecionada, [])

    # ===================================================
    # FORMULÁRIO
    # ===================================================

    with st.form("Forms"):

        # ----- Aplicar modelo -----
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

        # ----- CAMPOS -----
        titulo = st.text_input("Título da tarefa :", value=titulo_default)
        descricao = st.text_input("Descrição da tarefa :", value=descricao_default)

        col1, col2 = st.columns(2)
        with col1:
            hora_inicial = st.time_input("Hora inicial :", value=pd.to_datetime(hora_ini_default).time())
        with col2:
            hora_final = st.time_input("Hora final :", value=pd.to_datetime(hora_fim_default).time())

        col3, col4 = st.columns(2)
        with col3:
            data = st.date_input("Data da tarefa :")
        with col4:
            recorrencia = st.selectbox(
                "Tipo de recorrência :",
                tipos_recorrencia,
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        criada = st.selectbox("Criador da tarefa: ", ["Victor"])

        colN1, colN2 = st.columns(2)
        with colN1:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with colN2:
            loja_final = st.text_input("Loja selecionada:", loja_selecionada, disabled=True)

        colbtn1, colbtn2 = st.columns(2)
        enviar = colbtn1.form_submit_button("Enviar tarefa")
        salvar_tarefas = colbtn2.form_submit_button("Salvar como modelo")

    # ===================================================
    # ENVIAR TAREFA
    # ===================================================

    if enviar:

        if not nome:
            st.error("Selecione um *Nome do GL* para enviar a tarefa.")
            st.stop()

        pagina = client.open_by_key(planilha_chave).worksheet(nome)
        novo_id = len(pagina.get_all_records()) + 1


        pagina.append_row([
            novo_id,
            criada,
            loja_final,
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

    # ===================================================
    # SALVAR MODELO
    # ===================================================

    if salvar_tarefas:
        novo_id = len(aba_modelos.get_all_records()) + 1
        aba_modelos.append_row([
            novo_id,
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
        ])

        st.success("Modelo salvo com sucesso!")



def criar_page_fabiana():

    if "role" not in st.session_state or st.session_state.role not in ["Victor","Felipe","John","Fabiana","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- CONFIG ---
    gcp_info = st.secrets["fabi"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G",
                       layout="wide",
                       page_icon=icon)

    # --- LISTAS ---
    gvs = ["", 
        "GLS DA CARTEIRA DE FABIANA",
        "EU"
       
    ]
        
    lojas_por_carteira = {
        "": [""],
        "GLS DA CARTEIRA DE FABIANA": [
            "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA","LOJA PARALELA","LOJA PARQUE SHOP"
        ],
        "EU": [
            "Minhas Tarefas"
        ]
    }

    nomes_por_loja = {
        "": [""],
        "LOJA SSA |": ["Todos SSA |","Ana","Francisca","Vinicius"],
        "LOJA SSA ||": ["Todos SSA ||","Vitor","Mailan"],
        "LOJA BELA VISTA": ["Todos Bela","Vanessa","Danilo"],
        "LOJA PARALELA": ["Todos Paralela","Crislaine","Neide"],
        "LOJA PARQUE SHOP": ["Todos Parque","Denise_Parque","Neide"],
        "Minhas Tarefas": ["Fabiana"]
    }

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    # --- FUNÇÃO NOTIFICAÇÃO ---
   

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasFabiana")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)
    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

    # --- HEADER / LOGO ---
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Rotina de Excelência Gerencial")

    st.divider()
    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)
    st.divider()

    # ===================================================
    # SELEÇÃO DINÂMICA - CORRIGIDA
    # ===================================================

    # 1) Escolhe carteira
    envio = st.selectbox("Carteira :", gvs)

    # 2) Filtra lojas da carteira
    lojas = [""] + lojas_por_carteira.get(envio, [])

    # 3) Escolhe loja
    loja_selecionada = st.selectbox("Loja :", lojas)

    # 4) Filtra nomes daquela loja
    lista_nomes = [""] + nomes_por_loja.get(loja_selecionada, [])

    # ===================================================
    # FORMULÁRIO
    # ===================================================

    with st.form("Forms"):

        # ----- Aplicar modelo -----
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

        # ----- CAMPOS -----
        titulo = st.text_input("Título da tarefa :", value=titulo_default)
        descricao = st.text_input("Descrição da tarefa :", value=descricao_default)

        col1, col2 = st.columns(2)
        with col1:
            hora_inicial = st.time_input("Hora inicial :", value=pd.to_datetime(hora_ini_default).time())
        with col2:
            hora_final = st.time_input("Hora final :", value=pd.to_datetime(hora_fim_default).time())

        col3, col4 = st.columns(2)
        with col3:
            data = st.date_input("Data da tarefa :")
        with col4:
            recorrencia = st.selectbox(
                "Tipo de recorrência :",
                tipos_recorrencia,
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        criada = st.selectbox("Criador da tarefa: ", ["Fabiana"])

        colN1, colN2 = st.columns(2)
        with colN1:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with colN2:
            loja_final = st.text_input("Loja selecionada:", loja_selecionada, disabled=True)

        colbtn1, colbtn2 = st.columns(2)
        enviar = colbtn1.form_submit_button("Enviar tarefa")
        salvar_tarefas = colbtn2.form_submit_button("Salvar como modelo")

    # ===================================================
    # ENVIAR TAREFA
    # ===================================================

    if enviar:

        if not nome:
            st.error("Selecione um *Nome do GL* para enviar a tarefa.")
            st.stop()

        pagina = client.open_by_key(planilha_chave).worksheet(nome)
        novo_id = len(pagina.get_all_records()) + 1


        pagina.append_row([
            novo_id,
            criada,
            loja_final,
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

    # ===================================================
    # SALVAR MODELO
    # ===================================================

    if salvar_tarefas:
        novo_id = len(aba_modelos.get_all_records()) + 1
        aba_modelos.append_row([
            novo_id,
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
        ])

        st.success("Modelo salvo com sucesso!")


def criar_page_felipe():

    if "role" not in st.session_state or st.session_state.role not in ["Victor","Felipe","John","Fabiana","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- CONFIG ---
    gcp_info = st.secrets["fel"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G",
                       layout="wide",
                       page_icon=icon)

    # --- LISTAS ---
    gvs = ["",
        
        "GLS DA CARTEIRA DE FELIPE",
        "EU"
       
    ]
        
    lojas_por_carteira = {
        "": [""],

        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
        ],
        "EU": [
            "Minhas Tarefas"
        ]
    }

    nomes_por_loja = {
        "": [""],
        "LOJA IGUATEMI | BA": ["Todos Iguatemi |","Max","Denise"],
        "LOJA IGUATEMI || BA": ["Todos Iguatemi ||","Diego","Andressa"],
        "LOJA NORT SHOP": ["Todos Norte","Jairo","Wanderlei"],
        "Minhas Tarefas": ["Felipe"]
       
    }

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]



    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasFelipe")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)
    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

    # --- HEADER / LOGO ---
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Rotina de Excelência Gerencial")

    st.divider()
    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)
    st.divider()

    # ===================================================
    # SELEÇÃO DINÂMICA - CORRIGIDA
    # ===================================================
    cola,colb = st.columns(2)
    # 1) Escolhe carteira
    with cola:
        envio = st.selectbox("Carteira :", gvs)

    # 2) Filtra lojas da carteira
    lojas = [""] + lojas_por_carteira.get(envio, [])

    # 3) Escolhe loja
    with colb:
        loja_selecionada = st.selectbox("Loja :", lojas)

    # 4) Filtra nomes daquela loja
    lista_nomes = [""] + nomes_por_loja.get(loja_selecionada, [])

    # ===================================================
    # FORMULÁRIO
    # ===================================================

    with st.form("Forms"):

        # ----- Aplicar modelo -----
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

        # ----- CAMPOS -----
        titulo = st.text_input("Título da tarefa :", value=titulo_default)
        descricao = st.text_input("Descrição da tarefa :", value=descricao_default)

        col1, col2 = st.columns(2)
        with col1:
            hora_inicial = st.time_input("Hora inicial :", value=pd.to_datetime(hora_ini_default).time())
        with col2:
            hora_final = st.time_input("Hora final :", value=pd.to_datetime(hora_fim_default).time())

        col3, col4 = st.columns(2)
        with col3:
            data = st.date_input("Data da tarefa :")
        with col4:
            recorrencia = st.selectbox(
                "Tipo de recorrência :",
                tipos_recorrencia,
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        criada = st.selectbox("Criador da tarefa: ", ["Felipe"])

        colN1, colN2 = st.columns(2)
        with colN1:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with colN2:
            loja_final = st.text_input("Loja selecionada:", loja_selecionada, disabled=True)

        colbtn1, colbtn2 = st.columns(2)
        enviar = colbtn1.form_submit_button("Enviar tarefa")
        salvar_tarefas = colbtn2.form_submit_button("Salvar como modelo")

    # ===================================================
    # ENVIAR TAREFA
    # ===================================================

    if enviar:

        if not nome:
            st.error("Selecione um *Nome do GL* para enviar a tarefa.")
            st.stop()

        pagina = client.open_by_key(planilha_chave).worksheet(nome)
        novo_id = len(pagina.get_all_records()) + 1

        pagina.append_row([
            novo_id,
            criada,
            loja_final,
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

    # ===================================================
    # SALVAR MODELO
    # ===================================================

    if salvar_tarefas:
        novo_id = len(aba_modelos.get_all_records()) + 1
        aba_modelos.append_row([
            novo_id,
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
        ])

        st.success("Modelo salvo com sucesso!")



def criar_page_john():

    if "role" not in st.session_state or st.session_state.role not in ["Victor","Felipe","John","Fabiana","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- CONFIG ---
    gcp_info = st.secrets["joh"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G",
                       layout="wide",
                       page_icon=icon)

    # --- LISTAS ---
    gvs = ["",
    
        "GLS DA CARTEIRA DE JOHN",
        "EU"    
    ]
        
    lojas_por_carteira = {
        "": [""],
      
        "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
        ],
        "EU": [
            "Minhas Tarefas"
        ]
        
    }

    nomes_por_loja = {
        "": [""],
        
        "LOJA BARRA": ["Todos Barra","Igor","Carol","Alana"],
        "LOJA PIEDADE": ["Todos Piedade","DiegoL","Marcusl"],
        "LOJA LAPA": ["Todos Lapa","Sara","Rafel"],
        "Minhas Tarefas": ["John"]
       
    }

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    # --- FUNÇÃO NOTIFICAÇÃO ---
    

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasJohn")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)
    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

    # --- HEADER / LOGO ---
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Rotina de Excelência Gerencial")

    st.divider()
    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)
    st.divider()

    # ===================================================
    # SELEÇÃO DINÂMICA - CORRIGIDA
    # ===================================================
    cola,colb = st.columns(2)
    # 1) Escolhe carteira
    with cola:
        envio = st.selectbox("Carteira :", gvs)

    # 2) Filtra lojas da carteira
    lojas = [""] + lojas_por_carteira.get(envio, [])

    # 3) Escolhe loja
    with colb:
        loja_selecionada = st.selectbox("Loja :", lojas)

    # 4) Filtra nomes daquela loja
    lista_nomes = [""] + nomes_por_loja.get(loja_selecionada, [])

    # ===================================================
    # FORMULÁRIO
    # ===================================================

    with st.form("Forms"):

        # ----- Aplicar modelo -----
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

        # ----- CAMPOS -----
        titulo = st.text_input("Título da tarefa :", value=titulo_default)
        descricao = st.text_input("Descrição da tarefa :", value=descricao_default)

        col1, col2 = st.columns(2)
        with col1:
            hora_inicial = st.time_input("Hora inicial :", value=pd.to_datetime(hora_ini_default).time())
        with col2:
            hora_final = st.time_input("Hora final :", value=pd.to_datetime(hora_fim_default).time())

        col3, col4 = st.columns(2)
        with col3:
            data = st.date_input("Data da tarefa :")
        with col4:
            recorrencia = st.selectbox(
                "Tipo de recorrência :",
                tipos_recorrencia,
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        criada = st.selectbox("Criador da tarefa: ", ["John"])

        colN1, colN2 = st.columns(2)
        with colN1:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with colN2:
            loja_final = st.text_input("Loja selecionada:", loja_selecionada, disabled=True)

        colbtn1, colbtn2 = st.columns(2)
        enviar = colbtn1.form_submit_button("Enviar tarefa")
        salvar_tarefas = colbtn2.form_submit_button("Salvar como modelo")

    # ===================================================
    # ENVIAR TAREFA
    # ===================================================

    if enviar:

        if not nome:
            st.error("Selecione um *Nome do GL* para enviar a tarefa.")
            st.stop()

        pagina = client.open_by_key(planilha_chave).worksheet(nome)
        novo_id = len(pagina.get_all_records()) + 1


        pagina.append_row([
            novo_id,
            criada,
            loja_final,
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

    # ===================================================
    # SALVAR MODELO
    # ===================================================

    if salvar_tarefas:
        novo_id = len(aba_modelos.get_all_records()) + 1
        aba_modelos.append_row([
            novo_id,
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
        ])

        st.success("Modelo salvo com sucesso!")

def criar_page_chrys():

    if "role" not in st.session_state or st.session_state.role not in ["Victor","Felipe","John","Fabiana","Chrys"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # --- CONFIG ---
    gcp_info = st.secrets["chr"]
    planilha_chave = st.secrets["planilha"]["chave"]

    creds = Credentials.from_service_account_info(
        dict(gcp_info),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G",
                       layout="wide",
                       page_icon=icon)

    # --- LISTAS ---
    gvs = ["", 
        
        "GLS DA CARTEIRA DE CHRYS",
        "EU"
       
    ]
        
    lojas_por_carteira = {
        "": [""],
     
        "GLS DA CARTEIRA DE CHRYS": [
            "LOJA BOULEVARD"
        ],
        "EU": [
            "Minhas Tarefas"
        ]
    }

    nomes_por_loja = {
        "": [""],
        "LOJA BOULEVARD": ["Todos Boulevard","Camyla","Bruno","Gilvania"],
        "Minhas Tarefas": ["Chrys"]
    }

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    # --- FUNÇÃO NOTIFICAÇÃO ---
 
    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasChrys")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)
    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

    # --- HEADER / LOGO ---
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Rotina de Excelência Gerencial")

    st.divider()
    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)
    st.divider()

    # ===================================================
    # SELEÇÃO DINÂMICA - CORRIGIDA
    # ===================================================

    # 1) Escolhe carteira
    envio = st.selectbox("Carteira :", gvs)

    # 2) Filtra lojas da carteira
    lojas = [""] + lojas_por_carteira.get(envio, [])

    # 3) Escolhe loja
    loja_selecionada = st.selectbox("Loja :", lojas)

    # 4) Filtra nomes daquela loja
    lista_nomes = [""] + nomes_por_loja.get(loja_selecionada, [])

    # ===================================================
    # FORMULÁRIO
    # ===================================================

    with st.form("Forms"):

        # ----- Aplicar modelo -----
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

        # ----- CAMPOS -----
        titulo = st.text_input("Título da tarefa :", value=titulo_default)
        descricao = st.text_input("Descrição da tarefa :", value=descricao_default)

        col1, col2 = st.columns(2)
        with col1:
            hora_inicial = st.time_input("Hora inicial :", value=pd.to_datetime(hora_ini_default).time())
        with col2:
            hora_final = st.time_input("Hora final :", value=pd.to_datetime(hora_fim_default).time())

        col3, col4 = st.columns(2)
        with col3:
            data = st.date_input("Data da tarefa :")
        with col4:
            recorrencia = st.selectbox(
                "Tipo de recorrência :",
                tipos_recorrencia,
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        criada = st.selectbox("Criador da tarefa: ", ["Victor"])

        colN1, colN2 = st.columns(2)
        with colN1:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with colN2:
            loja_final = st.text_input("Loja selecionada:", loja_selecionada, disabled=True)

        colbtn1, colbtn2 = st.columns(2)
        enviar = colbtn1.form_submit_button("Enviar tarefa")
        salvar_tarefas = colbtn2.form_submit_button("Salvar como modelo")

    # ===================================================
    # ENVIAR TAREFA
    # ===================================================

    if enviar:

        if not nome:
            st.error("Selecione um *Nome do GL* para enviar a tarefa.")
            st.stop()

        pagina = client.open_by_key(planilha_chave).worksheet(nome)
        novo_id = len(pagina.get_all_records()) + 1

    

        pagina.append_row([
            novo_id,
            criada,
            loja_final,
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

    # ===================================================
    # SALVAR MODELO
    # ===================================================

    if salvar_tarefas:
        novo_id = len(aba_modelos.get_all_records()) + 1
        aba_modelos.append_row([
            novo_id,
            titulo,
            descricao,
            hora_inicial.strftime("%H:%M"),
            hora_final.strftime("%H:%M"),
            data.strftime("%d/%m/%Y"),
            recorrencia,
        ])

        st.success("Modelo salvo com sucesso!")

