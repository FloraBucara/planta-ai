import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import STREAMLIT_CONFIG
from utils.session_manager import session_manager, verificar_sistema_prediccion
from utils.firebase_config import firestore_manager

from ui.styles import aplicar_estilos
from ui.components import mostrar_header
from ui.sidebar import mostrar_sidebar
from ui.screens.error import pantalla_error_sistema
from ui.screens.splash import pantalla_splash
from ui.screens.home import pantalla_seleccion_metodo
from ui.screens.upload import pantalla_upload_archivo
from ui.screens.camera import pantalla_tomar_foto
from ui.screens.prediction import pantalla_prediccion_feedback
from ui.screens.selection import pantalla_top_especies

st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

@st.cache_resource
def inicializar_firestore_app():
    """Inicializa Firestore una sola vez usando cache con reconexión automática"""
    try:
        print("🔥 Inicializando Firestore...")
        
        if "firebase" in st.secrets:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            try:
                if firebase_admin._apps:
                    test_db = firestore.client()
                    test_db.collection('test').limit(1).get()
                    print("✅ Conexión Firebase existente válida")
                    
                    firestore_manager.db = test_db
                    firestore_manager.initialized = True
                    return True
            except Exception as conn_error:
                print(f"⚠️ Conexión existente inválida, reinicializando: {conn_error}")
                firebase_admin._apps.clear()
            
            try:
                firebase_creds = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_creds)
                app = firebase_admin.initialize_app(cred)
                
                db = firestore.client()
                db.collection('sistema_test').limit(1).get()
                
                firestore_manager.db = db
                firestore_manager.initialized = True
                print("✅ Firestore reinicializado exitosamente desde secrets")
                return True
                
            except Exception as init_error:
                print(f"❌ Error reinicializando Firebase: {init_error}")
                return False
        else:
            print("❌ No se encontraron secrets de Firebase")
            return False
            
    except Exception as e:
        print(f"❌ Excepción general inicializando Firestore: {e}")
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
        'splash_completado': False,
        'servidor_abierto': False,
        'servidor_clicked': False
    }
    
    for key, default_value in estados_default.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    if not st.session_state.firestore_initialized:
        st.session_state.firestore_initialized = inicializar_firestore_app()

def main():
    """Función principal de la aplicación"""
    inicializar_estado()
    
    aplicar_estilos()
    
    if not st.session_state.get('splash_completado', False):
        pantalla_splash()
        return
    
    mostrar_header()
    
    estado_sistema = verificar_sistema_prediccion()
    
    if not estado_sistema["disponible"]:
        pantalla_error_sistema()
        return
    
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
    
    mostrar_sidebar(estado_sistema)

if __name__ == "__main__":
    main()