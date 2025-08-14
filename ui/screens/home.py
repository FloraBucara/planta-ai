import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla REALMENTE estática - sin scroll"""
    
    # Inyectar CSS y JavaScript de forma más agresiva
    st.markdown("""
    <style>
        /* FORZAR OVERRIDE DE TODOS LOS ESTILOS */
        html, body, #root, .stApp, .main, .block-container {
            height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
            position: fixed !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .main .block-container {
            padding: 1rem !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
        }
        
        /* Ocultar scrollbars */
        ::-webkit-scrollbar { width: 0 !important; }
        * { scrollbar-width: none !important; }
        
        /* Ocultar elementos de Streamlit */
        .stDeployButton, .stDecoration, .stToolbar, .stStatusWidget {
            display: none !important;
        }
        
        /* Estilos del contenido */
        .main h3 {
            color: #2e7d32 !important;
            font-size: 1.8rem !important;
            margin: 1rem 0 2rem 0 !important;
        }
        
        .stAlert {
            max-width: 600px !important;
            margin: 0 auto 1rem auto !important;
        }
        
        /* Responsivo */
        @media (max-width: 768px) {
            .main h3 { font-size: 1.5rem !important; }
            .main .block-container { padding: 0.5rem !important; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript más agresivo para bloquear scroll
    st.markdown("""
    <script>
        // Función para bloquear scroll
        function bloquearScroll() {
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
            document.body.style.position = 'fixed';
            document.body.style.width = '100%';
            document.body.style.height = '100%';
        }
        
        // Ejecutar inmediatamente
        bloquearScroll();
        
        // Prevenir todos los tipos de scroll
        const preventDefault = (e) => {
            e.preventDefault();
            e.stopPropagation();
            return false;
        };
        
        // Eventos de scroll
        window.addEventListener('scroll', preventDefault, { passive: false });
        window.addEventListener('wheel', preventDefault, { passive: false });
        window.addEventListener('touchmove', preventDefault, { passive: false });
        window.addEventListener('keydown', (e) => {
            // Bloquear teclas de navegación
            if ([32, 33, 34, 35, 36, 37, 38, 39, 40].includes(e.keyCode)) {
                preventDefault(e);
            }
        });
        
        // Re-aplicar cada 100ms para asegurar
        setInterval(bloquearScroll, 100);
        
        // Observer para cambios en el DOM
        const observer = new MutationObserver(bloquearScroll);
        observer.observe(document.body, { 
            childList: true, 
            subtree: true, 
            attributes: true 
        });
    </script>
    """, unsafe_allow_html=True)
    
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
            # Restaurar scroll antes de cambiar pantalla
            st.markdown("""
            <script>
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
                document.body.style.position = 'relative';
            </script>
            """, unsafe_allow_html=True)
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
            # Restaurar scroll antes de cambiar pantalla
            st.markdown("""
            <script>
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
                document.body.style.position = 'relative';
            </script>
            """, unsafe_allow_html=True)
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()