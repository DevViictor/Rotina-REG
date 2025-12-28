import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image
from datetime import datetime



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



# =========================================================
# ===================== GLS ABERTURA ======================
# =========================================================
def visualizar_tarefas_gvs():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    
    image_logo = Image.open("image/Image (2).png")
    cola, colb, colc = st.columns([4, 1, 1])
    with colc:
        st.image(image_logo)
    with cola:
        st.title("📝 R.E.G - TAREFAS")


    gvs = ["GLS DA CARTEIRA DE FABIANA",
            "GLS DA CARTEIRA DE FELIPE",
            "GLS DA CARTEIRA DE JOHN",
            "GLS DA CARTEIRA DE CHRYS"
            ]
    

    col1, col2 = st.columns(2)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    
    with col2:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )
  


    aba = planilha.worksheet("GLS(ABERTURA)")
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    aba2 = planilha_exc.worksheet("EXECUCOES(ABERTURA)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())


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



    #Fabiana
    
    contagemT = planilha_Dados["Título"].count()

    contagemCris = planilha_filtrada["GL"].value_counts().get("Crislaine",0)

    contagemDeniseP = planilha_filtrada["GL"].value_counts().get("Denise_Parque",0)

    contagemMercia = planilha_filtrada["GL"].value_counts().get("Mércia",0)

    contagemMaise = planilha_filtrada["GL"].value_counts().get("Maise",0)

    contagemVitor = planilha_filtrada["GL"].value_counts().get("Vitor",0)


    #Felipe

    contagemT = planilha_Dados["Título"].count()

    contagemMax = planilha_filtrada["GL"].value_counts().get("Max",0)

    contagemJairo = planilha_filtrada["GL"].value_counts().get("Jairo",0)

    contagemAndressa = planilha_filtrada["GL"].value_counts().get("Andressa",0)


    #John

    contagemT = planilha_Dados["Título"].count()

    contagemCarol = planilha_filtrada["GL"].value_counts().get("Carol",0)

    contagemDiego = planilha_filtrada["GL"].value_counts().get("Diego",0)

    contagemRafael = planilha_filtrada["GL"].value_counts().get("Rafael",0)


    #Chrys

    contagemT = planilha_Dados["Título"].count()

    contagemBruno = planilha_filtrada["GL"].value_counts().get("Bruno",0)


    conclusao_tarefas_fabiana = pd.DataFrame({
    "GLS(ABERTURA)": [
       
        "Crislaine",
        "Denise",
        "Mércia",
        "Vitor",
        "Maise",

        "Tarefas criadas"
    ],
    "Conclusão": [
        contagemCris,
        contagemDeniseP,
        contagemMercia,
        contagemVitor,
        contagemMaise,
        contagemT
    ]
    
    })


    conclusao_tarefas_felipe = pd.DataFrame({
    "GLS(ABERTURA)": [
        "Andressa",
        "Jairo",
        "Max",
        "Total de tarefas criadas"
    ],
    "Conclusão": [
        contagemAndressa,
        contagemJairo,
        contagemMax,
        contagemT
    ]
    })


    conclusao_tarefas_john = pd.DataFrame({
    "GLS(ABERTURA)": [
        "Carol",
        "Diego",
        "Rafael",
        "Total de tarefas criadas"
    ],
    "Conclusão": [
        contagemCarol,
        contagemDiego,
        contagemRafael,
        contagemT
    ]
    })


    conclusao_tarefas_chrys = pd.DataFrame({
    "GLS": [
        "Bruno",
        "Total de tarefas criadas"
    ],
    "Conclusão": [
        contagemBruno,
        contagemT
    ]
    })


    #Visualizar as tarefas

    if carteira == "GLS DA CARTEIRA DE FABIANA":
        st.write(conclusao_tarefas_fabiana)

    elif carteira == "GLS DA CARTEIRA DE FELIPE":
        st.write(conclusao_tarefas_felipe)

    elif carteira == "GLS DA CARTEIRA DE JOHN":
        st.write(conclusao_tarefas_john)

    elif carteira == "GLS DA CARTEIRA DE CHRYS":
        st.write(conclusao_tarefas_chrys)
   
   


def visualizar_tarefas_intermedio():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G - GVS", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

    
    gvs = ["GLS(INTERMEDIO)",
            ]
    

    col1, col2 = st.columns(2)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    
    with col2:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )
  


    aba = planilha.worksheet("GLS(INTERMEDIO)")
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    aba2 = planilha_exc.worksheet("EXECUCOES(INTERMEDIO)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())


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



    
    
    contagemT = planilha_Dados["Título"].count()

    contagemFran = planilha_filtrada["GL"].value_counts().get("Francisca",0)


    #John

    contagemAlana = planilha_filtrada["GL"].value_counts().get("Alana",0)



    #Chrys

    contagemCamyla = planilha_filtrada["GL"].value_counts().get("Camyla",0)


    conclusao_tarefas_fabiana = pd.DataFrame({
    "GLS(INTERMEDIO)": [
       
        "Francisca(SSA|)",
        "Alana(BARRA)",
        "Camyla(BOULEVARD)",

        "Tarefas criadas"
    ],
    "Conclusão": [
        contagemFran,
        contagemAlana,
        contagemCamyla,
        contagemT
    ]
    
    })

    if carteira == "GLS(INTERMEDIO)":
        st.write(conclusao_tarefas_fabiana)

   
   

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
    

    col1, col2 = st.columns(2)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    
    with col2:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )
  


    aba = planilha.worksheet("GLS(FECHAMENTO)")
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    aba2 = planilha_exc.worksheet("EXECUCOES(FECHAMENTO)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())


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



    #Fabiana
    
    contagemT = planilha_Dados["Título"].count()

    contagemVini = planilha_filtrada["GL"].value_counts().get("Vinicius",0)

    contagemMai = planilha_filtrada["GL"].value_counts().get("Mailan",0)

    contagemVanessa = planilha_filtrada["GL"].value_counts().get("Vanessa",0)

    contagemNeide = planilha_filtrada["GL"].value_counts().get("Neide",0)

    contagemAdrielle = planilha_filtrada["GL"].value_counts().get("Adriele",0)


    #Felipe

    contagemT = planilha_Dados["Título"].count()

    contagemDenise = planilha_filtrada["GL"].value_counts().get("Denise",0)

    contagemDiego = planilha_filtrada["GL"].value_counts().get("Diego",0)

    contagemWanerdeli = planilha_filtrada["GL"].value_counts().get("Wanderlei",0)


    #John

    contagemT = planilha_Dados["Título"].count()

    contagemIgor = planilha_filtrada["GL"].value_counts().get("Igor",0)

    contagemMarcus = planilha_filtrada["GL"].value_counts().get("Marcusl",0)

    contagemSara = planilha_filtrada["GL"].value_counts().get("Sara",0)


    #Chrys

    contagemT = planilha_Dados["Título"].count()

    contagemGilvania = planilha_filtrada["GL"].value_counts().get("Gilvania",0)


    conclusao_tarefas_fabiana = pd.DataFrame({
    "GLS(FECHAMENTO)": [
       
        "Vinicius",
        "Mailan",
        "Vanessa",
        "Neide",
        "Adriele",
        "Tarefas criadas"
    ],
    "Conclusão": [
        contagemVini,
        contagemMai,
        contagemVanessa,
        contagemNeide,
        contagemAdrielle,
        contagemT
    ]
    
    })


    conclusao_tarefas_felipe = pd.DataFrame({
    "GLS(FECHAMENTO)": [
        "Denise",
        "Diego",
        "Wanderlei",
        "Total de tarefas criadas"
    ],
    "Conclusão": [
        contagemDenise,
        contagemDiego,
        contagemWanerdeli,
        contagemT
    ]
    })

    conclusao_tarefas_john = pd.DataFrame({
    "GLS(FECHAMENTO)": [
        "Igor",
        "Marcus",
        "Sara",
        "Total de tarefas criadas"
    ],
    "Conclusão": [
        contagemIgor,
        contagemMarcus,
        contagemSara,
        contagemT
    ]
    })


    conclusao_tarefas_chrys = pd.DataFrame({
    "GLS(FECHAMENTO)": [
        "Gilvania",
        "Total de tarefas criadas"
    ],
    "Conclusão": [
        contagemGilvania,
        contagemT
    ]
    })


    #Visualizar as tarefas

    if carteira == "GLS DA CARTEIRA DE FABIANA":
        st.write(conclusao_tarefas_fabiana)

    elif carteira == "GLS DA CARTEIRA DE FELIPE":
        st.write(conclusao_tarefas_felipe)

    elif carteira == "GLS DA CARTEIRA DE JOHN":
        st.write(conclusao_tarefas_john)

    elif carteira == "GLS DA CARTEIRA DE CHRYS":
        st.write(conclusao_tarefas_chrys)
   

def visualizar_tarefas_itinerantes():

    icon = Image.open("image/vivo.png")
    st.set_page_config(page_title="R.E.G - ITINERANTES", page_icon=icon, layout="wide")

    if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()

     
    gvs = ["ITINERANTES",
            ]
    

    col1, col2 = st.columns(2)
    with col1:
        carteira = st.selectbox("Selecione a carteira:", gvs)
    
    with col2:
        data_selecionada = st.date_input(
            "Selecione o período:", value=(datetime.today(), datetime.today())
        )
  


    aba = planilha.worksheet("ITINERANTES")
    planilha_Dados = pd.DataFrame(aba.get_all_records())

    aba2 = planilha_exc.worksheet("REGISTROS(ITINERANTES)")
    planilha_Dados2 = pd.DataFrame(aba2.get_all_records())


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



    
    
    contagemT = planilha_Dados["Título"].count()

    contagemLee = planilha_filtrada["GL"].value_counts().get("Lee",0)
    contagemMarcus = planilha_filtrada["GL"].value_counts().get("Marcus",0)
    contagemLázaro = planilha_filtrada["GL"].value_counts().get("Lázaro",0)


    #John

   

    conclusao_tarefas_itinerantes = pd.DataFrame({
    "ITINERANTES": [
       
        "Lee",
        "Marcus",
        "Lázaro",

        "Tarefas criadas"
    ],
    "Conclusão": [
        contagemLee,
        contagemMarcus,
        contagemLázaro,
        contagemT
    ]
    
    })

    if carteira == "ITINERANTES":
        st.write(conclusao_tarefas_itinerantes)

   