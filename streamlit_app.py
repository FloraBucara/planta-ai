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
from ui.styles import aplicar_estilos
from ui.components import mostrar_header
from ui.screens.error import pantalla_error_sistema
from ui.screens.home import pantalla_seleccion_metodo
from ui.screens.upload import pantalla_upload_archivo
from ui.screens.camera import pantalla_tomar_foto

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
    from utils.session_manager import session_manager, verificar_sistema_prediccion
    from utils.firebase_config import obtener_info_planta_basica, firestore_manager
except ImportError as e:
    st.error(f"❌ Error importando módulos: {e}")
    st.stop()

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
    
    print("ℹ️ Servidor de imágenes local no activo")
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


# ==================== FUNCIONES AUXILIARES MEJORADAS ====================

def mostrar_info_planta_completa(info_planta):
    """
    Muestra la información completa de la planta de forma visualmente atractiva
    """
    datos = info_planta.get('datos', {})
    fuente = info_planta.get('fuente', 'desconocido')
    
    # SIN contenedor que genera barra gris
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
    """Muestra la primera imagen disponible de la especie desde el servidor"""
    try:
        from utils.api_client import SERVER_URL
        from urllib.parse import quote
        
        if not SERVER_URL:
            return
        
        # CONVERTIR A FORMATO DE CARPETA ANTES DE ENVIAR
        nombre_carpeta = nombre_cientifico.replace(' ', '_')
        
        # Codificar URL (ahora ya sin espacios)
        especie_encoded = quote(nombre_carpeta)
        imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
        
        # Mostrar imagen directamente
        try:
            st.image(
                imagen_url,
                caption="Imagen de referencia",
                use_container_width=True
            )
        except Exception as e:
            pass
            
    except Exception as e:
        pass
        
def mostrar_imagen_referencia_sin_barra(nombre_cientifico):
    """Muestra imagen de referencia SIN la barra superior molesta"""
    try:
        from utils.api_client import SERVER_URL
        from urllib.parse import quote
        
        if not SERVER_URL:
            return
        
        # CONVERTIR A FORMATO DE CARPETA
        nombre_carpeta = nombre_cientifico.replace(' ', '_')
        especie_encoded = quote(nombre_carpeta)
        imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
        
        # Mostrar imagen SIN caption para evitar barra
        try:
            st.image(
                imagen_url,
                use_container_width=True
            )
            # Caption manual sin barra
            st.markdown(
                '<p style="text-align: center; color: gray; font-size: 0.8em; margin-top: 0.5rem;">Imagen de referencia</p>',
                unsafe_allow_html=True
            )
        except:
            pass
            
    except:
        pass
       

# ==================== PANTALLAS PRINCIPALES ====================

def pantalla_prediccion_feedback():
    """Pantalla de predicción con botones de feedback"""
    resultado = st.session_state.resultado_actual
    
    # Mostrar imagen del usuario
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.imagen_actual, caption="Tu planta", use_container_width=True)
    
    # Card de predicción
    st.markdown('<div>', unsafe_allow_html=True)
    
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
                # Enviar feedback positivo
                respuesta = enviar_feedback(
                    imagen_pil=st.session_state.imagen_actual,
                    session_id=st.session_state.session_id,
                    especie_predicha=resultado["especie_predicha"],
                    confianza=resultado["confianza"],
                    feedback_tipo="correcto",
                    especie_correcta=resultado["especie_predicha"]  # Misma especie
                )
            
                if respuesta.get("success"):
                    st.success("🎉 ¡Gracias por confirmar!")
                    st.success("✅ Imagen guardada para mejorar el modelo")
                
                    # Mostrar progreso de reentrenamiento
                    if respuesta.get("progreso"):
                        st.info(f"📊 Progreso para reentrenamiento: {respuesta['progreso']}%")
                    
                    if respuesta.get("necesita_reentrenamiento"):
                        st.warning("🚀 ¡Suficientes imágenes para reentrenamiento!")
                else:
                    st.warning(f"⚠️ {respuesta.get('mensaje', 'Error guardando feedback')}")
            
                st.balloons()
                time.sleep(2)
            
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
    """Pantalla de selección manual de las top 5 especies - VERSIÓN EXPANDIBLE"""
    st.markdown("### 🤔 ¿Tal vez sea una de estas?")
    st.info("Selecciona la especie correcta de las siguientes opciones:")
    
    # Obtener top 5 especies
    with st.spinner("🔍 Buscando especies similares..."):
        especies_excluir = list(st.session_state.especies_descartadas)
        top_especies = session_manager.predictor.obtener_top_especies(
            st.session_state.imagen_actual,
            cantidad=5,
            especies_excluir=especies_excluir
        )
    
    if not top_especies:
        st.error("❌ Error obteniendo especies similares")
        return
    
    # Mostrar imagen original
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.imagen_actual, caption="Tu planta", use_container_width=True)
    
    st.markdown("---")
    
    # Mostrar las 5 especies con información expandible
    for i, especie_data in enumerate(top_especies):
        # Buscar información de la especie
        info_planta = buscar_info_planta_firestore(especie_data["especie"])
        datos = info_planta.get('datos', {})
        
        # Container para cada especie (SIN BARRA SUPERIOR)
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 3])
            
            with col1:
                # Número de opción
                st.markdown(f"### {i+1}")
            
            with col2:
                # Imagen de referencia (SIN BARRA SUPERIOR)
                mostrar_imagen_referencia_sin_barra(especie_data["especie"])
            
            with col3:
                # Información básica
                st.markdown(f"**{datos.get('nombre_comun', 'Nombre no disponible')}**")
                st.markdown(f"*{especie_data['especie']}*")
                
                # Barra de confianza
                porcentaje = int(especie_data["confianza"] * 100)
                st.markdown(f"""
                <div class="confidence-bar" style="height: 10px; background: #e9ecef; border-radius: 5px; margin: 0.5rem 0; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: {porcentaje}%; transition: width 0.3s ease;"></div>
                </div>
                <p style="text-align: center; font-size: 0.9em; margin: 0;">
                    Confianza: {porcentaje}%
                </p>
                """, unsafe_allow_html=True)
                
                # Botón expandir/contraer información
                expand_key = f"expand_{i}"
                if st.button(
                    "▼ Ver información completa" if not st.session_state.get(expand_key, False) else "▲ Ocultar información",
                    key=f"toggle_{i}",
                    type="secondary"
                ):
                    st.session_state[expand_key] = not st.session_state.get(expand_key, False)
                    st.rerun()
                
                # Mostrar información expandida si está activada
                if st.session_state.get(expand_key, False):
                    st.markdown("---")
                    
                    # Información detallada
                    if info_planta.get('fuente') == 'firestore':
                        st.markdown("*✅ Información verificada de la base de datos*")
                    else:
                        st.info("ℹ️ Información básica disponible")
                    
                    # Descripción
                    if datos.get('descripcion'):
                        st.markdown("**📝 Descripción:**")
                        st.write(datos['descripcion'])
                    
                    # Taxonomía
                    if datos.get('taxonomia') and info_planta.get('fuente') == 'firestore':
                        taxonomia = datos['taxonomia']
                        if taxonomia:
                            st.markdown("**🧬 Clasificación Taxonómica:**")
                            col_tax1, col_tax2 = st.columns(2)
                            
                            with col_tax1:
                                st.write(f"• **Reino:** {taxonomia.get('reino', 'N/A')}")
                                st.write(f"• **Filo:** {taxonomia.get('filo', 'N/A')}")
                                st.write(f"• **Clase:** {taxonomia.get('clase', 'N/A')}")
                            
                            with col_tax2:
                                st.write(f"• **Orden:** {taxonomia.get('orden', 'N/A')}")
                                st.write(f"• **Familia:** {taxonomia.get('familia', 'N/A')}")
                                st.write(f"• **Género:** {taxonomia.get('genero', 'N/A')}")
                    
                    # Información adicional                   
                    if datos.get('fuente'):
                        st.markdown(f"**📚 Fuente:** {datos['fuente']}")
                    
                    st.markdown("---")
                    
                    # BOTÓN "ES ESTA" AL FINAL DE LA INFORMACIÓN EXPANDIDA
                    if st.button(
                        "✅ ¡Es esta planta!",
                        key=f"select_final_{i}",
                        type="primary",
                        use_container_width=True
                    ):
                        with st.spinner("💾 Guardando tu selección..."):
                            # Enviar feedback de corrección
                            respuesta = enviar_feedback(
                                imagen_pil=st.session_state.imagen_actual,
                                session_id=st.session_state.session_id,
                                especie_predicha=st.session_state.resultado_actual["especie_predicha"],
                                confianza=st.session_state.resultado_actual["confianza"],
                                feedback_tipo="corregido",
                                especie_correcta=especie_data["especie"]
                            )

                            if respuesta.get("success"):
                                st.success(f"🎉 ¡Gracias! Has identificado tu planta como **{datos.get('nombre_comun', especie_data['especie'])}**")
                                st.success("✅ Imagen guardada para mejorar el modelo")
                        
                                # Mostrar progreso
                                if respuesta.get("progreso"):
                                    st.info(f"📊 Progreso para reentrenamiento: {respuesta['progreso']}%")
                        
                                if respuesta.get("necesita_reentrenamiento"):
                                    st.warning("🚀 ¡Suficientes imágenes para reentrenamiento!")
                            else:
                                st.warning(f"⚠️ {respuesta.get('mensaje', 'Error guardando feedback')}")

                            st.balloons()
                            time.sleep(2)

                            # Limpiar estados de botones y volver al inicio
                            for j in range(5):
                                for state_key in [f'expand_{j}', f'boton_presionado_{j}']:
                                    if state_key in st.session_state:
                                        del st.session_state[state_key]
                            
                            limpiar_sesion()
                            st.rerun()
        
        # Separador entre especies
        st.markdown("---")
    
    # Opción "No es ninguna de estas"
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("❌ No es ninguna de estas", type="secondary", use_container_width=True):
            # Establecer mensaje para mostrar en inicio
            st.session_state.mensaje_inicio = "no_identificada"
            
            # Limpiar y volver al inicio
            limpiar_sesion()
            st.rerun()

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    # SIEMPRE inicializar estado primero
    inicializar_estado()
    
    # Aplicar estilos CSS
    aplicar_estilos()
    
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
    elif st.session_state.get('metodo_seleccionado') == "archivo":
        pantalla_upload_archivo()
    elif st.session_state.get('metodo_seleccionado') == "camara":
        pantalla_tomar_foto()
    else:
        pantalla_seleccion_metodo()
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### ℹ️ Información del Sistema")
        st.markdown(f"🌿 **Especies:** {estado_sistema.get('especies', 'N/A')}")
        st.markdown(f"⏱️ **Actualización:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Estado de servicios
        st.markdown("---")
        st.markdown("### 🔌 Estado de Servicios")
        
        # Estado del sistema (simplificado)
        if st.session_state.get('firestore_initialized', False):
            st.success("✅ Sistema: Completamente funcional")
    
            # Mostrar estadísticas solo si el servidor está disponible
            if servidor_disponible():
                stats = obtener_estadisticas()
                if stats:
                    st.markdown("📊 **Estadísticas del sistema:**")
                    st.write(f"• Feedback total: {stats.get('feedback_total', 0)}")
                    st.write(f"• Imágenes procesadas: {stats.get('imagenes_guardadas', 0)}")
        else:
            st.info("ℹ️ Sistema funcionando en modo básico")
    
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