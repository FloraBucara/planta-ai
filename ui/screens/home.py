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
    
    # Rutas de las imágenes
    upload_normal = Path("assets/btn_upload_normal.png")
    upload_pressed = Path("assets/btn_upload_pressed.png")
    camera_normal = Path("assets/btn_camera_normal.png")
    camera_pressed = Path("assets/btn_camera_pressed.png")
    
    # Estados para controlar el cambio de imagen
    if 'upload_pressed' not in st.session_state:
        st.session_state.upload_pressed = False
    if 'camera_pressed' not in st.session_state:
        st.session_state.camera_pressed = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # IMAGEN DE UPLOAD
        if upload_normal.exists():
            # Verificar si debe mostrar imagen pressed
            if st.session_state.upload_pressed and upload_pressed.exists():
                st.image(str(upload_pressed), use_container_width=True)
                st.session_state.upload_pressed = False
                time.sleep(0.3)
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
            else:
                # Mostrar imagen normal
                if st.button("", key="upload_btn", use_container_width=True):
                    st.session_state.upload_pressed = True
                    st.rerun()
                
                # Mover la imagen arriba del botón con margen negativo
                st.markdown(
                    f'<img src="data:image/png;base64,{image_to_base64(upload_normal)}" style="width: 100%; margin-top: -80px; cursor: pointer;">',
                    unsafe_allow_html=True
                )
        else:
            # Fallback si no hay imagen
            if st.button("📁 Subir imagen desde mi dispositivo", use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # IMAGEN DE CÁMARA
        if camera_normal.exists():
            # Verificar si debe mostrar imagen pressed
            if st.session_state.camera_pressed and camera_pressed.exists():
                st.image(str(camera_pressed), use_container_width=True)
                st.session_state.camera_pressed = False
                time.sleep(0.3)
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()
            else:
                # Mostrar imagen normal
                if st.button("", key="camera_btn", use_container_width=True):
                    st.session_state.camera_pressed = True
                    st.rerun()
                
                # Mover la imagen arriba del botón
                st.markdown(
                    f'<img src="data:image/png;base64,{image_to_base64(camera_normal)}" style="width: 100%; margin-top: -80px; cursor: pointer;">',
                    unsafe_allow_html=True
                )
        else:
            # Fallback si no hay imagen
            if st.button("📷 Tomar foto con la cámara", use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()

def image_to_base64(image_path):
    """Convierte imagen a base64"""
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()