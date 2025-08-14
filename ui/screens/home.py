import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - CENTRADA Y LIMPIA"""
    
    # CSS para centrado perfecto
    st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        .stDeployButton { display: none !important; }
        .stDecoration { display: none !important; }
        .stToolbar { display: none !important; }
        .stStatusWidget { display: none !important; }
        
        /* Centrar todo el contenido */
        .main .block-container {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            min-height: 60vh !important;
            text-align: center !important;
            padding: 2rem !important;
        }
        
        /* Centrar mensajes */
        .stAlert {
            width: 100% !important;
            max-width: 600px !important;
            margin: 0 auto 1rem auto !important;
        }
        
        /* Centrar título */
        .main h3 {
            text-align: center !important;
            color: #2e7d32 !important;
            font-size: 1.8rem !important;
            margin-bottom: 2rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar mensajes si existen (centrados)
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        st.session_state.mensaje_inicio = None
    
    # Título centrado
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Contenedor para botones centrados
    col1, col2, col3 = st.columns([1, 3, 1])
    
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
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Botón 2: Tomar foto
        if st.button(
            "📷 Tomar foto con la cámara",
            use_container_width=True,
            type="primary",
            key="btn_camera"
        ):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()