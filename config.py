# config.py

import streamlit as st
import google.generativeai as genai
import os
import psycopg2 # ¡Nuevo! Necesitas el driver de PostgreSQL

# --- Constantes ---
MODEL_NAME = 'gemini-2.5-pro'
# DB_NAME = 'olist.sqlite' # ¡Eliminamos la constante de SQLite!

# --- Constantes de PostgreSQL ---
# Las credenciales deben cargarse de Streamlit secrets o de variables de entorno
def get_postgres_config():
    """Obtiene la configuración de PostgreSQL de st.secrets o variables de entorno."""
    # Usamos .get() con un valor por defecto para evitar errores si la clave no existe
    config = {
        'HOST': st.secrets.get('PG_HOST') or os.getenv('PG_HOST'),
        'DATABASE': st.secrets.get('PG_DATABASE') or os.getenv('PG_DATABASE'),
        'USER': st.secrets.get('PG_USER') or os.getenv('PG_USER'),
        'PASSWORD': st.secrets.get('PG_PASSWORD') or os.getenv('PG_PASSWORD'),
        'PORT': st.secrets.get('PG_PORT') or os.getenv('PG_PORT', 5432) # Default de PG es 5432
    }
    
    if not all(config.values()):
        st.error("Error: Faltan credenciales de PostgreSQL (PG_HOST, PG_DATABASE, PG_USER, PG_PASSWORD).")
        st.stop()
        
    return config

# --- Inicialización de la API (Sin cambios) ---

def configure_gemini():
    """Configura la clave de la API de Gemini y el modelo."""
    try:
        API_KEY = st.secrets.get('GEMINI_API_KEY') or os.getenv('api_key')
    except AttributeError:
        API_KEY = os.getenv('api_key')

    if not API_KEY:
        st.error("Error: La clave de la API de Gemini (GEMINI_API_KEY) no está configurada.")
        st.stop()

    genai.configure(api_key=API_KEY)
    
    return genai.GenerativeModel(MODEL_NAME)