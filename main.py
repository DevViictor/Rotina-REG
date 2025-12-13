import streamlit as st
from GvFabiana import tarefas_adriele,tarefas_ana,tarefas_crislane,tarefas_danilo,tarefas_deniseP,tarefas_francisca,tarefas_mailan,tarefas_neide,tarefas_vanessa,tarefas_vinicius,tarefas_vitor
from GvChrys import tarefas_bruno,tarefas_camyla,tarefas_gilvania
from GvFelipe import tarefas_andressa, tarefas_denise , tarefas_diego ,tarefas_jairo ,tarefas_max, tarefas_wanderlei
from GVJohn import tarefas_alana , tarefas_carol , tarefas_diegol , tarefas_igor ,tarefas_marcus ,tarefas_rafel ,tarefas_sara 
from PIL import Image
from CriarTarefas import criar_page,criar_page_fabiana,criar_page_chrys,criar_page_felipe,criar_page_john
from RegGeralFabiana import relatorio_ssa1,relatorio_ssa2 , relatorio_bela ,relatorio_paralela ,relatorio_parque
from RegGeralFelipe import relatorio_iguatemi1,relatorio_iguatemi2,relatorio_nort 
from RegGeralChrys import relatorio_boulevard
from RegGeralJohn import relatorio_barra , relatorio_lapa ,relatorio_piedade 
from RegItirerantes import relatorio_intinerantes
from VisualizarTarefas import visualizar_tarefas,visualizar_tarefas_fabiana, visualizar_tarefas_chrys ,visualizar_tarefas_felipe ,visualizar_tarefas_john
from TarefasProntas import modelos_prontos,modelos_prontos_fabiana, modelos_prontos_chrys, modelos_prontos_felipe, modelos_prontos_john
from GlsTarefas import tarefas_iguatemi, tarefas_barra , tarefas_bela ,tarefas_iguatemi2 ,tarefas_itinerante ,tarefas_lapa,tarefas_nort,tarefas_parela,tarefas_parque,tarefas_piedade,tarefas_ssa1,tarefas_ssa2,tarefas_boulevard
from GvTarefas import tarefas_chyrs,tarefas_fabiana,tarefas_felipe,tarefas_john
from VisualizarTarefasGv import  visualizar_tarefas_gvs
from NotificaTarefas import notificar_page
from ModeloNotificacoes import notifcacao_prontas
from VisualizarNoficações import visualizar_notificacao


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
     
    #geral
    Visualizar_tarefas_gvs = (st.Page( visualizar_tarefas_gvs, title="GVS"))
   

    #CriarTarefas
    cadastro = st.Page(criar_page, title="📝 Criar tarefas")
    cadastro_fabiana = st.Page(criar_page_fabiana, title="📝 Criar")
    cadastro_felipe =  st.Page(criar_page_felipe, title="📝 Criar")
    cadastro_john =  st.Page(criar_page_john, title="📝 Criar")
    cadastro_chrys =  st.Page(criar_page_chrys, title="📝 Criar")

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

    Relatorio_itinerantes = (st.Page(relatorio_intinerantes, title="Itinerantes"))
    
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


    #Tarefas
    Visualizar_tarefas_victor = st.Page(visualizar_tarefas,title="📝 Tarefas criadas")
    Visualizar_tarefas_fabiana = st.Page(visualizar_tarefas_fabiana,title="📝 Tarefas criadas ")
    Visualizar_tarefas_felipe = st.Page(visualizar_tarefas_felipe,title="📝 Tarefas criadas ")
    Visualizar_tarefas_johon = st.Page(visualizar_tarefas_john,title="📝 Tarefas criadas ")
    Visualizar_tarefas_chrys = st.Page(visualizar_tarefas_chrys,title="📝 Tarefas criadas ")

    #TarefasGVs
    Fabiana_Tarefa = st.Page(tarefas_fabiana,title="📝 Suas tarefas")
    Felipe_Tarefa = st.Page(tarefas_felipe,title="📝 Suas tarefas")
    John_Tarefa = st.Page(tarefas_john,title="📝 Suas tarefas")
    Chrys_Tarefa = st.Page(tarefas_chyrs,title="📝 Suas tarefas")


    #tarefas_loja
    #FELIPE
    Tarefas_iguatemi = st.Page(tarefas_iguatemi,title="🏬 LOJA IGUATEMI |")
    Tarefas_iguatemi2  = st.Page(tarefas_iguatemi2,title="🏬 LOJA IGUATEMI ||")
    Tarefas_norte  = st.Page(tarefas_nort,title="🏬 LOJA NORT SHOP")
    
    #FABIANA
    Tarefas_ssa1 = st.Page(tarefas_ssa1,title="🏬 LOJA SSA1")
    Tarefas_ssa2 = st.Page(tarefas_ssa2,title="🏬 LOJA SSA2")
    Tarefas_bela = st.Page(tarefas_bela,title="🏬 LOJA BELA VISTA")
    Tarefas_parela = st.Page(tarefas_parela,title="🏬 LOJA PARARELA")
    Tarefas_parque = st.Page(tarefas_parque,title="🏬 LOJA PARQUE")

    #JHON
    Tarefas_barra = st.Page(tarefas_barra,title="🏬 LOJA BARRA")
    Tarefas_piedade = st.Page(tarefas_piedade,title="🏬 LOJA PIEDADE")
    Tarefas_lapa = st.Page(tarefas_lapa,title="🏬 LOJA LAPA")
    
    #CHRYS
    Tarefas_boulevard = st.Page(tarefas_boulevard,title="🏬 LOJA BOULEVARD")
    
    #Itinerantes
    Tarefas_itinerantes = st.Page(tarefas_itinerante,title="🏬 ITINERANTES")
    
    #modelos
    Visualizar_modelos = st.Page(modelos_prontos,title="📝 Modelos de tarefas")
    Visualizar_modelos_fabiana = st.Page(modelos_prontos_fabiana,title="📝 Modelos de tarefas")
    Visualizar_modelos_felipe = st.Page(modelos_prontos_felipe,title="📝 Modelos de tarefas ")
    Visualizar_modelos_john = st.Page(modelos_prontos_john,title="📝 Modelos de tarefas")
    Visualizar_modelos_chrys = st.Page(modelos_prontos_chrys,title="📝 Modelos de tarefas")

    #noficar
    Criar_notificacao = st.Page(notificar_page,title="🔔 Criar notificação ")
    Tarefas_notificacao = st.Page(visualizar_notificacao,title="🔔 Notificações de criadas ")
    Modelos_notificacao = st.Page(notifcacao_prontas,title="🔔 Modelos de notificação ")
    




    # Menus por role
    if role == "Victor":

        menu = {
    
            "🏬 R.E.G ": [
                Visualizar_tarefas_gvs
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
            "🏬 JOHN COITO": [
                Relatorio_barra,
                Relatorio_piedade,
                Relatorio_lapa
            ],
            "🏬 Chrys": [
                Relatorio_boulevard,
                
            ],
            "🏬 Itinerantes": [
                Relatorio_itinerantes,
                
            ],
        }
        
        menu3 = {
    
            "AÇÕES": [
                cadastro,
                Visualizar_tarefas_victor,
                Visualizar_modelos,
                Criar_notificacao,
                Tarefas_notificacao,
                Modelos_notificacao    
            ],
        }
    
    elif role == "Felipe":

        menu = {
            "🏬 R.E.G": [
                Felipe_Tarefa
                ,
            ],
        }

        menu2 = {
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

        menu3 = {
    
            "TAREFAS": [
                cadastro_felipe,
                Visualizar_tarefas_felipe,
                Visualizar_modelos_felipe,
                
            ],
        }

    elif role == "Fabiana":


        menu = {
            "🏬 R.E.G": [
                Fabiana_Tarefa
    
            ],
        }

        menu2 = {
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
        menu3 = {
    
            "TAREFAS": [
                cadastro_fabiana,
                Visualizar_tarefas_fabiana,
                Visualizar_modelos_fabiana,
                
            ],
        }
            
    
    elif role == "John":

        menu = {
            "🏬 R.E.G": [
                John_Tarefa
    
            ],
        }


        menu2 = {
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
        menu3 = {
    
            "TAREFAS": [
                cadastro_john,
                Visualizar_tarefas_johon,
                Visualizar_modelos_john,
                
            ],
        }
    
    elif role == "Chrys":

        menu = {
            "🏬 R.E.G": [
                Chrys_Tarefa
    
            ],
        }
        menu2 = {
            "🏬 Loja BOULEVARD": [
                Tarefas_Camyla,
                Tarefas_Bruno,
                Tarefas_Gilvania,
            ]
        }
        menu3 = {
    
            "TAREFAS": [
                cadastro_chrys,
                Visualizar_tarefas_chrys,
                Visualizar_modelos_chrys,
                
                
            ],
        }

    #Lojas
    elif role in ["Iguatemi1","Iguatemi2","Bela","Nort","Paralela","Salvador1","Salvador2","Parque","Barra","Piedade","Lapa","Boulevard","Itinerantes"]:

        menu = {
            "Carteira Felipe e Itinerantes": [
                Tarefas_iguatemi,
                Tarefas_iguatemi2,
                Tarefas_norte,
                Tarefas_itinerantes
            ],
        }
        menu2 = {
            " Carteira Fabiana": [
                Tarefas_ssa1,
                Tarefas_ssa2,
                Tarefas_bela,
                Tarefas_parela,
                Tarefas_parque
            ]
        }
        menu3 = {
    
            "Carteira John e Chrys": [
                Tarefas_barra,
                Tarefas_piedade,
                Tarefas_lapa,
                Tarefas_boulevard
            ],
        }


    

    # Criar navegação
   
    soma = {**menu,**menu2,**menu3}

    nav = st.navigation(soma)
    

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

