# config.py

import streamlit as st
import google.generativeai as genai
import os

# --- Constantes ---
MODEL_NAME = 'gemini-2.5-pro'
DB_NAME = 'olist.sqlite'

# --- Inicialización de la API ---

def configure_gemini():
    """Configura la clave de la API de Gemini y el modelo."""
    try:
        # Intenta obtener la clave de las secrets de Streamlit o de las variables de entorno
        API_KEY = st.secrets.get('GEMINI_API_KEY') or os.getenv('api_key')
    except AttributeError:
        # Manejo para entornos que no soportan st.secrets (aunque es raro en una app desplegada)
        API_KEY = os.getenv('api_key')

    if not API_KEY:
        st.error("Error: La clave de la API de Gemini (GEMINI_API_KEY) no está configurada.")
        st.stop()

    genai.configure(api_key=API_KEY)
    
    return genai.GenerativeModel(MODEL_NAME)