import streamlit as st
from PIL import Image
from config import STREAMLIT_CONFIG

def pantalla_upload_archivo():
    """Pantalla específica para subir archivo"""
    # Marcar pantalla actual
    st.session_state.current_screen = 'upload'
    
    # CSS para ocultar el nombre del archivo
    st.markdown("""
    <style>
    /* Método más agresivo - ocultar todo excepto el área de drop */
    div[data-testid="stFileUploader"] > div:not(:first-child) {
        display: none !important;
    }
    /* Ocultar específicamente elementos de archivo subido */
    .uploadedFile, 
    [data-testid="fileUploadedFileName"],
    div[data-testid="stFileUploader"] li,
    div[data-testid="stFileUploader"] ul {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📁 Subir imagen desde tu dispositivo")
    
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=STREAMLIT_CONFIG["allowed_extensions"],
        help="Formatos soportados: JPG, JPEG, PNG. Máximo 10MB.",
        key="file_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Validar tamaño
        if uploaded_file.size > STREAMLIT_CONFIG["max_file_size"] * 1024 * 1024:
            st.error(f"❌ Archivo muy grande. Máximo {STREAMLIT_CONFIG['max_file_size']}MB.")
            return
        
        try:
            imagen = Image.open(uploaded_file)
            mostrar_imagen_y_procesar(imagen, "archivo")
        except Exception as e:
            st.error(f"❌ Error cargando imagen: {e}")

def mostrar_imagen_y_procesar(imagen, fuente):
    """Muestra imagen y botón para procesar"""
    # Importar aquí para evitar circular imports
    from utils.session_manager import session_manager
    
    # Layout con imagen más pequeña (1/3) y botones (2/3)
    col_imagen, col_botones = st.columns([1, 2])
    
    # Columna izquierda: Imagen más pequeña
    with col_imagen:
        st.image(imagen, caption=f"Tu planta (desde {fuente})", width=200)
    
    # Columna derecha: Botones más pequeños
    with col_botones:
        # Sub-columnas para hacer botones más pequeños
        _, col_btn, _ = st.columns([0.2, 1, 0.2])
        
        with col_btn:
            # Botón de identificar
            if st.button(
                "🔍 Identificar Planta",
                type="primary",
                use_container_width=True,
                key="btn_analyze"
            ):
                # Guardar imagen y procesar
                st.session_state.temp_imagen = imagen
                procesar_identificacion()
            
            # Botón de regresar
            if st.button("← Regresar a selección de método", key="back_from_image", use_container_width=True):
                st.session_state.metodo_seleccionado = None
                st.rerun()

def procesar_identificacion():
    """Función separada para procesar la identificación"""
    from utils.session_manager import session_manager
    
    if 'temp_imagen' not in st.session_state:
        st.error("❌ No hay imagen para procesar")
        return
    
    imagen = st.session_state.temp_imagen
    
    with st.spinner("🧠 Analizando tu planta..."):
        try:
            # Limpiar estado anterior
            limpiar_sesion()
            
            # Crear nueva sesión
            sesion = session_manager.iniciar_nueva_sesion(imagen)
            
            # Establecer en session_state
            st.session_state.session_id = sesion.session_id
            st.session_state.imagen_actual = imagen
            st.session_state.intento_actual = 1
            st.session_state.especies_descartadas = set()
            
            # Hacer predicción
            resultado = hacer_prediccion_con_info(imagen, None)
            
            if resultado.get("exito"):
                st.session_state.resultado_actual = resultado
                # Limpiar imagen temporal
                if 'temp_imagen' in st.session_state:
                    del st.session_state.temp_imagen
                if 'temp_fuente' in st.session_state:
                    del st.session_state.temp_fuente
                st.rerun()
            else:
                st.error(f"❌ {resultado.get('mensaje', 'Error en la predicción')}")
                
        except Exception as e:
            st.error(f"❌ Error en la predicción: {e}")

def limpiar_sesion():
    """Limpia la sesión actual completamente"""
    # Importar aquí para evitar problemas
    # Guardar mensaje si existe
    mensaje_temp = st.session_state.get('mensaje_inicio', None)
    
    # Limpiar todo de forma segura
    for key in ['session_id', 'imagen_actual', 'especies_descartadas', 
                'intento_actual', 'resultado_actual', 'mostrar_top_especies',
                'prediction_screen_loaded']:
        if key in st.session_state:
            if key == 'especies_descartadas':
                st.session_state[key] = set()
            elif key == 'intento_actual':
                st.session_state[key] = 1
            else:
                st.session_state[key] = None
    
    # Restaurar mensaje
    st.session_state.mensaje_inicio = mensaje_temp
    
    # Limpiar caché
    try:
        st.cache_data.clear()
    except:
        pass

def hacer_prediccion_con_info(imagen, especies_excluir=None):
    """
    Hace predicción y obtiene información de Firestore
    """
    from utils.session_manager import session_manager
    from utils.firebase_config import obtener_info_planta_basica
    from datetime import datetime
    
    try:
        # Hacer predicción con el modelo
        resultado = session_manager.predictor.predecir_planta(imagen, especies_excluir)
        
        if resultado.get("exito"):
            especie_predicha = resultado["especie_predicha"]
            
            # Buscar información en Firestore
            info_planta = buscar_info_planta_firestore(especie_predicha)
            
            # Combinar resultados
            resultado_completo = {
                "exito": True,
                "especie_predicha": especie_predicha,
                "confianza": resultado["confianza"],
                "info_planta": info_planta,
                "top_predicciones": resultado.get("top_predicciones", []),
                "timestamp": datetime.now().isoformat()
            }
            
            return resultado_completo
        else:
            return resultado
            
    except Exception as e:
        return {
            "exito": False,
            "error": str(e),
            "mensaje": "Error en la predicción"
        }

def buscar_info_planta_firestore(nombre_cientifico):
    """
    Busca información de la planta en Firestore con múltiples formatos
    """
    from utils.firebase_config import obtener_info_planta_basica
    
    try:
        print(f"🔍 Buscando en Firestore: {nombre_cientifico}")
        
        # Usar la función básica mejorada
        info = obtener_info_planta_basica(nombre_cientifico)
        
        # Verificar si encontramos datos reales
        if info.get('fuente_datos') == 'firestore':
            print(f"✅ Datos encontrados en Firestore para: {nombre_cientifico}")
            return {
                "exito": True,
                "datos": info,
                "fuente": "firestore"
            }
        else:
            print(f"⚠️ No se encontraron datos en Firestore para: {nombre_cientifico}")
            return {
                "exito": False,
                "datos": info,
                "fuente": info.get('fuente_datos', 'no_encontrado')
            }
            
    except Exception as e:
        print(f"❌ Error buscando en Firestore: {e}")
        return {
            "exito": False,
            "datos": {
                "nombre_cientifico": nombre_cientifico,
                "nombre_comun": "Error de conexión",
                "descripcion": f"No se pudo conectar con la base de datos: {str(e)}",
                "fuente_datos": "error"
            },
            "fuente": "error"
        }