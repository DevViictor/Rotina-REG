import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image


def visualizar_notificacao():
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
        "TODOS OS ITINERANTES"
    ]
        
        lojas_por_carteira = {
            

            "GLS DA CARTEIRA DE FABIANA": [
                "Carteira(Fabiana)"

            ],
            "GLS DA CARTEIRA DE FELIPE": [
                "Carteira(Felipe)"
            ],
            "GLS DA CARTEIRA DE JOHN": [
                "Carteira(John)"
            ],
            "GLS DA CARTEIRA DE CHRYS": [
                "Carteira(Chrys)"
            ],
            "TODOS OS ITINERANTES": ["Carteira(Itinerantes)"]
        }

        nomes_por_loja = {
            
            "Carteira(Fabiana)": ["Carteira(Fabiana)"],
            "Carteira(Felipe)": ["Carteira(Felipe)"],
            "Carteira(John)": ["Carteira(John)"],
            "Carteira(Chrys)": ["Carteira(Chrys)"],
            "Carteira(Itinerantes)": ["Carteira(Itinerantes)"],
            
            
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
                st.title("🔔 R.E.G - TAREFAS")

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

                st.subheader(f"Notificações criadas para {nome}:")
                tabela_editada = st.data_editor(
                planilha_Dados,
                hide_index=True,
                use_container_width=True
                )

                ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

                st.text(f"Quantidade de notificações criadas: {contagemA}")
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
                if st.button("🗑️ Excluir notifcação"):
                        if not ids_para_excluir:
                                st.warning("Nenhuma notificação marcada.")
                        else:
                                aba = planilha.worksheet(nome)
                                count = 0

                                for id_valor in ids_para_excluir:
                                        if excluir_por_id(id_valor, aba):
                                                count += 1

                                st.success(f"{count} notificações excluída(s) com sucesso!")
                                st.rerun()
