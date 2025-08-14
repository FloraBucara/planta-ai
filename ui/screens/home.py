import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - VERSIÓN ESTÁTICA"""
    
    # Contenedor principal con altura fija
    st.markdown("""
    <div style="
        height: 100vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 999;
        background: inherit;
    ">
    """, unsafe_allow_html=True)
    
    # Mostrar mensajes si existen (centrados)
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.markdown("""
        <div style="
            position: fixed;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            z-index: 1000;
        ">
            <div style="
                background: #fff3cd;
                color: #856404;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid #ffeaa7;
                margin-bottom: 1rem;
            ">
                😔 Lo sentimos, no pudimos identificar tu planta anterior.
            </div>
            <div style="
                background: #d4edda;
                color: #155724;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid #c3e6cb;
            ">
                💡 <strong>Sugerencia:</strong> Intenta con otra foto desde un ángulo diferente, 
                asegurándote de que se vean claramente las hojas o flores.
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    # Título centrado
    st.markdown("""
    <div style="
        position: fixed;
        top: 40%;
        left: 50%;
        transform: translateX(-50%);
        text-align: center;
        z-index: 1000;
    ">
        <h3 style="
            margin: 0;
            padding: 0;
            color: #2e7d32;
            font-size: 1.8rem;
        ">📸 ¿Cómo quieres agregar tu planta?</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenedor de botones centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Usar un contenedor con CSS personalizado para los botones
        st.markdown("""
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1001;
            width: 400px;
            max-width: 90vw;
        ">
        """, unsafe_allow_html=True)
        
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
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Botón 2: Tomar foto
        if st.button(
            "📷 Tomar foto con la cámara",
            use_container_width=True,
            type="primary",
            key="btn_camera"
        ):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Cerrar contenedor principal
    st.markdown("</div>", unsafe_allow_html=True)