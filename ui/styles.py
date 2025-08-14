import streamlit as st
from pathlib import Path
import base64

def get_base64_image(image_path):
    """Convierte imagen a base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def aplicar_estilos():
    """Aplica todos los estilos CSS incluyendo bloqueo de scroll"""
    
    # Obtener imagen de fondo
    fondo_path = Path("assets/fondo.png")
    fondo_base64 = get_base64_image(fondo_path) if fondo_path.exists() else None
    
    # CSS con imagen de fondo
    css_fondo = ""
    if fondo_base64:
        css_fondo = f"""
        .stApp {{
            background-image: url("data:image/png;base64,{fondo_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        """
    
    st.markdown(f"""
    <style>
        {css_fondo}
        
        /* BLOQUEAR SCROLL COMPLETAMENTE */
        html, body {{
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }}
        
        .stApp {{
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }}
        
        .main {{
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }}
        
        .main .block-container {{
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 0 !important;
            backdrop-filter: blur(10px);
        }}
        
        /* Ocultar elementos de Streamlit que causan scroll */
        .stDeployButton {{
            display: none !important;
        }}
        
        .stDecoration {{
            display: none !important;
        }}
        
        .stToolbar {{
            display: none !important;
        }}
        
        .stStatusWidget {{
            display: none !important;
        }}
        
        /* Ocultar scrollbars completamente */
        ::-webkit-scrollbar {{
            width: 0px !important;
            background: transparent !important;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: transparent !important;
        }}
        
        * {{
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }}
        
        /* Header principal centrado */
        .main-header {{
            text-align: center;
            padding: 1rem 0;
            background: linear-gradient(90deg, #2E8B57, #98FB98);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            position: fixed;
            top: 10%;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            width: 100%;
        }}
        
        /* Contenedor de botones centrado */
        .button-container {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1001;
            width: 400px;
            max-width: 90vw;
        }}
        
        /* Estilos de botones mejorados */
        .stButton > button {{
            width: 100% !important;
            height: 60px !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            border: 2px solid #2e7d32 !important;
            background: linear-gradient(135deg, #4caf50, #2e7d32) !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3) !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
            background: linear-gradient(135deg, #66bb6a, #388e3c) !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(0px) !important;
            box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3) !important;
        }}
        
        /* Mensajes de notificación centrados */
        .notification-message {{
            position: fixed;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            z-index: 1000;
            max-width: 80vw;
        }}
        
        /* Sidebar con transparencia */
        section[data-testid="stSidebar"] > div {{
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            overflow: hidden !important;
            height: 100vh !important;
        }}
        
        section[data-testid="stSidebar"] {{
            overflow: hidden !important;
            height: 100vh !important;
        }}
        
        /* Ocultar elementos innecesarios cuando estamos en home */
        .home-static .stProgress {{
            display: none !important;
        }}
        
        .home-static .stSpinner {{
            display: none !important;
        }}
        
        /* Asegurar que los elementos fijos no se muevan */
        .static-element {{
            position: fixed !important;
            z-index: 1000 !important;
        }}
        
        /* Prevenir interacciones de scroll */
        body, html {{
            touch-action: none !important;
            -webkit-touch-callout: none !important;
            -webkit-user-select: none !important;
            -khtml-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }}
        
        /* Solo permitir selección en elementos específicos */
        .stButton, .stSelectbox, .stTextInput {{
            -webkit-user-select: auto !important;
            -moz-user-select: auto !important;
            -ms-user-select: auto !important;
            user-select: auto !important;
        }}
        
        /* Efectos visuales adicionales */
        .glass-effect {{
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(20px) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
        }}
        
        /* Animaciones sutiles */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.6s ease-out !important;
        }}
        
        /* Responsivo para móviles */
        @media (max-width: 768px) {{
            .main-header {{
                font-size: 1.8rem !important;
                top: 15% !important;
            }}
            
            .button-container {{
                width: 90vw !important;
            }}
            
            .stButton > button {{
                height: 50px !important;
                font-size: 1rem !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

def aplicar_clase_home_static():
    """Aplica clase CSS específica para la página home"""
    st.markdown("""
    <script>
        document.body.classList.add('home-static');
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';
    </script>
    """, unsafe_allow_html=True)