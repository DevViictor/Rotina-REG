import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image


def modelos_prontos():
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
            aba = planilha.worksheet("ModelosTarefas")
            dados = aba.get_all_records()
            return pd.DataFrame(dados)

    # ---------------------------
    # CARREGAR E FILTRAR DADOS
    # ---------------------------
    planilha_Dados = carregar_pedidos()

    colunas_desejadas = ["ID", "Título", "Descrição da tarefa","Hora inicial","Hora final" ,"Data","Tipo de recorrência"]
    planilha_Dados = planilha_Dados[colunas_desejadas]
    
    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="Tarefas", page_icon=icon, layout="wide")

    image_logo = Image.open("image/Image (2).png")

    cola, colb, colc = st.columns([4,1,1])

    
    with colc:
                st.image(image_logo)

    with cola:
                st.title("📝 R.E.G - MODELOS")
    # ---------------------------
    # CHECKBOX PARA EXCLUSÃO
    # ---------------------------
    planilha_Dados["Excluir"] = False

    st.write("Modelos de tarefas salvos: ")
    tabela_editada = st.data_editor(
        planilha_Dados,
        hide_index=True,
        use_container_width=True
    )

    ids_para_excluir = tabela_editada[tabela_editada["Excluir"] == True]["ID"].tolist()

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
                    aba = planilha.worksheet("ModelosTarefas")
                    count = 0

                    for id_valor in ids_para_excluir:
                            if excluir_por_id(id_valor, aba):
                                    count += 1

                    st.success(f"{count} tarefa(s) excluída(s) com sucesso!")
                    st.rerun()
