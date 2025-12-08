import streamlit as st
from GvFabiana import tarefas_adriele,tarefas_ana,tarefas_crislane,tarefas_danilo,tarefas_deniseP,tarefas_francisca,tarefas_mailan,tarefas_neide,tarefas_vanessa,tarefas_vinicius,tarefas_vitor
from GvChrys import tarefas_bruno,tarefas_camyla,tarefas_gilvania
from GvFelipe import tarefas_andressa, tarefas_denise , tarefas_diego ,tarefas_jairo ,tarefas_max, tarefas_wanderlei
from SnVictor import relatorio_iguatemi1,relatorio_iguatemi2,relatorio_ssa1,relatorio_ssa2,relatorio_piedade,relatorio_paralela,relatorio_barra,relatorio_bela,relatorio_boulevard,relatorio_lapa,relatorio_parque,relatorio_nort,relatorio_intinerantes
from GVJohn import tarefas_alana , tarefas_carol , tarefas_diegol , tarefas_igor ,tarefas_marcus ,tarefas_rafel ,tarefas_sara 
from PIL import Image
from RegGeral import relatorio_fabiana_geral,relatorio_felipe_geral, relatorio_john_geral ,relatorio_chrys_geral
from CriarTarefas import criar_page

st.sidebar.image("image/Image (2).png")

icon = Image.open("image/vivo.png")

st.set_page_config(page_title="Login", page_icon=icon)


# Obter usuários do secrets
usuarios = st.secrets["usuarios"]

# Inicializar session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None


def login():
    st.title("Login")
    user = st.text_input("Usuário:")
    password = st.text_input("Senha:", type="password")

    if st.button("Entrar"):
        if user in usuarios and password == usuarios[user]["senha"]:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.role = usuarios[user]["role"]
            st.success(f"Bem-vindo, {user}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

def run_navigation():
    role = st.session_state.role

    #Victor
    Relatorio_fabiana_geral = st.Page(relatorio_fabiana_geral,title="FABIANA SACRAMENTO")
    Relatorio_felipe_geral = st.Page(relatorio_felipe_geral,title="FELIPE SILVA")
    Relatorio_johon_geral = st.Page(relatorio_john_geral,title="JOHN COITO")
    Relatorio_chrys_geral= st.Page(relatorio_chrys_geral,title="CHRYS REBOUÇAS")

    
    #CriarTarefas
    cadastro = st.Page(criar_page, title="📝 Criar tarefas")

    #Fabiana
    Relatorio_ssa1 = (st.Page(relatorio_ssa1, title="SSA |"))
    Relatorio_ssa2 = (st.Page(relatorio_ssa2, title="SSA ||"))
    Relatorio_bela = (st.Page(relatorio_bela, title="Bela vista"))
    Relatorio_paralela = (st.Page(relatorio_paralela, title="Paralela"))
    Relatorio_parque = (st.Page(relatorio_parque, title="Parque Shop"))
    
    #Felipe
    
    Relatorio_iguatemi1 = (st.Page(relatorio_iguatemi1, title="Iguatemi |"))
    Relatorio_iguatemi2 = (st.Page(relatorio_iguatemi2, title="Iguatemi ||"))
    Relatorio_norte = (st.Page(relatorio_nort, title="Norte shop"))

    #Johm
    Relatorio_barra = (st.Page(relatorio_barra, title="Barra"))
    Relatorio_piedade = (st.Page(relatorio_piedade, title="Piedade"))
    Relatorio_lapa = (st.Page(relatorio_lapa, title="Lapa"))
    
    #Chrys

    Relatorio_boulevard = (st.Page(relatorio_boulevard, title="Boulevard"))

    #Intinerantes

    Relatorio_initinerantes = (st.Page(relatorio_intinerantes, title="Intinerantes"))
    
    #FElipe:
    
    #IGUATEMI 1
    Tarefas_Denise = st.Page(tarefas_denise, title="Denise")
    Tarefas_max = st.Page(tarefas_max, title="Max")
    #IGUATEMI 1
    Tarefas_diego = st.Page(tarefas_diego, title="Diego")
    Tarefas_andressa= st.Page(tarefas_andressa, title="Andressa")
    #SALVADORNORTH
    Tarefas_jairo= st.Page(tarefas_jairo, title="Jairo")
    Tarefas_wanderlei= st.Page(tarefas_wanderlei, title="Wanderlei")

    #Fabiana 

    #SSA1
    Tarefas_Ana = st.Page(tarefas_ana,title="Ana")
    Tarefas_francisca = st.Page(tarefas_francisca,title="Francisca")
    Tarefas_vinicius = st.Page(tarefas_vinicius,title="Vinicius")
    #SSA2
    Tarefas_mailan = st.Page(tarefas_mailan,title="Mailan")
    Tarefas_vitor = st.Page(tarefas_vitor,title="Vitor")
    #BELA
    Tarefas_vanessa = st.Page(tarefas_vanessa,title="Vanessa")
    Tarefas_danilo = st.Page(tarefas_danilo,title="Danilo")
    #Parela
    Tarefas_crislane = st.Page(tarefas_crislane,title="Crislane")
    Tarefas_neide = st.Page(tarefas_neide,title="Neide")
    #Parque
    Tarefas_adriele = st.Page(tarefas_adriele,title="Adriele")
    Tarefas_deniseP = st.Page(tarefas_deniseP,title="Denise")

    #Johm
    
    #Barra
    Tarefas_alana = st.Page(tarefas_alana,title="Alana")
    Tarefas_carol = st.Page(tarefas_carol,title="Carol")
    Tarefas_igor = st.Page(tarefas_igor,title="Igor")
    #Piedade
    Tarefas_diegol = st.Page(tarefas_diegol,title="Diego")
    Tarefas_marcus = st.Page(tarefas_marcus,title="Marcus")
    #Lapa
    Tarefas_Rafeael = st.Page(tarefas_rafel,title="Rafael")
    Tarefas_Sara = st.Page(tarefas_sara,title="Sara")
    
    #Chrys

    #Boulevard
    Tarefas_Camyla = st.Page(tarefas_camyla,title="Camyla")
    Tarefas_Bruno = st.Page(tarefas_bruno,title="Bruno")
    Tarefas_Gilvania = st.Page(tarefas_gilvania,title="Gilvania")


    #Relatorio GERAL


    # Menus por role
    if role == "Victor":
        
        menu = {
            "R.E.G": [
                Relatorio_fabiana_geral,
                Relatorio_felipe_geral,
                Relatorio_johon_geral,
                Relatorio_chrys_geral

            ],
            
        }

        menu2 = {
    
            "🏬 FABIANA SACRAMENTO ": [
                Relatorio_ssa1,
                Relatorio_ssa2,
                Relatorio_bela,
                Relatorio_paralela,
                Relatorio_parque
            ],

            "🏬 FELIPE SILVA ": [
                Relatorio_iguatemi1,
                Relatorio_iguatemi2,
                Relatorio_norte
            ],
            "🏬 JOHN COITO ": [
                Relatorio_barra,
                Relatorio_piedade,
                Relatorio_lapa
            ],
            "🏬 CHRYS REBOUÇAS ": [
                Relatorio_boulevard,
            ],
            "🏬 INTINERANTES ": [
                Relatorio_initinerantes,
            ]

        }
    
    elif role == "Felipe":

        menu = {
            "🏬 Loja Iguatemi |": [
                Tarefas_Denise,
                Tarefas_max
            ],
            "🏬 Loja Iguatemi ||": [
                Tarefas_andressa,
                Tarefas_diego
            ],
             "🏬 Nort Shop": [
                Tarefas_jairo,
                Tarefas_wanderlei
            ],
            
        }

    elif role == "Fabiana":
        menu = {
            "🏬 Loja SSA |": [
                Tarefas_Ana,
                Tarefas_francisca,
                Tarefas_vinicius,
            ],
            "🏬 Loja SSA ||": [
                Tarefas_mailan,
                Tarefas_vitor,
            ],
            "🏬 Loja Bela Vista ": [
                Tarefas_danilo,
                Tarefas_vanessa,
            ],
             "🏬 Loja Paralela": [
                Tarefas_crislane,
                Tarefas_neide,
            ],
             "🏬 Loja Paque Shop": [
                Tarefas_adriele,
                Tarefas_deniseP,
            ],
        }
            
    
    elif role == "Johm":
        menu = {
            "🏬 Loja Barra": [
                Tarefas_alana,
                Tarefas_carol,
                Tarefas_igor,
            ],
            "🏬 Loja Piedade": [
                Tarefas_diegol,
                Tarefas_marcus,
            ],
            "🏬 Loja Lapa": [
                Tarefas_Sara,
                Tarefas_Rafeael,
                
            ],

        }
    
    elif role == "Chrys":
        menu = {
            "🏬 Loja BOULEVARD": [
                Tarefas_Camyla,
                Tarefas_Bruno,
                Tarefas_Gilvania,
            ]
        }
    
    menu3 = {
            "Tarefas": [
                cadastro

            ],
            
        }
    

    # Criar navegação
   
    menu_total = {**menu,**menu2,**menu3}

    nav = st.navigation(menu_total)

    

    # Sidebar com usuário
    st.sidebar.write(f"👤 Usuário: **{st.session_state.user}**")
    st.sidebar.button("Sair", on_click=logout)

    # Rodar página selecionada
    nav.run()
    

# -----------------------------------------
# EXECUÇÃO PRINCIPAL
# -----------------------------------------
if not st.session_state.logged_in:
    login()
else:
    run_navigation()

