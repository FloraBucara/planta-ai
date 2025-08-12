# ui/screens/home.py - CON BOTONES BUBBLY
import streamlit as st
from ui.bubbly_buttons import boton_subir_imagen, boton_tomar_foto

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - CON BOTONES BUBBLY"""
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Botones con efecto bubbly
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botón 1: Subir archivo con efecto bubbly
        if boton_subir_imagen("btn_upload_bubbly"):
            st.session_state.metodo_seleccionado = "archivo"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)  # Espacio
        
        # Botón 2: Tomar foto con efecto bubbly
        if boton_tomar_foto("btn_camera_bubbly"):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()