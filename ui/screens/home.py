import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - CENTRADA Y LIMPIA"""
    
    # CSS para centrado perfecto y bloqueo de scroll
    st.markdown("""
    <style>
        /* BLOQUEAR SCROLL COMPLETAMENTE */
        html, body {
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }
        
        .stApp {
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }
        
        .main {
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }
        
        /* Ocultar elementos de Streamlit */
        .stDeployButton { display: none !important; }
        .stDecoration { display: none !important; }
        .stToolbar { display: none !important; }
        .stStatusWidget { display: none !important; }
        
        /* Ocultar scrollbars completamente */
        ::-webkit-scrollbar {
            width: 0px !important;
            background: transparent !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: transparent !important;
        }
        
        * {
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        
        /* Centrar todo el contenido */
        .main .block-container {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
            text-align: center !important;
            padding: 2rem !important;
            overflow: hidden !important;
            position: fixed !important;
            width: 100% !important;
            left: 0 !important;
            top: 0 !important;
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
        
        /* Prevenir interacciones de scroll */
        body, html {
            touch-action: none !important;
            -webkit-touch-callout: none !important;
            -webkit-user-select: none !important;
            -khtml-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
        
        /* Permitir selección solo en botones */
        .stButton, .stSelectbox, .stTextInput {
            -webkit-user-select: auto !important;
            -moz-user-select: auto !important;
            -ms-user-select: auto !important;
            user-select: auto !important;
        }
        
        /* Responsivo para móviles */
        @media (max-width: 768px) {
            .main h3 {
                font-size: 1.5rem !important;
            }
            
            .main .block-container {
                padding: 1rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript adicional para asegurar el bloqueo
    st.markdown("""
    <script>
        // Bloquear scroll con JavaScript
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
        
        // Prevenir scroll con eventos
        window.addEventListener('scroll', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
        
        // Prevenir scroll con touch
        document.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });
        
        // Prevenir scroll con wheel
        document.addEventListener('wheel', function(e) {
            e.preventDefault();
        }, { passive: false });
    </script>
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