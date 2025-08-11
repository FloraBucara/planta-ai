import streamlit as st
from pathlib import Path
from PIL import Image

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada con imágenes"""
    
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente.")
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Rutas de las imágenes
    upload_img = Path("assets/btn_upload_normal.png")
    camera_img = Path("assets/btn_camera_normal.png")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Mostrar imagen de upload
        if upload_img.exists():
            st.image(str(upload_img), use_container_width=True)
            st.info("👆 Clic en 'Subir archivo' abajo")
            if st.button("Subir archivo", key="btn_upload", use_container_width=True):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        else:
            if st.button("📁 Subir imagen desde mi dispositivo", use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mostrar imagen de cámara
        if camera_img.exists():
            st.image(str(camera_img), use_container_width=True)
            st.info("👆 Clic en 'Tomar foto' abajo")
            if st.button("Tomar foto", key="btn_camera", use_container_width=True):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()
        else:
            if st.button("📷 Tomar foto con la cámara", use_container_width=True, type="primary"):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()