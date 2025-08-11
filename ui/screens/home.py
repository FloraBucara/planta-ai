import streamlit as st
from pathlib import Path
from PIL import Image

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada con botones de imagen"""
    
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente.")
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Inicializar estados
    if 'click_upload' not in st.session_state:
        st.session_state.click_upload = False
    if 'click_camera' not in st.session_state:
        st.session_state.click_camera = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # BOTÓN UPLOAD
        upload_img = Path("assets/btn_upload_normal.png")
        upload_pressed = Path("assets/btn_upload_pressed.png")
        
        if upload_img.exists():
            # Mostrar imagen según estado
            if st.session_state.click_upload and upload_pressed.exists():
                image = Image.open(upload_pressed)
            else:
                image = Image.open(upload_img)
            
            # Mostrar imagen
            st.image(image, use_container_width=True)
            
            # Botón transparente encima
            if st.button("", key="btn_upload", use_container_width=True, 
                        help="Subir imagen desde dispositivo"):
                st.session_state.click_upload = True
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        else:
            # Fallback
            if st.button("📁 Subir imagen desde mi dispositivo",
                        use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # BOTÓN CÁMARA (similar)
        camera_img = Path("assets/btn_camera_normal.png")
        camera_pressed = Path("assets/btn_camera_pressed.png")
        
        if camera_img.exists():
            # Mostrar imagen según estado
            if st.session_state.click_camera and camera_pressed.exists():
                image = Image.open(camera_pressed)
            else:
                image = Image.open(camera_img)
            
            st.image(image, use_container_width=True)
            
            if st.button("", key="btn_camera", use_container_width=True,
                        help="Tomar foto con cámara"):
                st.session_state.click_camera = True
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()
        else:
            # Fallback
            if st.button("📷 Tomar foto con la cámara",
                        use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()