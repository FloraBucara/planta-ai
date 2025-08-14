import streamlit as st
import sys
from pathlib import Path

# Agregar directorio padre al path ANTES de importar configuración
sys.path.append(str(Path(__file__).parent))

from config import STREAMLIT_CONFIG
from utils.session_manager import session_manager, verificar_sistema_prediccion
from utils.firebase_config import firestore_manager

# Imports de UI
from ui.styles import aplicar_estilos, aplicar_clase_home_static
from ui.components import mostrar_header, mostrar_header_estatico
from ui.sidebar import mostrar_sidebar
from ui.screens.error import pantalla_error_sistema
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
        
        if "firebase" in st.secrets:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            if not firebase_admin._apps:
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
        'en_pantalla_home': True  # Nuevo estado para controlar el tipo de header
    }
    
    for key, default_value in estados_default.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    if not st.session_state.firestore_initialized:
        st.session_state.firestore_initialized = inicializar_firestore_app()

def es_pantalla_home():
    """Determina si estamos en la pantalla home"""
    return (
        not st.session_state.get('mostrar_top_especies', False) and
        not st.session_state.get('resultado_actual') and
        not st.session_state.get('metodo_seleccionado')
    )

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    inicializar_estado()
    
    # Determinar si estamos en home
    en_home = es_pantalla_home()
    st.session_state.en_pantalla_home = en_home
    
    # Aplicar estilos apropiados
    aplicar_estilos()
    
    if en_home:
        # PANTALLA HOME ESTÁTICA
        aplicar_clase_home_static()
        mostrar_header_estatico()
        
        # Verificar sistema
        estado_sistema = verificar_sistema_prediccion()
        
        if not estado_sistema["disponible"]:
            pantalla_error_sistema()
            return
        
        # Mostrar pantalla home estática
        pantalla_seleccion_metodo()
        
    else:
        # OTRAS PANTALLAS (con scroll normal)
        mostrar_header()
        
        # Verificar sistema
        estado_sistema = verificar_sistema_prediccion()
        
        if not estado_sistema["disponible"]:
            pantalla_error_sistema()
            return
        
        # Determinar qué pantalla mostrar
        if st.session_state.get('mostrar_top_especies', False):
            pantalla_top_especies()
        elif st.session_state.get('resultado_actual'):
            pantalla_prediccion_feedback()
        elif st.session_state.get('metodo_seleccionado') == "archivo":
            pantalla_upload_archivo()
        elif st.session_state.get('metodo_seleccionado') == "camara":
            pantalla_tomar_foto()
        else:
            # Esto no debería pasar, pero por seguridad volvemos a home
            st.session_state.metodo_seleccionado = None
            st.rerun()
        
        # Mostrar sidebar solo en pantallas que no son home
        mostrar_sidebar(estado_sistema)

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()