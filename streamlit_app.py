import streamlit as st
import sys
from pathlib import Path

# Agregar directorio padre al path ANTES de importar configuración
sys.path.append(str(Path(__file__).parent))

from config import STREAMLIT_CONFIG
from utils.session_manager import session_manager, verificar_sistema_prediccion
from utils.firebase_config import firestore_manager

# Imports de UI
from ui.styles import aplicar_estilos
from ui.components import mostrar_header
from ui.sidebar import mostrar_sidebar
from ui.screens.error import pantalla_error_sistema
from ui.screens.splash import pantalla_splash  # NUEVA PANTALLA
from ui.screens.home import pantalla_seleccion_metodo
from ui.screens.upload import pantalla_upload_archivo
from ui.screens.camera import pantalla_tomar_foto
from ui.screens.prediction import pantalla_prediccion_feedback
from ui.screens.selection import pantalla_top_especies

# ==================== CONFIGURACIÓN DE LA PÁGINA (DEBE SER PRIMERO) ====================
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

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
        'mensaje_inicio': None,
        'splash_completado': False  # NUEVO ESTADO PARA SPLASH
    }
    
    # Inicializar cada estado si no existe
    for key, default_value in estados_default.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Ahora sí, intentar inicializar servicios
    if not st.session_state.firestore_initialized:
        st.session_state.firestore_initialized = inicializar_firestore_app()

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    # SIEMPRE inicializar estado primero
    inicializar_estado()
    
    # Aplicar estilos CSS
    aplicar_estilos()
    
    # NUEVA LÓGICA: Verificar si debe mostrar splash
    if not st.session_state.get('splash_completado', False):
        pantalla_splash()
        return  # No mostrar nada más hasta completar splash
    
    # Mostrar header (solo después del splash)
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
    
    # Mostrar sidebar (solo después del splash)
    mostrar_sidebar(estado_sistema)

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()