# core_logic.py

import streamlit as st
import re
import altair as alt
import pandas as pd
# Importamos la función de esquema de DB y las definiciones del agente/prompt
from database import get_db_schema 
from prompts import get_analyst_role, INITIAL_GREETING 


# --- Inicialización del Chat ---

def initialize_chat(model):
    """Inicializa la sesión de chat con el rol del agente."""
    if "chat" not in st.session_state:
        # 1. Obtener el esquema de la DB
        db_schema = get_db_schema()
        if db_schema is None:
            st.stop()
        
        # 2. Generar el rol (System Prompt)
        analyst_role = get_analyst_role(db_schema)
        
        # 3. Iniciar el chat
        try:
            st.session_state.chat = model.start_chat(history=[
                {"role": "user", "parts": [analyst_role]},
                {"role": "model", "parts": [INITIAL_GREETING]},
            ])
            # Inicializar historial de mensajes de Streamlit
            if "messages" not in st.session_state:
                 st.session_state.messages = [] 
            st.session_state.messages.append({"role": "assistant", "content": INITIAL_GREETING})
        except Exception as e:
            st.error(f"Error al inicializar el modelo Gemini: {e}")
            st.stop()

# --- Funciones de Detección y Ejecución ---

def extract_code(text, start_tag):
    """Extrae código de un bloque específico (ej: ```sql o ```python_altair)."""
    pattern = rf"```{re.escape(start_tag)}\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def execute_altair_code(code, df_result):
    """Ejecuta el código de Altair en un entorno seguro y devuelve el resultado."""
    exec_globals = {
        'pd': pd, 
        'alt': alt, 
        'st': st, 
        'df_result': df_result # El DataFrame de resultado SQL
    }
    
    try:
        exec(code, exec_globals)
        return True, "Gráfico generado exitosamente."
    except Exception as e:
        return False, f"Error al generar el gráfico de Altair: {e}"

def process_gemini_response(response_text):
    """Procesa la respuesta de Gemini, extrayendo código y limpiando el texto."""
    
    # 1. Extraer códigos
    # Usamos la función local extract_code
    altair_code = extract_code(response_text, "python_altair")
    sql_query = extract_code(response_text, "sql")

    # 2. Limpiar el texto de explicación
    gemini_text = response_text
    # Elimina los bloques de código para que el texto de explicación sea limpio
    if altair_code:
        gemini_text = re.sub(r"```python_altair.*?```", "", gemini_text, flags=re.DOTALL).strip()
    if sql_query:
        gemini_text = re.sub(r"```sql.*?```", "", gemini_text, flags=re.DOTALL).strip()
        
    return gemini_text, sql_query, altair_code