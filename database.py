# database.py

import streamlit as st
import psycopg2 # ¡Cambiado de sqlite3 a psycopg2!
import pandas as pd
import os
from config import get_postgres_config # Importamos la nueva función

# --- Lista de tablas a incluir (Filtro específico para Odoo) ---
# Se asume un prefijo "public." y se listan las tablas relevantes para el negocio (ventas, pedidos, clientes)
BUSINESS_TABLES = [
    'sale_order',         # Pedidos de Venta
    'sale_order_line',    # Líneas de Pedido
    'res_partner',        # Clientes/Contactos
    'product_product',    # Productos
    'product_template',   # Plantillas de Producto
    'account_move',       # Facturas/Movimientos Contables
    'account_move_line',  # Líneas de Factura
    'stock_picking',      # Movimientos de Inventario/Envíos
]

# --- Funciones de Conexión ---

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos PostgreSQL."""
    config = get_postgres_config()
    try:
        conn = psycopg2.connect(
            host=config['HOST'],
            database=config['DATABASE'],
            user=config['USER'],
            password=config['PASSWORD'],
            port=config['PORT']
        )
        return conn
    except Exception as e:
        st.error(f"Error de conexión a PostgreSQL: {e}")
        st.stop()
        return None

# --- Funciones de DB ---

# Ya no se necesita `validate_db` ya que la conexión fallará si no existe.

@st.cache_resource
def get_db_schema():
    """Obtiene el esquema de las tablas de negocio de PostgreSQL y lo cachea."""
    conn = get_db_connection()
    if conn is None:
        return None
        
    try:
        cursor = conn.cursor()
        schema = {}
        
        # Iteramos solo sobre las tablas relevantes definidas en BUSINESS_TABLES
        for table_name in BUSINESS_TABLES:
            # Consulta para obtener las columnas de la tabla en PostgreSQL (usando information_schema)
            sql_columns = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table_name}';
            """
            
            cursor.execute(sql_columns)
            columns_info = cursor.fetchall()
            columns = [col[0] for col in columns_info]
            
            # Solo incluimos tablas si tienen columnas
            if columns:
                schema[table_name] = columns
                
        conn.close()
        return schema
        
    except Exception as e:
        st.error(f"Error al cargar el esquema de la base de datos (PostgreSQL): {e}")
        conn.close()
        return None

def execute_sql_query(query):
    """Ejecuta una consulta SQL y devuelve un DataFrame o un error."""
    conn = get_db_connection()
    if conn is None:
        return None, "Error de conexión a la base de datos."
        
    try:
        # Usamos pd.read_sql para ejecutar y obtener el DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        # Devolvemos solo el mensaje de error para evitar exponer detalles internos al usuario final
        return None, str(e)