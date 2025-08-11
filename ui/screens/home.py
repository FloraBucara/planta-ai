import streamlit as st

import streamlit as st
from pathlib import Path

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada"""
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Inicializar estados de botones si no existen
    if 'btn_upload_pressed' not in st.session_state:
        st.session_state.btn_upload_pressed = False
    if 'btn_camera_pressed' not in st.session_state:
        st.session_state.btn_camera_pressed = False
    
    # Rutas de las imágenes
    upload_normal = Path("assets/boton_upload_normal.png")
    upload_pressed = Path("assets/boton_upload_pressed.png")
    camera_normal = Path("assets/boton_camera_normal.png")
    camera_pressed = Path("assets/boton_camera_pressed.png")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # BOTÓN DE UPLOAD CON IMAGEN
        if upload_normal.exists() and upload_pressed.exists():
            # Determinar qué imagen mostrar
            imagen_upload = upload_pressed if st.session_state.btn_upload_pressed else upload_normal
            
            # Crear un contenedor clickeable
            if st.button(
                "",  # Sin texto
                key="btn_upload_img",
                use_container_width=True,
                help="Subir imagen desde tu dispositivo"
            ):
                st.session_state.btn_upload_pressed = True
                st.session_state.metodo_seleccionado = "archivo"
                # Pequeña pausa para mostrar el cambio de imagen
                import time
                time.sleep(0.1)
                st.rerun()
            
            # Mostrar la imagen sobre el botón invisible
            st.image(imagen_upload, use_container_width=True)
        else:
            # Fallback al botón normal si no hay imágenes
            if st.button(
                "📁 Subir imagen desde mi dispositivo",
                use_container_width=True,
                type="primary",
                key="btn_upload"
            ):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)  # Espacio
        
        # BOTÓN DE CÁMARA CON IMAGEN (similar)
        if camera_normal.exists() and camera_pressed.exists():
            # Determinar qué imagen mostrar
            imagen_camera = camera_pressed if st.session_state.btn_camera_pressed else camera_normal
            
            if st.button(
                "",  # Sin texto
                key="btn_camera_img",
                use_container_width=True,
                help="Tomar foto con la cámara"
            ):
                st.session_state.btn_camera_pressed = True
                st.session_state.metodo_seleccionado = "camara"
                import time
                time.sleep(0.1)
                st.rerun()
            
            # Mostrar la imagen
            st.image(imagen_camera, use_container_width=True)
        else:
            # Fallback al botón normal
            if st.button(
                "📷 Tomar foto con la cámara",
                use_container_width=True,
                type="primary",
                key="btn_camera"
            ):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()