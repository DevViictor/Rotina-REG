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

    carteiras = {
        "TODOS OS GLS": sum(nomes_por_loja.values(), []),

        "GLS DA CARTEIRA DE FABIANA":
            nomes_por_loja["LOJA SSA |"] +
            nomes_por_loja["LOJA SSA ||"] +
            nomes_por_loja["LOJA BELA VISTA"] +
            nomes_por_loja["LOJA PARALELA"] +
            nomes_por_loja["LOJA PARQUE SHOP"],

        "GLS DA CARTEIRA DE FELIPE":
            nomes_por_loja["LOJA IGUATEMI | BA"] +
            nomes_por_loja["LOJA IGUATEMI || BA"] +
            nomes_por_loja["LOJA NORT SHOP"],

        "GLS DA CARTEIRA DE JHON":
            nomes_por_loja["LOJA BARRA"] +
            nomes_por_loja["LOJA PIEDADE"] +
            nomes_por_loja["LOJA LAPA"] +
            nomes_por_loja["LOJA BOULEVARD"],

        "GLS DA CARTEIRA DE CHRYS":
        
            nomes_por_loja["LOJA BOULEVARD"],

        "TODOS OS ITINERANTES": nomes_por_loja["ITINERANTES"],
    }

    lojas = [" ", "LOJA IGUATEMI | BA", "LOJA IGUATEMI || BA", "LOJA SSA |",
             "LOJA SSA ||", "LOJA BELA VISTA", "LOJA PARALELA",
             "LOJA PARQUE SHOP", "LOJA NORT SHOP", "LOJA BARRA",
             "LOJA PIEDADE", "LOJA LAPA", "LOJA BOULEVARD"]

    para = [" ","TODOS OS GLS", 
            "GLS DA CARTEIRA DE FABIANA",
            "GLS DA CARTEIRA DE FELIPE",
            "GLS DA CARTEIRA DE CRIS",
            "TODOS OS ITINERANTES"]

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    

    # --- FUNÇÃO NOTIFICAÇÃO ---
    def notificacao(loja,):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]

        messagem = f"Novas tarefas foram criadas.\nLoja: {loja}.\nVisualize o painel de tarefas."

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

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.header("R.E.G - Rotina de Excelência Gerencial")

    st.divider()

    st.subheader("Reutilizar tarefa")
    modelo_escolhido = st.selectbox("Selecione um modelo salvo:", lista_modelos)

    st.divider()

    # --- SELECIONA CARTEIRA AQUI! (ANTES de montar lista de nomes) ---
    envio = st.selectbox("Carteira :", para)

    # --- Agora sim a lista de nomes é carregada corretamente ---
    lista_nomes = [""] + carteiras.get(envio, [])

    

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
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        por = ["Victor"]
        criada = st.selectbox("Criador da terefa: ",por)
        cold, cole = st.columns(2)

        with cold:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with cole:
            loja = st.selectbox("Loja :", lojas)

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
            criada,
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
        pagina = client.open_by_key(planilha_chave).worksheet("ModelosTarefas")
        
        novo_id = len(pagina.get_all_records()) + 1
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
    nomes_por_loja = {
        # --- GV 1 - FABIANA SACRAMENTO ---
        "LOJA SSA |": ["Ana", "Francisca", "Vinicius"],
        "LOJA SSA ||": ["Vitor", "Mailan"],
        "LOJA BELA VISTA": ["Vanessa", "Danilo"],
        "LOJA PARALELA": ["Crislaine", "Neide"],
        "LOJA PARQUE SHOP": ["Denise", "Adrielle"],

    }

    carteiras = {
        
        "GLS DA CARTEIRA DE FABIANA":
            nomes_por_loja["LOJA SSA |"] +
            nomes_por_loja["LOJA SSA ||"] +
            nomes_por_loja["LOJA BELA VISTA"] +
            nomes_por_loja["LOJA PARALELA"] +
            nomes_por_loja["LOJA PARQUE SHOP"],

    }

    lojas = [" ", "LOJA SSA |",
             "LOJA SSA ||", "LOJA BELA VISTA", "LOJA PARALELA",
             "LOJA PARQUE SHOP",] 

    para = [" ", 
            "GLS DA CARTEIRA DE FABIANA",
            ]
    
    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    
    # --- FUNÇÃO NOTIFICAÇÃO ---
    def notificacao(loja,):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]

        messagem = f"Novas tarefas foram criadas.\nLoja: {loja}.\nVisualize o painel de tarefas."

        requests.post("https://api.pushover.net/1/messages.json", 
                      data={
                          "token": api_token,
                          "user": user_key,
                          "message": messagem
                      })

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasFabiana")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)

    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

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

    # --- SELECIONA CARTEIRA AQUI! (ANTES de montar lista de nomes) ---
    envio = st.selectbox("Carteira :", para)

    # --- Agora sim a lista de nomes é carregada corretamente ---
    lista_nomes = [""] + carteiras.get(envio, [])

    
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
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        por = ["Fabiana"]
        criada = st.selectbox("Criador da terefa: ",por)
        cold, cole = st.columns(2)

        with cold:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with cole:
            loja = st.selectbox("Loja :", lojas)

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
            criada,
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
        pagina = client.open_by_key(planilha_chave).worksheet("ModelosTarefasFabiana")
        
        novo_id = len(pagina.get_all_records()) + 1
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
    nomes_por_loja = {
        # --- GV 2 - FELIPE SILVA ---
        "LOJA IGUATEMI | BA": ["Max", "Denise"],
        "LOJA IGUATEMI || BA": ["Diego", "Andressa"],
        "LOJA NORT SHOP": ["Jairo", "Wanderlei"],
    }

    carteiras = {
        
        "GLS DA CARTEIRA DE FELIPE":
            nomes_por_loja["LOJA IGUATEMI | BA"] +
            nomes_por_loja["LOJA IGUATEMI || BA"] +
            nomes_por_loja["LOJA NORT SHOP"],

    }

    lojas = [" ", "LOJA IGUATEMI | BA", "LOJA IGUATEMI || BA",
             "LOJA NORT SHOP",
             ]

    para = [" ",
            "GLS DA CARTEIRA DE FELIPE",
            ]

    
    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    
    # --- FUNÇÃO NOTIFICAÇÃO ---
    def notificacao(loja,):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]

        messagem = f"Novas tarefas foram criadas.\nLoja: {loja}.\nVisualize o painel de tarefas."

        requests.post("https://api.pushover.net/1/messages.json", 
                      data={
                          "token": api_token,
                          "user": user_key,
                          "message": messagem
                      })

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasFelipe")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)

    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

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

    # --- SELECIONA CARTEIRA AQUI! (ANTES de montar lista de nomes) ---
    envio = st.selectbox("Carteira :", para)

    # --- Agora sim a lista de nomes é carregada corretamente ---
    lista_nomes = [""] + carteiras.get(envio, [])

    
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
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        por = ["Felipe"]
        criada = st.selectbox("Criador da terefa: ",por)
        cold, cole = st.columns(2)

        with cold:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with cole:
            loja = st.selectbox("Loja :", lojas)

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
            criada,
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
        pagina = client.open_by_key(planilha_chave).worksheet("ModelosTarefasFelipe")
        
        novo_id = len(pagina.get_all_records()) + 1
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
    nomes_por_loja = {
        
        # --- GV 1 - JOHM COITO ---
        "LOJA BARRA": ["Igor", "Carol", "Alana"],
        "LOJA PIEDADE": ["Diego", "Marcus"],
        "LOJA LAPA": ["Sara", "Rafael"], 
    }

    carteiras = {
        "TODOS OS GLS": sum(nomes_por_loja.values(), []),
        
        "GLS DA CARTEIRA DE JOHN":
            nomes_por_loja["LOJA BARRA"] +
            nomes_por_loja["LOJA PIEDADE"] +
            nomes_por_loja["LOJA LAPA"],

    }

    lojas = [" ", 
             "LOJA BARRA",
             "LOJA PIEDADE", "LOJA LAPA"]

    para = [" ",
            "GLS DA CARTEIRA DE JOHN",]

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    

    # --- FUNÇÃO NOTIFICAÇÃO ---
    def notificacao(loja,):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]

        messagem = f"Novas tarefas foram criadas.\nLoja: {loja}.\nVisualize o painel de tarefas."

        requests.post("https://api.pushover.net/1/messages.json", 
                      data={
                          "token": api_token,
                          "user": user_key,
                          "message": messagem
                      })

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasJohn")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)

    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

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

    # --- SELECIONA CARTEIRA AQUI! (ANTES de montar lista de nomes) ---
    envio = st.selectbox("Carteira :", para)

    # --- Agora sim a lista de nomes é carregada corretamente ---
    lista_nomes = [""] + carteiras.get(envio, [])

    

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
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        por = ["John"]
        criada = st.selectbox("Criador da terefa: ",por)
        cold, cole = st.columns(2)

        with cold:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with cole:
            loja = st.selectbox("Loja :", lojas)

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
            criada,
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
        pagina = client.open_by_key(planilha_chave).worksheet("ModelosTarefasJohn")
        
        novo_id = len(pagina.get_all_records()) + 1
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
    nomes_por_loja = {
        
        # --- GV 2 - CHRYS REBOUÇAS ---
        "LOJA BOULEVARD": ["Camyla", "Bruno", "Gilvania"],

    }

    carteiras = {
        "TODOS OS GLS": sum(nomes_por_loja.values(), []),

    
        "GLS DA CARTEIRA DE CHRYS":
        
            nomes_por_loja["LOJA BOULEVARD"],

       
    }

    lojas = [" ", "LOJA BOULEVARD"]

    para = [" ", 
            "GLS DA CARTEIRA DE CHRYS"]

    tipos_recorrencia = ["", "Não recorrente", "Diária", "Semanal",
                         "Semanal Laboral(seg a sex)", "Mensal", "Anual"]

    

    # --- FUNÇÃO NOTIFICAÇÃO ---
    def notificacao(loja,):
        user_key = st.secrets["notificacao"]["user_key"]
        api_token = st.secrets["notificacao"]["api_token"]

        messagem = f"Novas tarefas foram criadas.\nLoja: {loja}.\nVisualize o painel de tarefas."

        requests.post("https://api.pushover.net/1/messages.json", 
                      data={
                          "token": api_token,
                          "user": user_key,
                          "message": messagem
                      })

    # --- CARREGAR MODELOS ---
    aba_modelos = client.open_by_key(planilha_chave).worksheet("ModelosTarefasChrys")
    dados_modelos = aba_modelos.get_all_records()
    df_modelos = pd.DataFrame(dados_modelos)

    lista_modelos = [""] + df_modelos["Título"].tolist() if not df_modelos.empty else [""]

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

    # --- SELECIONA CARTEIRA AQUI! (ANTES de montar lista de nomes) ---
    envio = st.selectbox("Carteira :", para)

    # --- Agora sim a lista de nomes é carregada corretamente ---
    lista_nomes = [""] + carteiras.get(envio, [])

    

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
                index=tipos_recorrencia.index(recorrencia_default)
                if recorrencia_default in tipos_recorrencia else 0
            )

        por = ["Chrys"]
        criada = st.selectbox("Criador da terefa: ",por)
        cold, cole = st.columns(2)

        with cold:
            nome = st.selectbox("Nome do GL :", lista_nomes)

        with cole:
            loja = st.selectbox("Loja :", lojas)

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
            criada,
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
        pagina = client.open_by_key(planilha_chave).worksheet("ModelosTarefasChrys")
        
        novo_id = len(pagina.get_all_records()) + 1
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

