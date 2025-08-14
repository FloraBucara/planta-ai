import streamlit as st

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada - MEJORADA SIN ESPACIOS"""
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    # Título centrado - TEXTO MODIFICADO
    st.markdown("""
    <div style="text-align: center; margin-bottom: 0.5rem;">
        <h4 style="margin-bottom: 0; font-size: 1.25rem;">¿Cómo quieres agregar tu planta?</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones centrados - ANCHO REDUCIDO
    col1, col2, col3 = st.columns([1.5, 1.5, 1.5])  # Columnas más estrechas
    
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
        
        # AQUÍ CAMBIAS EL ESPACIO ENTRE BOTONES:
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        # Opciones de espaciado:
        # margin: 0.25rem 0;  → Poco espacio
        # margin: 0.5rem 0;   → Espacio normal (actual)
        # margin: 1rem 0;     → Más espacio
        # margin: 1.5rem 0;   → Mucho espacio
        
        # Botón 2: Tomar foto
        if st.button(
            "📷 Tomar foto con la cámara",
            use_container_width=True,
            type="primary",
            key="btn_camera"
        ):
            st.session_state.metodo_seleccionado = "camara"
            st.rerun()