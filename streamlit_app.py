import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from datetime import datetime
import requests
import threading
import time
import subprocess
import os
import re
import time
from utils.api_client import enviar_feedback, servidor_disponible, obtener_estadisticas

# ==================== CONFIGURACIÓN DE LA PÁGINA (DEBE SER PRIMERO) ====================
# Agregar directorio padre al path ANTES de importar configuración
sys.path.append(str(Path(__file__).parent))

from config import STREAMLIT_CONFIG, MESSAGES, RETRAINING_CONFIG

st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

# ==================== IMPORTS DEL MODELO (DESPUÉS DE set_page_config) ====================
try:
    from model.prediction import session_manager, verificar_sistema_prediccion
    from utils.firebase_config import obtener_info_planta_basica, firestore_manager
except ImportError as e:
    st.error(f"❌ Error importando módulos: {e}")
    st.stop()


# ==================== CSS PERSONALIZADO ====================

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #2E8B57, #98FB98);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .prediction-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .info-card {
        background: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .species-card {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        margin: 0.5rem 0;
        text-align: center;
        transition: all 0.3s;
    }
    
    .species-card:hover {
        border-color: #28a745;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .debug-info {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
        margin: 0.5rem 0;
        font-size: 0.9em;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .firestore-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .firestore-connected {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .firestore-disconnected {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    .confidence-bar {
        background: #e9ecef;
        border-radius: 10px;
        height: 20px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .confidence-fill {
        background: linear-gradient(90deg, #28a745, #20c997);
        height: 100%;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES DE INICIALIZACIÓN ====================

@st.cache_resource
def inicializar_firestore_app():
    """Inicializa Firestore una sola vez usando cache"""
    try:
        print("🔥 Inicializando Firestore...")
        
        # Intentar usar secrets (funciona en local y cloud)
        if "firebase" in st.secrets:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Verificar si ya está inicializado
            if not firebase_admin._apps:
                # Convertir secrets a diccionario
                firebase_creds = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_creds)
                firebase_admin.initialize_app(cred)
            
            firestore_manager.db = firestore.client()
            firestore_manager.initialized = True
            print("✅ Firestore inicializado desde secrets")
            return True
        else:
            print("❌ No se encontraron secrets de Firebase")
            return False
            
    except Exception as e:
        print(f"❌ Excepción inicializando Firestore: {e}")
        return False
    
def iniciar_api_background():
    """Inicia la API con Ngrok en background"""
    try:
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        print("🚀 Iniciando API con Ngrok en background...")
        subprocess.Popen([sys.executable, "api_server.py"], cwd=project_dir)
        time.sleep(5)
        print("✅ API iniciada en background")
        
    except Exception as e:
        print(f"❌ Error iniciando API: {e}")

def verificar_y_iniciar_api():
    """Verifica si la API está corriendo, si no la inicia"""
    try:
        response = requests.get("http://localhost:5000/", timeout=3)
        if response.status_code == 200:
            print("✅ API ya está corriendo")
            return True
    except:
        pass
    
    # Solo intentar iniciar API en desarrollo local
    if "firebase" not in st.secrets:  # Si NO estamos en Streamlit Cloud
        print("🔄 API no detectada, iniciando...")
        thread = threading.Thread(target=iniciar_api_background, daemon=True)
        thread.start()
        
        for i in range(30):
            try:
                response = requests.get("http://localhost:5000/", timeout=2)
                if response.status_code == 200:
                    print("✅ API lista y funcionando")
                    return True
            except:
                pass
            time.sleep(1)
    
    print("⚠️ API no disponible (normal en Streamlit Cloud)")
    return False

# ==================== INICIALIZACIÓN DE ESTADO ====================

def inicializar_estado():
    """Inicializa todos los estados necesarios"""
    # Lista de estados con sus valores por defecto
    estados_default = {
        'firestore_initialized': False,
        'api_initialized': False,
        'session_id': None,
        'imagen_actual': None,
        'especies_descartadas': set(),
        'intento_actual': 1,
        'resultado_actual': None,
        'mostrar_top_especies': False,
        'max_intentos': 3,
        'mensaje_inicio': None
    }
    
    # Inicializar cada estado si no existe
    for key, default_value in estados_default.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Ahora sí, intentar inicializar servicios
    if not st.session_state.firestore_initialized:
        st.session_state.firestore_initialized = inicializar_firestore_app()
    
    if not st.session_state.api_initialized:
        st.session_state.api_initialized = verificar_y_iniciar_api()

def limpiar_sesion():
    """Limpia la sesión actual completamente"""
    # Guardar mensaje si existe
    mensaje_temp = st.session_state.get('mensaje_inicio', None)
    
    # Limpiar todo de forma segura
    for key in ['session_id', 'imagen_actual', 'especies_descartadas', 
                'intento_actual', 'resultado_actual', 'mostrar_top_especies']:
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

inicializar_estado()
# ==================== FUNCIONES AUXILIARES MEJORADAS ====================

def mostrar_header():
    """Muestra el header principal de la aplicación"""
    st.markdown('<h1 class="main-header">🌱 BucaraFlora - Identificador de Plantas IA</h1>', unsafe_allow_html=True)
    st.markdown("**Sube una foto de tu planta y descubre qué especie es**")
    
    # Mostrar estado de servicios
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.get('api_initialized'):
            st.markdown('<div class="firestore-connected">✅ API Activa</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="firestore-disconnected">⚠️ API Local No Disponible</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.get('firestore_initialized'):
            st.markdown('<div class="firestore-connected">✅ Base de Datos Conectada</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="firestore-disconnected">❌ Base de Datos Desconectada</div>', unsafe_allow_html=True)

def buscar_info_planta_firestore(nombre_cientifico):
    """
    Busca información de la planta en Firestore con múltiples formatos
    """
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

def mostrar_info_planta_completa(info_planta):
    """
    Muestra la información completa de la planta de forma visualmente atractiva
    """
    datos = info_planta.get('datos', {})
    fuente = info_planta.get('fuente', 'desconocido')
    
    # Indicador de fuente de datos
    if fuente == 'firestore':
        st.success("✅ Información verificada de la base de datos")
    elif fuente == 'no_encontrado':
        st.warning("⚠️ Especie no encontrada en la base de datos")
    else:
        st.error("❌ Error al obtener información de la base de datos")
    
    # Contenedor principal
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Nombre común y científico
            st.markdown(f"### 🌿 {datos.get('nombre_comun', 'Nombre no disponible')}")
            st.markdown(f"**Nombre científico:** *{datos.get('nombre_cientifico', 'N/A')}*")
            
            # Descripción
            descripcion = datos.get('descripcion', '')
            if descripcion and fuente == 'firestore':
                st.markdown("#### 📝 Descripción")
                st.markdown(f'<div class="info-card">{descripcion}</div>', unsafe_allow_html=True)
            
            # Información adicional
            if datos.get('fecha_observacion'):
                st.markdown(f"**📅 Fecha de observación:** {datos.get('fecha_observacion')}")
            
            if datos.get('fuente'):
                st.markdown(f"**📚 Fuente:** {datos.get('fuente')}")
        
        with col2:
            # NUEVA FUNCIÓN: Imagen desde servidor
            mostrar_imagen_referencia(datos.get('nombre_cientifico', ''))
    
    # Información taxonómica (sin cambios)
    if datos.get('taxonomia') and fuente == 'firestore':
        with st.expander("🧬 Ver Clasificación Taxonómica"):
            # ... resto del código sin cambios
            taxonomia = datos.get('taxonomia', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Clasificación Superior:**")
                st.write(f"• **Reino:** {taxonomia.get('reino', 'N/A')}")
                st.write(f"• **Filo:** {taxonomia.get('filo', 'N/A')}")
                st.write(f"• **Clase:** {taxonomia.get('clase', 'N/A')}")
            
            with col2:
                st.markdown("**Clasificación Inferior:**")
                st.write(f"• **Orden:** {taxonomia.get('orden', 'N/A')}")
                st.write(f"• **Familia:** {taxonomia.get('familia', 'N/A')}")
                st.write(f"• **Género:** {taxonomia.get('genero', 'N/A')}")
                st.write(f"• **Especie:** {taxonomia.get('especie', 'N/A')}")
def mostrar_imagen_referencia(nombre_cientifico):
    """Muestra la primera imagen de la especie desde el servidor"""
    try:
        from utils.api_client import SERVER_URL
        import requests
        
        if not SERVER_URL or SERVER_URL == "http://localhost:8000":
            st.info("📷 Servidor de imágenes no disponible")
            return
        
        # Probar la primera imagen con el formato: NombreCientifico_01.jpg
        imagen_url = f"{SERVER_URL}/api/image/{nombre_cientifico}/{nombre_cientifico}_01.jpg"
        
        try:
            # Verificar que la imagen existe
            response = requests.head(imagen_url, timeout=5)
            
            if response.status_code == 200:
                st.image(
                    imagen_url,
                    caption="Imagen de referencia",
                    use_container_width=True
                )
            else:
                st.info("📷 Imagen de referencia no disponible")
                
        except requests.RequestException:
            st.info("📷 Error cargando imagen de referencia")
            
    except Exception as e:
        st.info("📷 Sin imagen de referencia")
        print(f"Error: {e}")
        
def hacer_prediccion_con_info(imagen, especies_excluir=None):
    """
    Hace predicción y obtiene información de Firestore
    """
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

# ==================== PANTALLAS PRINCIPALES ====================

def pantalla_upload_imagen():
    """Pantalla inicial para subir imagen"""
    # Mostrar mensajes si existen
    if st.session_state.get('mensaje_inicio') == "no_identificada":
        st.warning("😔 Lo sentimos, no pudimos identificar tu planta anterior.")
        st.info("💡 **Sugerencia:** Intenta con otra foto desde un ángulo diferente, asegurándote de que se vean claramente las hojas o flores.")
        # Limpiar el mensaje después de mostrarlo
        st.session_state.mensaje_inicio = None
        
    st.markdown("### 📸 Sube una foto de tu planta")
    
    # Área de carga
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=STREAMLIT_CONFIG["allowed_extensions"],
        help="Formatos soportados: JPG, JPEG, PNG. Máximo 10MB."
    )
    
    if uploaded_file is not None:
        # Validar tamaño
        if uploaded_file.size > STREAMLIT_CONFIG["max_file_size"] * 1024 * 1024:
            st.error(f"❌ Archivo muy grande. Máximo {STREAMLIT_CONFIG['max_file_size']}MB.")
            return
        
        try:
            # Cargar y mostrar imagen
            imagen = Image.open(uploaded_file)
            
            # Mostrar imagen con columnas para centrarla
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(imagen, caption="Tu planta", use_container_width=True)
            
            # Botón de análisis
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔍 Identificar Planta", type="primary", use_container_width=True):
                    with st.spinner("🧠 Analizando tu planta..."):
                        # Limpiar estado anterior
                        limpiar_sesion()
                        
                        # Establecer nueva sesión
                        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.session_state.imagen_actual = imagen
                        st.session_state.intento_actual = 1
                        st.session_state.especies_descartadas = set()
                        
                        # Hacer predicción con información
                        resultado = hacer_prediccion_con_info(imagen, None)
                        
                        if resultado.get("exito"):
                            st.session_state.resultado_actual = resultado
                            st.rerun()
                        else:
                            st.error(f"❌ {resultado.get('mensaje', 'Error en la predicción')}")
                            
        except Exception as e:
            st.error(f"❌ Error cargando imagen: {e}")

def pantalla_prediccion_feedback():
    """Pantalla de predicción con botones de feedback"""
    resultado = st.session_state.resultado_actual
    
    # Mostrar imagen del usuario
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.imagen_actual, caption="Tu planta", use_container_width=True)
    
    # Card de predicción
    st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
    
    # Mostrar información de la planta
    info_planta = resultado.get("info_planta", {})
    mostrar_info_planta_completa(info_planta)
    
    # Barra de confianza
    confianza = resultado["confianza"]
    porcentaje = int(confianza * 100)
    
    st.markdown(f"""
    <div class="confidence-bar">
        <div class="confidence-fill" style="width: {porcentaje}%;"></div>
    </div>
    <p style="text-align: center; margin: 0.5rem 0; font-weight: bold;">
        Confianza de la predicción: {porcentaje}%
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Botones de feedback
    st.markdown("---")
    st.markdown("### ¿Es correcta esta identificación?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ ¡Sí, es correcta!", type="primary", use_container_width=True):
            with st.spinner("💾 Guardando tu confirmación..."):
                # Intentar enviar al servidor
                if servidor_disponible():
                    respuesta = enviar_feedback(
                        imagen_pil=st.session_state.imagen_actual,
                        session_id=st.session_state.session_id,
                        especie_predicha=resultado["especie_predicha"],
                        confianza=resultado["confianza"],
                        feedback_tipo="correcto",
                        especie_correcta=resultado["especie_predicha"]
                   )
                
                    if respuesta.get("exito"):
                        st.success(MESSAGES["prediction_success"])
                        st.success("✅ Imagen guardada en el servidor")
                    
                        # Mostrar info de reentrenamiento si está cerca
                        if respuesta.get("reentrenamiento", {}).get("progreso", 0) > 80:
                            st.info(f"📊 Progreso para reentrenamiento: {respuesta['reentrenamiento']['progreso']}%")
                    else:
                        st.warning("⚠️ No se pudo guardar en el servidor, pero tu feedback fue registrado")
                else:
                    st.warning("⚠️ Servidor no disponible, feedback guardado localmente")
            
                st.balloons()
            
                # Esperar para que vea el mensaje
                time.sleep(2)
            
                # Establecer mensaje de éxito
                st.session_state.mensaje_inicio = "identificada_correcta"
            
                # Limpiar y volver al inicio
                limpiar_sesion()
                st.rerun()
    
    with col2:
        if st.button("❌ No, es incorrecta", type="secondary", use_container_width=True):
            # Procesar feedback negativo
            especie_rechazada = resultado["especie_predicha"]
            st.session_state.especies_descartadas.add(especie_rechazada)
            st.session_state.intento_actual += 1
            
            # Mostrar directamente las top 5 especies
            st.session_state.mostrar_top_especies = True
            st.rerun()

def pantalla_top_especies():
    """Pantalla de selección manual de las top 5 especies"""
    st.markdown("### 🤔 ¿Tal vez sea una de estas?")
    st.info("Selecciona la especie correcta de las siguientes opciones:")
    
    # Obtener top 5 especies
    with st.spinner("🔍 Buscando especies similares..."):
        especies_excluir = list(st.session_state.especies_descartadas)
        top_especies = session_manager.predictor.obtener_top_especies(
            st.session_state.imagen_actual,
            cantidad=5,  # Solo top 5
            especies_excluir=especies_excluir
        )
    
    if not top_especies:
        st.error("❌ Error obteniendo especies similares")
        return
    
    # Mostrar imagen original
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.imagen_actual, caption="Tu planta", use_column_width=True)
    
    st.markdown("---")
    
    # Variable para controlar si se seleccionó algo
    seleccionado = False
    
    # Mostrar las 5 especies en un layout mejorado
    for i, especie_data in enumerate(top_especies):
        # Buscar información de la especie
        info_planta = buscar_info_planta_firestore(especie_data["especie"])
        datos = info_planta.get('datos', {})
        
        # Card para cada especie
        st.markdown(f'<div class="species-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            # Número de opción
            st.markdown(f"### {i+1}")
        
        with col2:
            # Info de la especie
            st.markdown(f"**{datos.get('nombre_comun', 'N/A')}**")
            st.markdown(f"*{especie_data['especie']}*")
            
            # Barra de confianza mini
            porcentaje = int(especie_data["confianza"] * 100)
            st.markdown(f"""
            <div class="confidence-bar" style="height: 10px;">
                <div class="confidence-fill" style="width: {porcentaje}%;"></div>
            </div>
            <p style="text-align: center; font-size: 0.9em; margin: 0;">
                Confianza: {porcentaje}%
            </p>
            """, unsafe_allow_html=True)
        
        with col3:
            # Botón de selección
            
            if st.button(
                "✅ Es esta", 
                key=f"select_{i}",
                use_container_width=True,
                type="primary" if i == 0 else "secondary"
            ):
                with st.spinner("💾 Guardando tu selección..."):
                    # Intentar enviar al servidor
                    if servidor_disponible():
                        respuesta = enviar_feedback(
                            imagen_pil=st.session_state.imagen_actual,
                            session_id=st.session_state.session_id,
                            especie_predicha=st.session_state.resultado_actual["especie_predicha"],
                            confianza=st.session_state.resultado_actual["confianza"],
                            feedback_tipo="corregido",
                            especie_correcta=especie_data["especie"]
                        )
            
                        if respuesta.get("exito"):
                            st.success(f"🎉 ¡Gracias! Has identificado tu planta como **{datos.get('nombre_comun', especie_data['especie'])}**")
                            st.success("✅ Imagen guardada para mejorar el modelo")
                        else:
                            st.warning("⚠️ Feedback registrado (servidor no disponible)")
                    else:
                        st.success(f"🎉 ¡Gracias! Has identificado tu planta como **{datos.get('nombre_comun', especie_data['especie'])}**")
        
                    st.balloons()
        
                    # Guardar info de la planta identificada
                    st.session_state.mensaje_inicio = f"identificada_top5:{datos.get('nombre_comun', especie_data['especie'])}"
        
                    # Limpiar y volver al inicio
                    limpiar_sesion()
                    st.rerun()
    
    # Opción "No es ninguna de estas"
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("❌ No es ninguna de estas", type="secondary", use_container_width=True):
            # Establecer mensaje para mostrar en inicio
            st.session_state.mensaje_inicio = "no_identificada"
        
            # Limpiar y volver al inicio
            limpiar_sesion()
            st.rerun()

def pantalla_error_sistema():
    """Pantalla cuando el sistema no está disponible"""
    st.markdown('<div class="error-message">', unsafe_allow_html=True)
    st.markdown("### ❌ Sistema No Disponible")
    st.markdown("El modelo de identificación no está cargado o entrenado.")
    st.markdown("**Posibles soluciones:**")
    st.markdown("- Entrenar el modelo inicial: `python model/train_model.py`")
    st.markdown("- Verificar que existe el archivo del modelo")
    st.markdown("- Contactar al administrador del sistema")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Verificar sistema nuevamente"):
        st.rerun()

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    # SIEMPRE inicializar estado primero
    inicializar_estado()
    
    # Mostrar header
    mostrar_header()
    
    # Verificar sistema
    estado_sistema = verificar_sistema_prediccion()
    
    if not estado_sistema["disponible"]:
        pantalla_error_sistema()
        return
    
    # Determinar qué pantalla mostrar con verificaciones seguras
    if st.session_state.get('mostrar_top_especies', False):
        pantalla_top_especies()
    elif st.session_state.get('resultado_actual'):
        pantalla_prediccion_feedback()
    else:
        pantalla_upload_imagen()
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### ℹ️ Información del Sistema")
        st.markdown(f"🌿 **Especies:** {estado_sistema.get('especies', 'N/A')}")
        st.markdown(f"⏱️ **Actualización:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Estado de servicios
        st.markdown("---")
        st.markdown("### 🔌 Estado de Servicios")
        
        if st.session_state.get('firestore_initialized', False):
            st.success("✅ Base de Datos: Conectada")
        else:
            st.error("❌ Base de Datos: Desconectada")
        # En el sidebar, después del estado de Firebase
        if servidor_disponible():
            st.success("✅ Servidor Local: Conectado")
    
            # Mostrar estadísticas si están disponibles
            stats = obtener_estadisticas()
            if stats:
                st.markdown("📊 **Estadísticas:**")
                st.write(f"• Feedback total: {stats['feedback_total']}")
                st.write(f"• Imágenes guardadas: {stats['imagenes_guardadas']}")
        
                # Estado de reentrenamiento
                estado = stats.get('reentrenamiento', {})
                if estado.get('necesita_reentrenar'):
                    st.warning("🔄 ¡Listo para reentrenar!")
                else:
                    progreso = estado.get('total_imagenes', 0)
                    st.progress(progreso / 50)
                    st.caption(f"Progreso: {progreso}/50 imágenes")
        else:
            st.error("❌ Servidor Local: Desconectado")
    
        # Botón de reset
        st.markdown("---")
        if st.button("🔄 Nueva Consulta", use_container_width=True):
            limpiar_sesion()
            st.rerun()
        
        # Debug info
        with st.expander("🔧 Debug Info"):
            st.write(f"**Session ID:** {st.session_state.get('session_id', 'None')}")
            st.write(f"**Intento:** {st.session_state.get('intento_actual', 0)}")
            st.write(f"**Descartadas:** {len(st.session_state.get('especies_descartadas', set()))}")
            if st.session_state.get('resultado_actual'):
                st.write(f"**Especie actual:** {st.session_state.resultado_actual.get('especie_predicha')}")

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()