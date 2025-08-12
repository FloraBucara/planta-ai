import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada"""
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Botones verticales
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # BOTÓN 1: Subir archivo - CON NUEVO ESTILO VERDE ESTÁNDAR
        if st.button(
            "📁 Subir imagen desde mi dispositivo",
            use_container_width=True,
            type="primary",
            key="btn_upload"  # ← KEY PARA ESTILO VERDE ESTÁNDAR
        ):
            st.session_state.metodo_seleccionado = "archivo"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)  # Espacio
        
        # BOTÓN 2: Tomar foto - CON NUEVO ESTILO VERDE ESTÁNDAR
        if st.button(
            "📷 Tomar foto con la cámara",
            use_container_width=True,
            type="primary",
            key="btn_camera"  # ← KEY PARA ESTILO VERDE ESTÁNDAR
        ):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()