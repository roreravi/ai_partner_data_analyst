# app_modular.py

import streamlit as st
from config import configure_gemini
from database import execute_sql_query
from core_logic import initialize_chat, process_gemini_response, execute_altair_code

# --- Configuración de la Aplicación ---
st.set_page_config(page_title="🤝 Consultor de Negocios Olist (Gemini + Gráficos)", layout="wide")
st.title("🤝 Consultor de Negocios Olist")
st.caption("Pregunta sobre ventas, clientes o productos. Obtén respuestas de negocio, el SQL y, a veces, un gráfico.")

# --- Inicialización ---
model = configure_gemini()
initialize_chat(model)

# --- Interfaz y Flujo Principal ---

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar la entrada del usuario
if prompt := st.chat_input("Escribe tu pregunta de análisis de negocio..."):
    
    # 1. Mostrar pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Obtener respuesta de Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Analizando datos y generando respuesta...")
            
        # Enviar la pregunta del usuario al modelo
        response = st.session_state.chat.send_message(f"El usuario pregunta: {prompt}")
        
        # Procesar y limpiar la respuesta
        gemini_text, sql_query, altair_code = process_gemini_response(response.text)
        
        # --- A. Mostrar Explicación de Negocio (Texto Limpio) ---
        message_placeholder.markdown(gemini_text)
        
        # --- B. Procesar y Ejecutar SQL (Oculto) ---
        df_result = None
        if sql_query:
            # ¡IMPORTANTE! Eliminamos st.code(sql_query) para el perfil gerencial
            
            df_result, error = execute_sql_query(sql_query) # Usa la función del módulo database
            
            if error:
                st.error(f"❌ Error interno al procesar los datos: {error}")
            
        # --- C. Procesar Gráfico y CSV Descargable ---
        if df_result is not None and not df_result.empty:
            
            # 1. Generar Gráfico Altair (si hay código)
            if altair_code:
                st.markdown("---")
                st.markdown(f"### 📈 Visualización Clave")
                
                success, result_msg = execute_altair_code(altair_code, df_result)
                
                if not success:
                    st.warning(f"⚠️ El gráfico no pudo generarse: {result_msg}. Se muestra la opción de descargar los datos.") 
                st.markdown("---")
            
            # 2. Generar Botón de Descarga CSV
            
            # Convertir DataFrame a CSV en bytes
            csv_data = df_result.to_csv(index=False).encode('utf-8')
            
            # Crear botón de descarga
            st.download_button(
                label="⬇️ Descargar Datos de Respaldo (CSV)",
                data=csv_data,
                file_name=f'analisis_{prompt[:30].replace(" ", "_")}.csv',
                mime='text/csv',
                help='Descarga el conjunto de datos completo utilizado para generar el análisis y la tabla en formato CSV.'
            )
            
            st.markdown("---")
            
        # 3. Guardar el contenido final en el historial de Streamlit
        st.session_state.messages.append({"role": "assistant", "content": gemini_text})