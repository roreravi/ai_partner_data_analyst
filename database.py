# database.py

import streamlit as st
import sqlite3
import pandas as pd
import os
from config import DB_NAME # Importamos la constante

# --- Validar DB ---

def validate_db():
    """Verifica si el archivo de la base de datos existe."""
    if not os.path.exists(DB_NAME):
        st.error(f"Error: La base de datos '{DB_NAME}' no se encontró.")
        st.stop()
        return False
    return True

# --- Funciones de DB ---

@st.cache_resource
def get_db_schema():
    """Obtiene el esquema de la base de datos y lo cachea."""
    if not validate_db():
        return None
        
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = {}
        for table_name in tables:
            table_name = table_name[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            schema[table_name] = columns
        conn.close()
        return schema
    except Exception as e:
        st.error(f"Error al cargar el esquema de la base de datos: {e}")
        return None

def execute_sql_query(query):
    """Ejecuta una consulta SQL y devuelve un DataFrame o un error."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)