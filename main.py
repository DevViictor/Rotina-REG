import streamlit as st
from TarefasCarteira import tarefas_carteira_chrys,tarefas_carteira_fabiana,tarefas_carteira_felipe,tarefas_carteira_john
from PIL import Image
from CriarTarefas import criar_page,criar_page_fabiana,criar_page_chrys,criar_page_felipe,criar_page_john
from VisualizarTarefas import visualizar_tarefas,visualizar_tarefas_fabiana, visualizar_tarefas_chrys ,visualizar_tarefas_felipe ,visualizar_tarefas_john
from TarefasProntas import modelos_prontos,modelos_prontos_fabiana, modelos_prontos_chrys, modelos_prontos_felipe, modelos_prontos_john
from GlsTarefas import tarefas_iguatemi, tarefas_barra , tarefas_bela ,tarefas_iguatemi2 ,tarefas_itinerante ,tarefas_lapa,tarefas_nort,tarefas_parela,tarefas_parque,tarefas_piedade,tarefas_ssa1,tarefas_ssa2,tarefas_boulevard
from GvTarefas import tarefas_chyrs,tarefas_fabiana,tarefas_felipe,tarefas_john
from VisualizarTarefasGv import  visualizar_tarefas_gvs
from Intinerantes import tarefas_itinerantes

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
    Visualizar_tarefas_gvs = (st.Page( visualizar_tarefas_gvs, title="R.E.G(GERAL)"))
   

    #CriarTarefas
    cadastro = st.Page(criar_page, title="📝 Criar tarefas")
    cadastro_fabiana = st.Page(criar_page_fabiana, title="📝 Criar")
    cadastro_felipe =  st.Page(criar_page_felipe, title="📝 Criar")
    cadastro_john =  st.Page(criar_page_john, title="📝 Criar")
    cadastro_chrys =  st.Page(criar_page_chrys, title="📝 Criar")

    #FElipe:

    Tarefas_carteria_felipe = st.Page(tarefas_carteira_felipe, title="R.E.G")
   

    #Fabiana 
   
    Tarefas_carteria_fabiana = st.Page(tarefas_carteira_fabiana, title="R.E.G")
    
    #Johm
    
    Tarefas_carteria_johm = st.Page(tarefas_carteira_john, title="R.E.G")
    
    
    #Chrys

    Tarefas_carteria_chrys = st.Page(tarefas_carteira_chrys, title="R.E.G")
   


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
    Tarefas_itinerantes = st.Page(tarefas_itinerantes,title="🏬 ITINERANTES")
    
    #modelos
    Visualizar_modelos = st.Page(modelos_prontos,title="📝 Modelos de tarefas")
    Visualizar_modelos_fabiana = st.Page(modelos_prontos_fabiana,title="📝 Modelos de tarefas")
    Visualizar_modelos_felipe = st.Page(modelos_prontos_felipe,title="📝 Modelos de tarefas ")
    Visualizar_modelos_john = st.Page(modelos_prontos_john,title="📝 Modelos de tarefas")
    Visualizar_modelos_chrys = st.Page(modelos_prontos_chrys,title="📝 Modelos de tarefas")

    #noficar
   

    # Menus por role
    if role == "Victor":

        menu = {
    
            "🏬 R.E.G ": [
                Visualizar_tarefas_gvs
            ],
        }
        menu2 = {
         "Tarefas": [
                cadastro,
                
                ]
        }
        
        menu3 = {
    
            "Salvamentos": [
                Visualizar_tarefas_victor,
                Visualizar_modelos,   
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
            "🏬 R.E.G LOJAS": [
                Tarefas_carteria_felipe
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
            "🏬 R.E.G. LOJAS": [
              Tarefas_carteria_fabiana
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
            "🏬 R.E.G LOJA": [
                Tarefas_carteria_johm
            ]

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
            "🏬 R.E.G LOJA": [
                Tarefas_carteria_chrys
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
    elif role in ["Iguatemi1","Iguatemi2","Bela","Norte","Paralela","Salvador1","Salvador2","Parque","Barra","Piedade","Lapa","Boulevard","Itinerantes"]:

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

