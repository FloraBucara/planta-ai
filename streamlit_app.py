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
        'mensaje_inicio': None
    }
    
    # Inicializar cada estado si no existe
    for key, default_value in estados_default.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Ahora sí, intentar inicializar servicios
    if not st.session_state.firestore_initialized:
        st.session_state.firestore_initialized = inicializar_firestore_app()

def mostrar_header_limpio():
    """Muestra el header centrado sin estado del sistema"""
    logo_path = Path("assets/logo.png")
    
    # Centrar todo el header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("""
            <h1 style="
                text-align: center;
                background: linear-gradient(90deg, #2E8B57, #98FB98);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.2rem;
                font-weight: bold;
                margin: 1rem 0;
            ">
                🌱 BucaraFlora - Identificador de Plantas IA
            </h1>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style="
            text-align: center;
            color: #2e7d32;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 1rem;
        ">
            Sube una foto de tu planta y descubre qué especie es
        </p>
        """, unsafe_allow_html=True)

def mostrar_header():
    """Muestra header normal para pantallas que no son home"""
    logo_path = Path("assets/logo.png")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown('<h1 class="main-header">🌱 BucaraFlora - Identificador de Plantas IA</h1>', unsafe_allow_html=True)
    
    st.markdown("**Sube una foto de tu planta y descubre qué especie es**", unsafe_allow_html=True)
    
    # Solo mostrar estado en pantallas que no son home
    if st.session_state.get('firestore_initialized'):
        st.success("✅ Sistema conectado y listo")
    else:
        st.warning("⚠️ Algunas funciones pueden estar limitadas")

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    # SIEMPRE inicializar estado primero
    inicializar_estado()
    
    # Aplicar estilos CSS
    aplicar_estilos()
    
    # Verificar sistema
    estado_sistema = verificar_sistema_prediccion()
    
    if not estado_sistema["disponible"]:
        pantalla_error_sistema()
        return
    
    # Determinar qué pantalla mostrar
    if st.session_state.get('mostrar_top_especies', False):
        # Restaurar scroll para otras pantallas
        st.markdown("""
        <script>
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        </script>
        """, unsafe_allow_html=True)
        mostrar_header()
        pantalla_top_especies()
        mostrar_sidebar(estado_sistema)
    elif st.session_state.get('resultado_actual'):
        # Restaurar scroll para otras pantallas
        st.markdown("""
        <script>
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        </script>
        """, unsafe_allow_html=True)
        mostrar_header()
        pantalla_prediccion_feedback()
        mostrar_sidebar(estado_sistema)
    elif st.session_state.get('metodo_seleccionado') == "archivo":
        # Restaurar scroll para otras pantallas
        st.markdown("""
        <script>
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        </script>
        """, unsafe_allow_html=True)
        mostrar_header()
        pantalla_upload_archivo()
        mostrar_sidebar(estado_sistema)
    elif st.session_state.get('metodo_seleccionado') == "camara":
        # Restaurar scroll para otras pantallas
        st.markdown("""
        <script>
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        </script>
        """, unsafe_allow_html=True)
        mostrar_header()
        pantalla_tomar_foto()
        mostrar_sidebar(estado_sistema)
    else:
        # PANTALLA HOME - Solo header limpio, sin estado ni sidebar, SIN SCROLL
        mostrar_header_limpio()
        pantalla_seleccion_metodo()

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()