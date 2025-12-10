import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image


def visualizar_tarefas():
        # ---- Controle de acesso ----
        if "role" not in st.session_state or st.session_state.role not in ["Victor","Fabiana","Felipe","John","Chrys"]:
                st.error("⚠️ Acesso negado!")
                st.stop()

        # ---------------------------
        # LISTAS E DICIONÁRIOS
        # ---------------------------
        gvs = [ 
            "GLS DA CARTEIRA DE FABIANA",
            "GLS DA CARTEIRA DE FELIPE",
            "GLS DA CARTEIRA DE CHRYS",
            "GLS DA CARTEIRA DE JOHN",
            "TODOS OS ITINERANTES"]
        
        lojas_por_carteira = {
        " ": [" "],
        "TODOS OS GLS": [
                 "LOJA IGUATEMI | BA", "LOJA IGUATEMI || BA", "LOJA SSA |",
                "LOJA SSA ||", "LOJA BELA VISTA", "LOJA PARALELA",
                "LOJA PARQUE SHOP", "LOJA NORT SHOP", "LOJA BARRA",
                "LOJA PIEDADE", "LOJA LAPA", "LOJA BOULEVARD"
        ],
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
        "TODOS OS ITINERANTES": [
                "ITINERANTES"
        ]        
        }

        nomes_por_loja = {
        " ": [" "],
        "LOJA SSA |": ["Ana","Francisca","Vinicius"],
        "LOJA SSA ||": ["Vitor","Mailan"],
        "LOJA BELA VISTA": ["Vanessa","Danilo"],
        "LOJA PARALELA": ["Crislaine","Neide"],
        "LOJA PARQUE SHOP": ["Denise_Parque","Neide"],
        "LOJA IGUATEMI | BA": ["Max","Denise"],
        "LOJA IGUATEMI || BA": ["Diego","Andressa"],
        "LOJA NORT SHOP": ["Jairo","Wanderlei"],
        "LOJA BARRA": ["Igor","Carol","Alana"],
        "LOJA PIEDADE": ["DiegoL","Marcus"],
        "LOJA LAPA": ["Sara","Rafel"],
        "LOJA BOULEVARD": ["Camyla","Bruno","Gilvania"],
        "ITINERANTES": ["Lázaro","Lee","Marcus"],
        }

        # ---------------------------
        # INTERFACE
        # ---------------------------
        icon = Image.open("image/vivo.png")
        st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

        image_logo = Image.open("image/Image (2).png")

        cola, colb, colc = st.columns([4,1,1])

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
                data = st.date_input("Selecione a data:")

        # ---------------------------
        # CONFIGURAÇÃO GOOGLE SHEETS
        # ---------------------------
        gcp_info = st.secrets["taf"]
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
        else:

                colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa", "Data"]
                planilha_Dados = planilha_Dados[colunas_desejadas]

                planilha_Dados["Data"] = pd.to_datetime(
                        planilha_Dados["Data"],
                        dayfirst=True,
                        errors="coerce"
                ).dt.date

                planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

                contagemA = planilha_Dados["Criada"].astype(str).str.contains("Victor", case=False, na=False).sum()

                # ---------------------------
                # CHECKBOX PARA EXCLUSÃO
                # ---------------------------
                planilha_Dados["Excluir"] = False

                st.subheader(f"Tarefas criadas para {nome}:")
                tabela_editada = st.data_editor(
                planilha_Dados,
                hide_index=True,
                use_container_width=True
                )

                ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

                st.text(f"Quantidade de tarefas criadas: {contagemA}")
                # ---------------------------
                # FUNÇÃO EXCLUSÃO NO GOOGLE
                # ---------------------------
                def excluir_por_id(id_valor, aba):
                        valores = aba.col_values(1)  # coluna A

                        try:
                                linha = valores.index(str(id_valor)) + 1
                                aba.delete_rows(linha)
                                return True
                        except ValueError:
                                return False

                # ---------------------------
                # BOTÃO DE EXCLUSÃO
                # ---------------------------
                if st.button("🗑️ Excluir tarefa"):
                        if not ids_para_excluir:
                                st.warning("Nenhuma tarefa marcada.")
                        else:
                                aba = planilha.worksheet(nome)
                                count = 0

                                for id_valor in ids_para_excluir:
                                        if excluir_por_id(id_valor, aba):
                                                count += 1

                                st.success(f"{count} tarefa(s) excluída(s) com sucesso!")
                                st.rerun()


def visualizar_tarefas_fabiana():
        # ---- Controle de acesso ----
        if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
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
        "TODOS OS GLS": [
                "LOJA SSA |",
                "LOJA SSA ||", "LOJA BELA VISTA", "LOJA PARALELA",
                "LOJA PARQUE SHOP" 
        ],
        "GLS DA CARTEIRA DE FABIANA": [
                 "LOJA SSA |","LOJA SSA ||","LOJA BELA VISTA ","LOJA PARALELA","LOJA PARQUE SHOP"
        ]
        }

        nomes_por_loja = {
        " ": [" "],
        "LOJA SSA |": ["Ana","Francisca","Vinicius"],
        "LOJA SSA ||": ["Vitor","Mailan"],
        "LOJA BELA VISTA": ["Vanessa","Danilo"],
        "LOJA PARALELA": ["Crislaine","Neide"],
        "LOJA PARQUE SHOP": ["Denise_Parque","Neide"],
        }

        # ---------------------------
        # INTERFACE
        # ---------------------------
        icon = Image.open("image/vivo.png")
        st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

        image_logo = Image.open("image/Image (2).png")

        cola, colb, colc = st.columns([4,1,1])

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
                data = st.date_input("Selecione a data:")

        # ---------------------------
        # CONFIGURAÇÃO GOOGLE SHEETS
        # ---------------------------
        gcp_info = st.secrets["taf"]
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
        else:

                colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa", "Data"]
                planilha_Dados = planilha_Dados[colunas_desejadas]

                planilha_Dados["Data"] = pd.to_datetime(
                        planilha_Dados["Data"],
                        dayfirst=True,
                        errors="coerce"
                ).dt.date

                planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

                contagemA = planilha_Dados["Criada"].astype(str).str.contains("Victor", case=False, na=False).sum()

                # ---------------------------
                # CHECKBOX PARA EXCLUSÃO
                # ---------------------------
                planilha_Dados["Excluir"] = False

                st.subheader(f"Tarefas criadas para {nome}:")
                tabela_editada = st.data_editor(
                planilha_Dados,
                hide_index=True,
                use_container_width=True
                )

                ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

                st.text(f"Quantidade de tarefas criadas: {contagemA}")
                # ---------------------------
                # FUNÇÃO EXCLUSÃO NO GOOGLE
                # ---------------------------
                def excluir_por_id(id_valor, aba):
                        valores = aba.col_values(1)  # coluna A

                        try:
                                linha = valores.index(str(id_valor)) + 1
                                aba.delete_rows(linha)
                                return True
                        except ValueError:
                                return False

                # ---------------------------
                # BOTÃO DE EXCLUSÃO
                # ---------------------------
                if st.button("🗑️ Excluir tarefa"):
                        if not ids_para_excluir:
                                st.warning("Nenhuma tarefa marcada.")
                        else:
                                aba = planilha.worksheet(nome)
                                count = 0

                                for id_valor in ids_para_excluir:
                                        if excluir_por_id(id_valor, aba):
                                                count += 1

                                st.success(f"{count} tarefa(s) excluída(s) com sucesso!")
                                st.rerun()





def visualizar_tarefas_felipe():
        # ---- Controle de acesso ----
        if "role" not in st.session_state or st.session_state.role != "Felipe":
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
                "LOJA IGUATEMI | BA","LOJA IGUATEMI || BA","LOJA NORT SHOP"
        ]
        }

        nomes_por_loja = {
        " ": [" "],
      
        "LOJA IGUATEMI | BA": ["Max","Denise"],
        
        "LOJA NORT SHOP": ["Jairo","Wanderlei"],
        }

        # ---------------------------
        # INTERFACE
        # ---------------------------
        icon = Image.open("image/vivo.png")
        st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

        image_logo = Image.open("image/Image (2).png")

        cola, colb, colc = st.columns([4,1,1])

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
                data = st.date_input("Selecione a data:")

        # ---------------------------
        # CONFIGURAÇÃO GOOGLE SHEETS
        # ---------------------------
        gcp_info = st.secrets["taf"]
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
        else:

                colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa", "Data"]
                planilha_Dados = planilha_Dados[colunas_desejadas]

                planilha_Dados["Data"] = pd.to_datetime(
                        planilha_Dados["Data"],
                        dayfirst=True,
                        errors="coerce"
                ).dt.date

                planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

                contagemA = planilha_Dados["Criada"].astype(str).str.contains("Victor", case=False, na=False).sum()

                # ---------------------------
                # CHECKBOX PARA EXCLUSÃO
                # ---------------------------
                planilha_Dados["Excluir"] = False

                st.subheader(f"Tarefas criadas para {nome}:")
                tabela_editada = st.data_editor(
                planilha_Dados,
                hide_index=True,
                use_container_width=True
                )

                ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

                st.text(f"Quantidade de tarefas criadas: {contagemA}")
                # ---------------------------
                # FUNÇÃO EXCLUSÃO NO GOOGLE
                # ---------------------------
                def excluir_por_id(id_valor, aba):
                        valores = aba.col_values(1)  # coluna A

                        try:
                                linha = valores.index(str(id_valor)) + 1
                                aba.delete_rows(linha)
                                return True
                        except ValueError:
                                return False

                # ---------------------------
                # BOTÃO DE EXCLUSÃO
                # ---------------------------
                if st.button("🗑️ Excluir tarefa"):
                        if not ids_para_excluir:
                                st.warning("Nenhuma tarefa marcada.")
                        else:
                                aba = planilha.worksheet(nome)
                                count = 0

                                for id_valor in ids_para_excluir:
                                        if excluir_por_id(id_valor, aba):
                                                count += 1

                                st.success(f"{count} tarefa(s) excluída(s) com sucesso!")
                                st.rerun()



def visualizar_tarefas_john():
        # ---- Controle de acesso ----
        if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
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
                
                "LOJA BARRA",
                "LOJA PIEDADE", "LOJA LAPA"
        ],
       
        "GLS DA CARTEIRA DE JOHN": [
                "LOJA BARRA","LOJA PIEDADE","LOJA LAPA"
        ],
        }

        nomes_por_loja = {
        " ": [" "],
        "LOJA BARRA": ["Igor","Carol","Alana"],
        "LOJA PIEDADE": ["DiegoL","Marcus"],
        "LOJA LAPA": ["Sara","Rafel"],
        }

        # ---------------------------
        # INTERFACE
        # ---------------------------
        icon = Image.open("image/vivo.png")
        st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

        image_logo = Image.open("image/Image (2).png")

        cola, colb, colc = st.columns([4,1,1])

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
                data = st.date_input("Selecione a data:")

        # ---------------------------
        # CONFIGURAÇÃO GOOGLE SHEETS
        # ---------------------------
        gcp_info = st.secrets["taf"]
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
        else:

                colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa", "Data"]
                planilha_Dados = planilha_Dados[colunas_desejadas]

                planilha_Dados["Data"] = pd.to_datetime(
                        planilha_Dados["Data"],
                        dayfirst=True,
                        errors="coerce"
                ).dt.date

                planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

                contagemA = planilha_Dados["Criada"].astype(str).str.contains("Victor", case=False, na=False).sum()

                # ---------------------------
                # CHECKBOX PARA EXCLUSÃO
                # ---------------------------
                planilha_Dados["Excluir"] = False

                st.subheader(f"Tarefas criadas para {nome}:")
                tabela_editada = st.data_editor(
                planilha_Dados,
                hide_index=True,
                use_container_width=True
                )

                ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

                st.text(f"Quantidade de tarefas criadas: {contagemA}")
                # ---------------------------
                # FUNÇÃO EXCLUSÃO NO GOOGLE
                # ---------------------------
                def excluir_por_id(id_valor, aba):
                        valores = aba.col_values(1)  # coluna A

                        try:
                                linha = valores.index(str(id_valor)) + 1
                                aba.delete_rows(linha)
                                return True
                        except ValueError:
                                return False

                # ---------------------------
                # BOTÃO DE EXCLUSÃO
                # ---------------------------
                if st.button("🗑️ Excluir tarefa"):
                        if not ids_para_excluir:
                                st.warning("Nenhuma tarefa marcada.")
                        else:
                                aba = planilha.worksheet(nome)
                                count = 0

                                for id_valor in ids_para_excluir:
                                        if excluir_por_id(id_valor, aba):
                                                count += 1

                                st.success(f"{count} tarefa(s) excluída(s) com sucesso!")
                                st.rerun()


def visualizar_tarefas_chrys():
        # ---- Controle de acesso ----
        if "role" not in st.session_state or st.session_state.role not in ["Fabiana","Felipe","John","Chrys"]:
                st.error("⚠️ Acesso negado!")
                st.stop()

        # ---------------------------
        # LISTAS E DICIONÁRIOS
        # ---------------------------
        gvs = [ 

            "GLS DA CARTEIRA DE CHRYS",
          ]
        
        lojas_por_carteira = {
        " ": [" "],
        "GLS DA CARTEIRA DE CHRYS": [
                "LOJA BOULEVARD"
        ]
        }

        nomes_por_loja = {
        " ": [" "],
        "LOJA BOULEVARD": ["Camyla","Bruno","Gilvania"],
        }

        # ---------------------------
        # INTERFACE
        # ---------------------------
        icon = Image.open("image/vivo.png")
        st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

        image_logo = Image.open("image/Image (2).png")

        cola, colb, colc = st.columns([4,1,1])

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
                data = st.date_input("Selecione a data:")

        # ---------------------------
        # CONFIGURAÇÃO GOOGLE SHEETS
        # ---------------------------
        gcp_info = st.secrets["taf"]
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
        else:

                colunas_desejadas = ["ID", "Criada", "Título", "Descrição da tarefa", "Data"]
                planilha_Dados = planilha_Dados[colunas_desejadas]

                planilha_Dados["Data"] = pd.to_datetime(
                        planilha_Dados["Data"],
                        dayfirst=True,
                        errors="coerce"
                ).dt.date

                planilha_Dados = planilha_Dados[planilha_Dados["Data"] == data]

                contagemA = planilha_Dados["Criada"].astype(str).str.contains("Victor", case=False, na=False).sum()

                # ---------------------------
                # CHECKBOX PARA EXCLUSÃO
                # ---------------------------
                planilha_Dados["Excluir"] = False

                st.subheader(f"Tarefas criadas para {nome}:")
                tabela_editada = st.data_editor(
                planilha_Dados,
                hide_index=True,
                use_container_width=True
                )

                ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

                st.text(f"Quantidade de tarefas criadas: {contagemA}")
                # ---------------------------
                # FUNÇÃO EXCLUSÃO NO GOOGLE
                # ---------------------------
                def excluir_por_id(id_valor, aba):
                        valores = aba.col_values(1)  # coluna A

                        try:
                                linha = valores.index(str(id_valor)) + 1
                                aba.delete_rows(linha)
                                return True
                        except ValueError:
                                return False

                # ---------------------------
                # BOTÃO DE EXCLUSÃO
                # ---------------------------
                if st.button("🗑️ Excluir tarefa"):
                        if not ids_para_excluir:
                                st.warning("Nenhuma tarefa marcada.")
                        else:
                                aba = planilha.worksheet(nome)
                                count = 0

                                for id_valor in ids_para_excluir:
                                        if excluir_por_id(id_valor, aba):
                                                count += 1

                                st.success(f"{count} tarefa(s) excluída(s) com sucesso!")
                                st.rerun()

