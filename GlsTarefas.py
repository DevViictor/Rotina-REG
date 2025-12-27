import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import datetime as dt
from PIL import Image
from datetime import datetime, timedelta


gcp_info = st.secrets["geral"]
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



def tarefas_iguatemi_abertura():


    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G Iguatemi |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi1", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FELIPE",
                ]
            
    lojas_por_carteira = {
    " ": [" "],
    
    "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI | BA"
    
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA IGUATEMI | BA": ["Max"],
   
    }
    # ---------------------------
    # INTERFACE
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

  
    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Max",
            "Iguatemi |",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    
    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



    # 🔄 Atualiza a página a cada 60s para verificar notificações


def tarefas_iguatemi_fechamento():



    # Controle de estado das notificações
    if "notificados" not in st.session_state:
        st.session_state.notificados = {}

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS -------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FELIPE",
                ]
            
    lojas_por_carteira = {
    " ": [" "],
    
    "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI | BA"
    
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA IGUATEMI | BA": ["Denise"],
   
    }
    # ---------------------------
    # INTERFACE
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)
    

  
    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    

    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Denise",
            "Iguatemi |",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()


def tarefas_iguatemi2_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G IGUATEMI ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Iguatemi2","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GLS DA CARTEIRA DE FELIPE",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI || BA"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "LOJA IGUATEMI || BA": ["Andressa"],
    }

   
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Andressa",
            "Iguatemi ||",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
   
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")

    with col12:
        if st.button("Atualizar"):
         st.rerun()




def tarefas_iguatemi2_fechamento():
    icon = Image.open("image/vivo.png")
    
    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [
        "GLS DA CARTEIRA DE FELIPE",
    ]

    lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE FELIPE": [
            "LOJA IGUATEMI || BA"
        ]
    }

    nomes_por_loja = {
        " ": [" "],
        "LOJA IGUATEMI || BA": ["Diego"],
    }

   
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Diego",
            "Iguatemi ||",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")

    with col12:
        if st.button("Atualizar"):
         st.rerun()


def tarefas_nort_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G NORT", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Norte","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            
        "GLS DA CARTEIRA DE FELIPE",
    ]
           
        
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE FELIPE": [
            "LOJA NORT SHOP"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA NORT SHOP": ["Jairo"]
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha, row):
        aba_exec = planilha.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Jairo",
            "Nort Shop",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")

    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_nort_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G NORTE SHOP", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Norte","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            
        "GLS DA CARTEIRA DE FELIPE",
    ]
           
        
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE FELIPE": [
            "LOJA NORT SHOP"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA NORT SHOP": ["Wanderlei"]
    }

    # -------------------------
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Wanderlei",
            "Nort Shop",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()

#Fabiana


def tarefas_ssa1_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["Mércia"],   
    
    }


    # ---------------------------------
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Mércia",
            "SSA |",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_ssa1_intermedio():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["Francisca"],   
    
    }


    # ----------------------------
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   
    def carregar_pedidos():
        aba = planilha.worksheet("GLS(INTERMEDIO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Francisca",
            "SSA |",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_ssa1_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR |", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador1","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["Vinicius"],   
    
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   

    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_key(planilha_chave)

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Vinicius",
            "SSA |",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
    
    with col12:
        if st.button("Atualizar"):
         st.rerun()

def tarefas_ssa2_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador2","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA SSA |"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA |": ["Vitor"],   
    
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Vitor",
            "SSA |",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_ssa2_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G SALVADOR ||", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Salvador2", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            ]
        
    lojas_por_carteira = {
    " ": [" "],  

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA SSA ||"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA SSA ||": ["Mailan"],
    
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    
    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Mailan",
            "SSA ||",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
            
    with col12:
        if st.button("Atualizar"):
         st.rerun()




def tarefas_bela_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BELA VISTA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Bela", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
                "GLS DA CARTEIRA DE FABIANA",
                ]
            
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA BELA VISTA"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BELA VISTA": ["Danilo"]
    
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Danilo",
            "Bela",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()

def tarefas_bela_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BELA VISTA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Bela","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
                "GLS DA CARTEIRA DE FABIANA",
                ]
            
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA BELA VISTA"
    ]
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BELA VISTA": ["Vanessa"]
    
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Vanessa",
            "Bela",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")

    with col12:
        if st.button("Atualizar"):
         st.rerun()

def tarefas_parela_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARALELA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Paralela", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()
   
    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        "GLS DA CARTEIRA DE FABIANA",]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA PARALELA"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PARALELA": ["Crislaine"]
    }
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Crislaine",
            "Paralela",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")

    with col12:
        if st.button("Atualizar"):
         st.rerun()






def tarefas_parela_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARALELA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Paralela", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        "GLS DA CARTEIRA DE FABIANA",]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA PARALELA"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PARALELA": ["Neide"]
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)



    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Neide",
            "Paralela",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
            
    with col12:
        if st.button("Atualizar"):
         st.rerun()


    
def tarefas_parque_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARQUE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Parque", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
           ]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA PARQUE SHOP"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA PARQUE SHOP": ["Denise_Parque"],
    
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Denise_Parque",
            "Parque",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()






def tarefas_parque_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PARQUE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Parque", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
           ]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
                "LOJA PARQUE SHOP"
    ],
   
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA PARQUE SHOP": ["Adrielle"],
    
    }


    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Adrielle",
            "Parque",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



#LOJAS JOHN

def tarefas_barra_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Barra", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
           ]
    
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA"
    ],
    
    }

    nomes_por_loja = {
    " ": [" "],

    "LOJA BARRA": ["Carol"],
    
    }
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Carol",
            "Barra",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_barra_intermedio():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Barra", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
           ]
    
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA"
    ],
    
    }

    nomes_por_loja = {
    " ": [" "],

    "LOJA BARRA": ["Alana"],
    
    }
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(INTERMEDIO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Alana",
            "Barra",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                st.rerun()
    with col12:
        if st.button("Atualizar"):
         st.rerun()


def tarefas_barra_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BARRA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Barra", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
           ]
    
    lojas_por_carteira = {
    " ": [" "],
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA BARRA"
    ],
    
    }

    nomes_por_loja = {
    " ": [" "],

    "LOJA BARRA": ["Igor"],
    
    }
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    
    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Igor",
            "Barra",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()

def tarefas_piedade_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PIEDADE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in  ["Piedade","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        
            "GLS DA CARTEIRA DE JOHN",
            ]
        
    lojas_por_carteira = {
    " ": [" "],
    "TODOS OS GLS": [
                "LOJA PIEDADE",
            
    ],
  
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA PIEDADE"
    ]     
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PIEDADE": ["DiegoP"],
    
    }
   
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "DiegoP",
            "Piedade",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()


def tarefas_piedade_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G PIEDADE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in  ["Piedade","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
        
            "GLS DA CARTEIRA DE JOHN",
            ]
        
    lojas_por_carteira = {
    " ": [" "],
    "TODOS OS GLS": [
                "LOJA PIEDADE",
            
    ],
  
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA PIEDADE"
    ]     
    }

    nomes_por_loja = {
    " ": [" "],
    "LOJA PIEDADE": ["Marcusl"],
    
    }
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Marcusl",
            "Piedade",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()


         

def tarefas_lapa_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LAPA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Lapa", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
                ]
            
    lojas_por_carteira = {
    " ": [" "],
    
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA LAPA"
    
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA LAPA": ["Rafael"],
   
    }

    # INTERFACE
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    
    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Rafael",
            "Lapa",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()




def tarefas_lapa_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LAPA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Lapa", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE JOHN",
                ]
            
    lojas_por_carteira = {
    " ": [" "],
    
    "GLS DA CARTEIRA DE JOHN": [
            "LOJA LAPA"
    
    ]        
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA LAPA": ["Sara"],
   
    }
    # ----------------------
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Sara",
            "Lapa",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Hora","Data","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
    
    with col12:
        if st.button("Atualizar"):
         st.rerun()

        



def tarefas_diasdavila_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G DIAS DAVILA", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Davila", "Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE FABIANA"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE FABIANA": [
        "LOJA DIAS DAVILA"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA DIAS DAVILA": ["Maise"],
    }


    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Maise",
            "Dias Davila",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_boulevard_abertura():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Boulevard","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE CHRYS": [
         "LOJA BOULEVARD"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BOULEVARD": ["Bruno"],
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(ABERTURA)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Bruno",
            "Boulevard",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_boulevard_fechamento():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Boulevard","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE CHRYS": [
         "LOJA BOULEVARD"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BOULEVARD": ["Gilvania"],
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Gilvania",
            "Boulevard",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()


def tarefas_boulevard_intermedio():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G BOULEVARD", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Boulevard","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "GLS DA CARTEIRA DE CHRYS"]
        
    lojas_por_carteira = {
    " ": [" "],

    "GLS DA CARTEIRA DE CHRYS": [
         "LOJA BOULEVARD"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "LOJA BOULEVARD": ["Alana"],
    }

    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("GLS(INTERMEDIO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Alana",
            "Boulevard",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")
        valores = aba.get_all_values()

        if len(valores) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(valores[1:], columns=valores[0])
        df["Observação"] = df["Observação"].fillna("")
        return df


    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()







def tarefas_itinerante_lee():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G LEE", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerantes","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],

    "ITINERANTES": [
         "ITINERANTES"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["Lee"],
    }


    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)


    def carregar_pedidos():
        aba = planilha.worksheet("ITINERANTES")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("REGISTROS(ITINERANTES)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Lee",
            "Itinerante",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("REGISTROS(ITINERANTES)")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()
    # --------------------------

def tarefas_itinerante_marcus():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G Marcus", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerantes","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],

    "ITINERANTES": [
         "ITINERANTES"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["Marcus"],
    }


    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   
    def carregar_pedidos():
        aba = planilha.worksheet("ITINERANTES")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("REGISTROS(ITINERANTES)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Marcus",
            "Itinerante",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("REGISTROS(ITINERANTES)")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()



def tarefas_itinerante_lazaro():
    icon = Image.open("image/vivo.png")

    st.set_page_config(page_title="R.E.G Lázaro", page_icon=icon, layout="wide")

    # --- Controle de acesso ---
    if "role" not in st.session_state or st.session_state.role not in ["Itinerantes","Admin"]:
        st.error("⚠️ Acesso negado!")
        st.stop()

    # ---------------------------
    # LISTAS E DICIONÁRIOS
    # ---------------------------
    gvs = [ 
            "ITINERANTES"]
        
    lojas_por_carteira = {
    " ": [" "],

    "ITINERANTES": [
         "ITINERANTES"
    ],      
    }

    nomes_por_loja = {
    " ": [" "],
    
    "ITINERANTES": ["Lázaro"],
    }


    # ------------------------
    # ---------------------------
    icon = Image.open("image/vivo.png")
    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4, 1, 1])

    with colc:
        st.image(image_logo)

    with cola:
        st.title("📝 R.E.G - TAREFAS")

    col1, col2, col3, col4 = st.columns(4)

   

    def carregar_pedidos():
        aba = planilha.worksheet("ITINERANTES")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    if "df_tarefas" not in st.session_state:
        st.session_state.df_tarefas = planilha_Dados.copy()
    
    def registrar_execucao(planilha_exc, row):
        aba_exec = planilha_exc.worksheet("REGISTROS(ITINERANTES)")

        agora = datetime.now()
        data_hoje = agora.strftime("%d/%m/%Y")
        hora_agora = agora.strftime("%H:%M:%S")

        # lê todos os registros
        registros = aba_exec.get_all_records()

        linha_para_atualizar = None

        for i, r in enumerate(registros, start=2):  # start=2 por causa do cabeçalho
            if str(r["ID"]) == str(row["ID"]) and r["Data"] == data_hoje:
                linha_para_atualizar = i
                break

        valores = [
            row["ID"],
            row["Título"],
            row["Descrição da tarefa"],
            "Lázaro",
            "Itinerante",
            data_hoje,
            hora_agora,
            row["Observação"],
        ]

        if linha_para_atualizar:
            aba_exec.update(f"A{linha_para_atualizar}:H{linha_para_atualizar}", [valores])
        else:
    
            aba_exec.append_row(valores)


    colunas_desejadas = ["ID","Criada", "Título", "Descrição da tarefa","Hora inicial","Hora final","Data","Observação"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
  
    # ---------------------------
    # CHECKBOX PARA CONCLUIR TAREFA
    # ---------------------------
    if "Concluir" not in planilha_Dados.columns:
        planilha_Dados["Concluir"] = False

    df_editado = st.data_editor(
        planilha_Dados,
        column_config={
            "Concluir": st.column_config.CheckboxColumn(
                "Registrar",
                help="Marque para registrar a conclusão da tarefa"
            ),
            "Observação": st.column_config.TextColumn(
            "Observação",
            help="Digite uma observação sobre a tarefa",
            max_chars=200
        )
        },
        
        disabled=["ID"]
    )

    st.divider()
    
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)

    lojas_filtradas = lojas_por_carteira.get(carteira, [" "])

    with col2:
        loja = st.selectbox("Selecione a loja:", lojas_filtradas)

    with col3:
        nomes_filtrados = nomes_por_loja.get(loja, [" "])
        nome = st.selectbox("Nome:", nomes_filtrados)

    with col4:
        data = st.date_input("Selecione a data")

    def carregar_registro():
        aba = planilha_exc.worksheet("REGISTROS(ITINERANTES)")
        dados = aba.get_all_records()
        return pd.DataFrame(dados)

    planilha_registros = carregar_registro()

    colunas_desejadas2 = ["ID","Titulo", "Descrição da tarefa","GL","Loja","Data","Hora","Observação"]
    planilha_registros = planilha_registros[colunas_desejadas2]

    if nome:
        planilha_registros = planilha_registros[planilha_registros["GL"].str.contains(nome,case =False)]

    if data:
            data_str = data.strftime("%d/%m/%Y")
            planilha_registros = planilha_registros[planilha_registros["Data"] == data_str]

    
    st.subheader("Registro de Tarefas")
    
    if planilha_registros.empty:
        st.warning("Nenhum registro nessa data")
    else:
        st.dataframe(planilha_registros)

# ---------------------------
    # SALVAR ALTERAÇÕES NO GOOGLE SHEETS
    # ---------------------------
    col11, col12, col13, col14, col15 = st.columns(5)

    with col11:
           if st.button("Salvar alterações"):
                
                df_editado[df_editado["Concluir"]]

                for _, row in df_editado.iterrows():
                    if row["Concluir"]:
                        registrar_execucao(
                            planilha_exc,
                            row,     # vem da aba de tarefas    # loja selecionada
                        )
                st.success("✔️ Registro efetuado com sucesso!")
                
    with col12:
        if st.button("Atualizar"):
         st.rerun()