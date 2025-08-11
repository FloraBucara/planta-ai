import streamlit as st
from pathlib import Path
import time
from PIL import Image

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada con botones de imagen"""
    
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente.")
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # CSS para ocultar los botones de Streamlit
    st.markdown("""
    <style>
    div[data-testid="column"] button {
        opacity: 0;
        position: absolute;
        width: 100%;
        height: 100%;
        z-index: 1;
        cursor: pointer;
    }
    div[data-testid="column"] > div {
        position: relative;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Rutas de las imágenes
    upload_normal = Path("assets/btn_upload_normal.png")
    upload_pressed = Path("assets/btn_upload_pressed.png")
    camera_normal = Path("assets/btn_camera_normal.png")
    camera_pressed = Path("assets/btn_camera_pressed.png")
    
    # Inicializar estados
    if 'show_upload_pressed' not in st.session_state:
        st.session_state.show_upload_pressed = False
    if 'show_camera_pressed' not in st.session_state:
        st.session_state.show_camera_pressed = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # BOTÓN UPLOAD
        if upload_normal.exists():
            # Contenedor para el botón upload
            container_upload = st.container()
            
            with container_upload:
                # Determinar qué imagen mostrar
                if st.session_state.show_upload_pressed and upload_pressed.exists():
                    img = Image.open(upload_pressed)
                    st.image(img, use_container_width=True)
                    # Cambiar después de mostrar
                    st.session_state.show_upload_pressed = False
                    time.sleep(0.2)
                    st.session_state.metodo_seleccionado = "archivo"
                    st.rerun()
                else:
                    img = Image.open(upload_normal)
                    st.image(img, use_container_width=True)
                
                # Botón invisible encima de la imagen
                if st.button("Click", key="btn_upload"):
                    st.session_state.show_upload_pressed = True
                    st.rerun()
        else:
            # Fallback
            if st.button("📁 Subir imagen desde mi dispositivo",
                        use_container_width=True, type="primary", key="btn_upload_fallback"):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        # Espacio entre botones
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # BOTÓN CÁMARA
        if camera_normal.exists():
            # Contenedor para el botón cámara
            container_camera = st.container()
            
            with container_camera:
                # Determinar qué imagen mostrar
                if st.session_state.show_camera_pressed and camera_pressed.exists():
                    img = Image.open(camera_pressed)
                    st.image(img, use_container_width=True)
                    # Cambiar después de mostrar
                    st.session_state.show_camera_pressed = False
                    time.sleep(0.2)
                    st.session_state.metodo_seleccionado = "camara"
                    st.rerun()
                else:
                    img = Image.open(camera_normal)
                    st.image(img, use_container_width=True)
                
                # Botón invisible encima
                if st.button("Click", key="btn_camera"):
                    st.session_state.show_camera_pressed = True
                    st.rerun()
        else:
            # Fallback
            if st.button("📷 Tomar foto con la cámara",
                        use_container_width=True, type="primary", key="btn_camera_fallback"):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()