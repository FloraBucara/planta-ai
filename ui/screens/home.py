import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - MEJORADA SIN ESPACIOS"""
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    # Título centrado - SIN ESPACIO EXTRA
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="margin-bottom: 0;">📸 ¿Cómo quieres agregar tu planta?</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones centrados - SIN ESPACIOS EXTRA
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botón 1: Subir archivo
        if st.button(
            "📁 Subir imagen desde mi dispositivo",
            use_container_width=True,
            type="primary",
            key="btn_upload"
        ):
            st.session_state.metodo_seleccionado = "archivo"
            st.rerun()
        
        # Pequeño espaciado entre botones
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # Botón 2: Tomar foto
        if st.button(
            "📷 Tomar foto con la cámara",
            use_container_width=True,
            type="primary",
            key="btn_camera"
        ):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()