import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - VERSIÓN LIMPIA SIN SUPERPOSICIONES"""
    
    # Ocultar elementos de Streamlit que causan conflictos
    st.markdown("""
    <style>
        /* Ocultar elementos que causan superposición */
        .stDeployButton { display: none !important; }
        .stDecoration { display: none !important; }
        .stToolbar { display: none !important; }
        .stStatusWidget { display: none !important; }
        .stMainBlockContainer { padding: 0 !important; }
        
        /* Limpiar cualquier margin/padding residual */
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            margin-top: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    # Título
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Espacio entre título y botones
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contenedor para los botones centrados
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
        
        # Espacio entre botones
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón 2: Tomar foto
        if st.button(
            "📷 Tomar foto con la cámara",
            use_container_width=True,
            type="primary",
            key="btn_camera"
        ):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()