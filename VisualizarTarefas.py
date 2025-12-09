import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from PIL import Image

if "role" not in st.session_state or st.session_state.role != "Victor":
        st.error("⚠️ Acesso negado!")
        st.stop()


