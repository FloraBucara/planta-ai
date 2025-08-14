import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla estática que SÍ muestra el contenido"""
    
    # CSS equilibrado - bloquea scroll pero muestra contenido
    st.markdown("""
    <style>
        /* Bloquear scroll manteniendo el contenido visible */
        html, body {
            overflow: hidden !important;
            height: 100vh !important;
        }
        
        .stApp {
            overflow: hidden !important;
            height: 100vh !important;
        }
        
        .main {
            overflow: hidden !important;
            height: 100vh !important;
        }
        
        /* Contenedor principal - MANTENER VISIBLE */
        .main .block-container {
            overflow: hidden !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
            padding: 2rem !important;
            position: relative !important; /* NO fixed para que se vea */
        }
        
        /* Ocultar elementos de Streamlit molestos */
        .stDeployButton, .stDecoration, .stToolbar, .stStatusWidget {
            display: none !important;
        }
        
        /* Ocultar scrollbars */
        ::-webkit-scrollbar { width: 0 !important; }
        * { scrollbar-width: none !important; }
        
        /* Estilos del contenido */
        .main h3 {
            color: #2e7d32 !important;
            font-size: 1.8rem !important;
            margin: 1rem 0 2rem 0 !important;
            text-align: center !important;
        }
        
        .stAlert {
            max-width: 600px !important;
            margin: 0 auto 1rem auto !important;
        }
        
        /* Asegurar que los botones se vean */
        .stButton {
            display: block !important;
            margin: 0.5rem 0 !important;
        }
        
        .stButton > button {
            width: 100% !important;
            height: 60px !important;
            font-size: 1.2rem !important;
        }
        
        /* Responsivo */
        @media (max-width: 768px) {
            .main h3 { font-size: 1.5rem !important; }
            .main .block-container { padding: 1rem !important; }
            .stButton > button { height: 50px !important; font-size: 1rem !important; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript SOLO para bloquear scroll, sin tocar el layout
    st.markdown("""
    <script>
        // Bloquear scroll sin afectar el contenido
        function bloquearSoloScroll() {
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
        }
        
        // Ejecutar inmediatamente
        bloquearSoloScroll();
        
        // Prevenir eventos de scroll solamente
        const preventDefault = (e) => {
            e.preventDefault();
            return false;
        };
        
        window.addEventListener('scroll', preventDefault, { passive: false });
        window.addEventListener('wheel', preventDefault, { passive: false });
        window.addEventListener('touchmove', preventDefault, { passive: false });
        
        // Re-aplicar cada 500ms (menos agresivo)
        setInterval(bloquearSoloScroll, 500);
    </script>
    """, unsafe_allow_html=True)
    
    # Contenido normal de Streamlit
    
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        st.session_state.mensaje_inicio = None
    
    # Título
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Contenedor para botones
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