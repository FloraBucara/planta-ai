import streamlit as st
from PIL import Image
from ui.screens.upload import mostrar_imagen_y_procesar

def pantalla_tomar_foto():
    """Pantalla específica para tomar foto"""
    st.markdown("### 📷 Tomar foto con la cámara")
    st.info("📱 **En móviles:** Esto abrirá la cámara directamente")
    
    camera_image = st.camera_input(
        "Toma una foto de tu planta",
        key="camera_input",
        help="Asegúrate de que la planta esté bien iluminada y enfocada"
    )
    
    if camera_image is not None:
        try:
            imagen = Image.open(camera_image)
            mostrar_imagen_y_procesar(imagen, "cámara")
        except Exception as e:
            st.error(f"❌ Error procesando foto: {e}")
    
    # Botón para regresar - CON NUEVO ESTILO VERDE + GRIS
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "← Regresar a selección de método", 
            key="btn_back_camera",  # ← KEY DIFERENTE PARA EVITAR CONFLICTOS
            use_container_width=True
        ):
            st.session_state.metodo_seleccionado = None
            st.rerun()