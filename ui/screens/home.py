import streamlit as st
from pathlib import Path
import time

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
    
    # Inicializar estados para controlar qué imagen mostrar
    if 'show_upload_pressed' not in st.session_state:
        st.session_state.show_upload_pressed = False
    if 'show_camera_pressed' not in st.session_state:
        st.session_state.show_camera_pressed = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # BOTÓN UPLOAD
        if upload_normal.exists() and upload_pressed.exists():
            # Placeholder para la imagen
            upload_placeholder = st.empty()
            
            # Mostrar imagen según estado
            if st.session_state.show_upload_pressed:
                upload_placeholder.image(str(upload_pressed), use_container_width=True)
                # Resetear estado y cambiar pantalla después de mostrar imagen pressed
                st.session_state.show_upload_pressed = False
                time.sleep(0.3)  # Mostrar imagen pressed por 0.3 segundos
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
            else:
                upload_placeholder.image(str(upload_normal), use_container_width=True)
            
            # Botón invisible sobre la imagen
            if st.button("", key="btn_upload", help="Subir imagen desde dispositivo"):
                st.session_state.show_upload_pressed = True
                st.rerun()
        else:
            # Fallback si no existen las imágenes
            if st.button("📁 Subir imagen desde mi dispositivo",
                        use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # BOTÓN CÁMARA
        if camera_normal.exists() and camera_pressed.exists():
            # Placeholder para la imagen
            camera_placeholder = st.empty()
            
            # Mostrar imagen según estado
            if st.session_state.show_camera_pressed:
                camera_placeholder.image(str(camera_pressed), use_container_width=True)
                # Resetear estado y cambiar pantalla
                st.session_state.show_camera_pressed = False
                time.sleep(0.3)  # Mostrar imagen pressed por 0.3 segundos
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()
            else:
                camera_placeholder.image(str(camera_normal), use_container_width=True)
            
            # Botón invisible sobre la imagen
            if st.button("", key="btn_camera", help="Tomar foto con cámara"):
                st.session_state.show_camera_pressed = True
                st.rerun()
        else:
            # Fallback si no existen las imágenes
            if st.button("📷 Tomar foto con la cámara",
                        use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()