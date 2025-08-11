import streamlit as st
from pathlib import Path
import base64
import time

def get_image_base64(image_path):
    """Convierte una imagen a base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def crear_boton_imagen(nombre_boton, imagen_normal_path, imagen_pressed_path, accion_callback):
    """Crea un botón personalizado con imágenes"""
    
    # Estado del botón
    estado_key = f"{nombre_boton}_estado"
    if estado_key not in st.session_state:
        st.session_state[estado_key] = "normal"
    
    # Obtener imágenes en base64
    img_normal = get_image_base64(imagen_normal_path)
    img_pressed = get_image_base64(imagen_pressed_path)
    
    if img_normal and img_pressed:
        # Determinar qué imagen mostrar
        imagen_actual = img_pressed if st.session_state[estado_key] == "pressed" else img_normal
        
        # CSS para el botón
        st.markdown(f"""
        <style>
        .custom-btn-{nombre_boton} {{
            background: none;
            border: none;
            padding: 0;
            cursor: pointer;
            width: 100%;
            transition: transform 0.1s;
        }}
        .custom-btn-{nombre_boton}:active {{
            transform: scale(0.95);
        }}
        .custom-btn-img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Crear el botón con imagen
        button_html = f"""
        <button class="custom-btn-{nombre_boton}" onclick="window.location.reload();">
            <img src="data:image/png;base64,{imagen_actual}" class="custom-btn-img">
        </button>
        """
        
        # Usar un botón invisible de Streamlit para capturar el clic
        if st.button("", key=f"btn_{nombre_boton}", use_container_width=True, help=f"Clic para {nombre_boton}"):
            st.session_state[estado_key] = "pressed"
            time.sleep(0.15)  # Breve pausa para mostrar el estado pressed
            accion_callback()
            st.session_state[estado_key] = "normal"
            st.rerun()
        
        # Mostrar la imagen encima del botón invisible
        # Usamos negative margin para superponer
        st.markdown(f"""
        <div style="margin-top: -45px; pointer-events: none;">
            <img src="data:image/png;base64,{imagen_actual}" style="width: 100%; height: auto;">
        </div>
        """, unsafe_allow_html=True)
        
        return True
    
    return False

def pantalla_seleccion_metodo():
    """Pantalla para seleccionar método de entrada con botones personalizados"""
    
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        st.session_state.mensaje_inicio = None
    
    st.markdown("### 📸 ¿Cómo quieres agregar tu planta?")
    
    # Rutas de las imágenes
    assets_path = Path("assets")
    upload_normal = assets_path / "btn_upload_normal.png"
    upload_pressed = assets_path / "btn_upload_pressed.png"
    camera_normal = assets_path / "btn_camera_normal.png"
    camera_pressed = assets_path / "btn_camera_pressed.png"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # BOTÓN DE UPLOAD CON IMAGEN
        if upload_normal.exists() and upload_pressed.exists():
            def accion_upload():
                st.session_state.metodo_seleccionado = "archivo"
            
            if not crear_boton_imagen("upload", upload_normal, upload_pressed, accion_upload):
                # Fallback si falla la creación del botón personalizado
                if st.button("📁 Subir imagen desde mi dispositivo", 
                            use_container_width=True, type="primary", key="btn_upload_fallback"):
                    st.session_state.metodo_seleccionado = "archivo"
                    st.rerun()
        else:
            # Botón normal si no existen las imágenes
            if st.button("📁 Subir imagen desde mi dispositivo",
                        use_container_width=True, type="primary", key="btn_upload"):
                st.session_state.metodo_seleccionado = "archivo"
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)  # Espacio
        
        # BOTÓN DE CÁMARA CON IMAGEN
        if camera_normal.exists() and camera_pressed.exists():
            def accion_camera():
                st.session_state.metodo_seleccionado = "camara"
            
            if not crear_boton_imagen("camera", camera_normal, camera_pressed, accion_camera):
                # Fallback
                if st.button("📷 Tomar foto con la cámara",
                            use_container_width=True, type="primary", key="btn_camera_fallback"):
                    st.session_state.metodo_seleccionado = "camara"
                    st.rerun()
        else:
            # Botón normal si no existen las imágenes
            if st.button("📷 Tomar foto con la cámara",
                        use_container_width=True, type="primary", key="btn_camera"):
                st.session_state.metodo_seleccionado = "camara"
                st.rerun()