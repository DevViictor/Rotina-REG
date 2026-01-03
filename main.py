import streamlit as st
from TarefasCarteira import tarefas_carteira_chrys,tarefas_carteira_fabiana,tarefas_carteira_felipe,tarefas_carteira_john
from PIL import Image
from CriarTarefas import criar_page
from VisualizarTarefas import visualizar_tarefas
from TarefasProntas import modelos_prontos
from GlsTarefas import  tarefas_barra_abertura , tarefas_barra_fechamento , tarefas_barra_intermedio ,tarefas_bela_abertura,tarefas_bela_fechamento,tarefas_boulevard_abertura,tarefas_boulevard_fechamento,tarefas_boulevard_intermedio,tarefas_iguatemi2_abertura,tarefas_iguatemi2_fechamento,tarefas_iguatemi_abertura,tarefas_iguatemi_fechamento,tarefas_lapa_abertura,tarefas_lapa_fechamento,tarefas_nort_abertura,tarefas_nort_fechamento,tarefas_parela_abertura,tarefas_parela_fechamento,tarefas_parque_abertura,tarefas_parque_fechamento,tarefas_piedade_abertura,tarefas_ssa1_abertura,tarefas_ssa1_fechamento,tarefas_ssa1_intermedio,tarefas_ssa2_abertura,tarefas_ssa2_fechamento,tarefas_piedade_fechamento,tarefas_itinerante_lazaro,tarefas_itinerante_lee,tarefas_itinerante_marcus,tarefas_diasdavila_abertura
from VisualizarTarefasGv import  visualizar_tarefas_gvs, visualizar_tarefas_fechamento , visualizar_tarefas_intermedio,visualizar_tarefas_itinerantes

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
    Visualizar_tarefas_gvs = (st.Page( visualizar_tarefas_gvs, title="R.E.G(ABERTURA)"))
    Visualizar_tarefas_intermedio = (st.Page( visualizar_tarefas_intermedio, title="R.E.G(INTERMEDIO)"))
    Visualizar_tarefas_fechamento = (st.Page( visualizar_tarefas_fechamento, title="R.E.G(FECHAMENTO)"))
   

    #CriarTarefas
    cadastro = st.Page(criar_page, title="📝 Criar tarefas")


    #FElipe:

    Tarefas_carteria_felipe = st.Page(tarefas_carteira_felipe, title="LOJAS")


   

    #Fabiana 
   
    Tarefas_carteria_fabiana = st.Page(tarefas_carteira_fabiana, title="LOJAS")
    
    #Johm
    
    Tarefas_carteria_johm = st.Page(tarefas_carteira_john, title="LOJAS")
    
    
    #Chrys

    Tarefas_carteria_chrys = st.Page(tarefas_carteira_chrys, title="LOJAS")
   

    #Tarefas
    Visualizar_tarefas_victor = st.Page(visualizar_tarefas,title="📝 Tarefas criadas")
  
    #tarefas_loja
    #FELIPE
    Tarefas_iguatemi_abertura = st.Page(tarefas_iguatemi_abertura,title="🏬 LOJA IGUATEMI | (ABERTURA)")
    Tarefas_iguatemi_fechamento  = st.Page(tarefas_iguatemi_fechamento,title="🏬 LOJA IGUATEMI | (FECHAMENTO)")

    Tarefas_iguatemi2_abertura  = st.Page(tarefas_iguatemi2_abertura,title="🏬 LOJA IGUATEMI || (ABERTURA)")
    Tarefas_iguatemi2_fechamento  = st.Page(tarefas_iguatemi2_fechamento,title="🏬 LOJA IGUATEMI || (FECHAMENTO)")

    Tarefas_norte_abertura  = st.Page(tarefas_nort_abertura,title="🏬 LOJA NORT SHOP (ABERTURA)")
    Tarefas_norte_fechamento  = st.Page(tarefas_nort_fechamento,title="🏬 LOJA NORT SHOP (FECHAMENTO)")
    
    
    #FABIANA
    Tarefas_ssa1_abertura = st.Page(tarefas_ssa1_abertura,title="🏬 LOJA SSA1 (ABERTURA)")
    Tarefas_ssa1_intermedio = st.Page(tarefas_ssa1_intermedio,title="🏬 LOJA SSA1 (INTERMEDIO)")
    Tarefas_ssa1_fechamento = st.Page(tarefas_ssa1_fechamento,title="🏬 LOJA SSA1 (FECHAMENTO)" )
    

    Tarefas_ssa2_abertura = st.Page(tarefas_ssa2_abertura,title="🏬 LOJA SSA2 (ABERTURA)" )
    Tarefas_ssa2_fechamento= st.Page(tarefas_ssa2_fechamento,title="🏬 LOJA SSA2 (FECHAMENTO)" ) 

    Tarefas_bela_abertura = st.Page(tarefas_bela_abertura,title="🏬 LOJA BELA VISTA (ABERTURA)")
    Tarefas_bela_fechamento = st.Page(tarefas_bela_fechamento,title="🏬 LOJA BELA VISTA (FECHAMENTO)")

    Tarefas_parela_abertura = st.Page(tarefas_parela_abertura,title="🏬 LOJA PARARELA (ABERTURA)")
    Tarefas_parela_fechamento = st.Page(tarefas_parela_fechamento,title="🏬 LOJA PARARELA (FECHAMENTO)")

    Tarefas_parque_abertura = st.Page(tarefas_parque_abertura,title="🏬 LOJA PARQUE (ABERTURA)")
    Tarefas_parque_fechamento = st.Page(tarefas_parque_fechamento,title="🏬 LOJA PARQUE (FECHAMENTO)")
    
    Tarefas_davila_abertura = st.Page(tarefas_diasdavila_abertura,title="🏬 LOJA DIAS DAVILA(ABERTURA)")

    #JHON
    Tarefas_barra_abertura = st.Page(tarefas_barra_abertura,title="🏬 LOJA BARRA (ABERTURA)")
    Tarefas_barra_intermedio = st.Page(tarefas_barra_intermedio,title="🏬 LOJA BARRA (INTERMEDIO)")
    Tarefas_barra_fechamento = st.Page(tarefas_barra_fechamento,title="🏬 LOJA BARRA (FECHAMENTO)")

    Tarefas_piedade_abertura = st.Page(tarefas_piedade_abertura,title="🏬 LOJA PIEDADE (ABERTURA)")
    Tarefas_piedade_fechamento = st.Page(tarefas_piedade_fechamento,title="🏬 LOJA PIEDADE (FECHAMENTO)")

    Tarefas_lapa_abertura = st.Page(tarefas_lapa_abertura,title="🏬 LOJA LAPA (ABERTURA)")
    Tarefas_lapa_fechamento = st.Page(tarefas_lapa_fechamento,title="🏬 LOJA LAPA (FECHAMENTO)")
    

    #CHRYS
    Tarefas_boulevard_abertura = st.Page(tarefas_boulevard_abertura,title="🏬 LOJA BOULEVARD (ABERTURA)")
    Tarefas_boulevard_intermedio = st.Page(tarefas_boulevard_intermedio,title="🏬 LOJA BOULEVARD (INTERMEDIO)")
    Tarefas_boulevard_fechamentio = st.Page(tarefas_boulevard_fechamento,title="🏬 LOJA BOULEVARD (FECHAMENTO)")
    
    #Itinerantes victor
    Visualizar_tarefas_itinerantes = st.Page(visualizar_tarefas_itinerantes,title="R.E.G (ITINERANTES)")

    # PESSAOS
    Visualizar_tarefas_itinerantesL = st.Page(tarefas_itinerante_lee,title="🏬 LEE")
    Visualizar_tarefas_itinerantesM = st.Page(tarefas_itinerante_marcus,title="🏬 MARCUS")
    Visualizar_tarefas_itinerantesL2 = st.Page(tarefas_itinerante_lazaro,title="🏬 LAZARO")     

    
    #modelos
    Visualizar_modelos = st.Page(modelos_prontos,title="📝 Modelos de tarefas")
    

    # Menus por role
    if role == "Victor":

        menu = {
    
            "🏬 R.E.G ": [
                Visualizar_tarefas_gvs,
                Visualizar_tarefas_intermedio,
                Visualizar_tarefas_fechamento,
                Visualizar_tarefas_itinerantes
                
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
    
   
    
    #Lojas
    elif role in ["Iguatemi1","Iguatemi2","Bela","Norte","Paralela","Salvador1","Salvador2","Parque","Barra","Piedade","Lapa","Boulevard","Itinerantes","Davila","Admin"]:

        menu = {
            "GLS ABERTURA": [
                Tarefas_ssa1_abertura,
                Tarefas_ssa2_abertura,
                Tarefas_bela_abertura,
                Tarefas_parela_abertura,
                Tarefas_parque_abertura,
                Tarefas_iguatemi_abertura,
                Tarefas_iguatemi2_abertura,
                Tarefas_norte_abertura,
                Tarefas_barra_abertura,
                Tarefas_piedade_abertura,
                Tarefas_lapa_abertura,
                Tarefas_boulevard_abertura,
                Tarefas_davila_abertura]
        }
        menu2 = {
            " GLS INTERMEDIO": [
                Tarefas_ssa1_intermedio,
                Tarefas_barra_intermedio,
                Tarefas_boulevard_intermedio,
    
            ]
        }
        menu3 = {
    
            "GLS FECHAMENTO": [
               Tarefas_ssa1_fechamento,
                Tarefas_ssa2_fechamento,
                Tarefas_bela_fechamento,
                Tarefas_parela_fechamento,
                Tarefas_parque_fechamento,
                Tarefas_iguatemi_fechamento,
                Tarefas_iguatemi2_fechamento,
                Tarefas_norte_fechamento,
                Tarefas_barra_fechamento,
                Tarefas_piedade_fechamento,
                Tarefas_lapa_fechamento,
                Tarefas_boulevard_fechamentio,
                #falta piedade
            ],
        }

    if role == "Itinerantes":

        menu = {
    
            "🏬 R.E.G (LEE) ": [
              Visualizar_tarefas_itinerantesL
            ],
        }
        menu2 = {
         "🏬 R.E.G (MARCUS)": [
                Visualizar_tarefas_itinerantesM
                ]
        }
        
        menu3 = {
    
            "🏬 R.E.G (Lázaro)": [
                Visualizar_tarefas_itinerantesL2
            ],
        }

    if role == "Felipe":

        menu = {
    
            "R.E.G(ABERTURA) ": [
              Tarefas_carteria_felipe
            ],
        }
        menu2 = {
            "R.E.G (FECHAMENTO)": [
                ]
        }
        
        menu3 = {
    
            "🏬 R.E.G (Lázaro)": [
            ],
        }
    
    if role == "Fabiana":

        menu = {
    
            "R.E.G(ABERTURA) ": [
              Tarefas_carteria_fabiana
            ],
        }
        menu2 = {
            "R.E.G (INTERMEDIO)": [
                
                ]
        }
        
        menu3 = {
    
            "R.E.G (FECHAMENTO)": [
                
            ],
        }

    if role == "John":

        menu = {
    
            "R.E.G(ABERTURA) ": [
              Tarefas_carteria_johm
            ],
        }
        menu2 = {
            "R.E.G (INTERMEDIO)": [
                
                ]
        }
        
        menu3 = {
    
            "R.E.G (FECHAMENTO)": [
                
            ],
        }
    

    if role == "Chrys":

        menu = {
    
            "R.E.G(ABERTURA) ": [
              Tarefas_carteria_chrys
            ],
        }
        menu2 = {
            "R.E.G (INTERMEDIO)": [
                
                ]
        }
        
        menu3 = {
    
            "R.E.G (FECHAMENTO)": [
                
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

