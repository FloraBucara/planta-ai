import streamlit as st
from pathlib import Path
import base64

def get_base64_image(image_path):
    """Convierte una imagen local a formato base64 para usar en CSS."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def aplicar_estilos():
    """Aplica todos los estilos CSS de la aplicación incluyendo fondo y elementos de interfaz."""
    
    fondo_path = Path("assets/fondo.png")
    fondo_base64 = get_base64_image(fondo_path) if fondo_path.exists() else None
    
    css_fondo = ""
    if fondo_base64:
        css_fondo = f"""
        .stApp {{
            background-image: url("data:image/png;base64,{fondo_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            min-height: 100vh;
        }}
        
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        section[data-testid="stSidebar"] > div {{
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }}
        
        .splash-container {{
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .splash-card {{
            background: rgba(248, 249, 250, 0.95) !important;
            backdrop-filter: blur(5px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .streamlit-expanderHeader {{
            background-color: rgba(248, 249, 250, 0.95) !important;
        }}
        
        .streamlit-expanderContent {{
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}
        """
    
    st.markdown(f"""
    <style>
        {css_fondo}
        
        .main .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
        }}
        
        h1, h2, h3 {{
            margin-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }}
        
        .stImage {{
            margin-top: -1rem !important;
            margin-bottom: 0rem !important;
        }}
        
        .stMarkdown {{
            margin-bottom: 0.25rem;
        }}
        
        .main-header {{
            text-align: center;
            padding: 0.25rem 0;
            background: linear-gradient(90deg, #2E8B57, #98FB98);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }}
        
        .prediction-card {{
            background: rgba(248, 249, 250, 0.95);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }}
        
        .info-card {{
            background: rgba(232, 245, 233, 0.95);
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }}
        
        .species-card {{
            background: rgba(240, 248, 255, 0.95);
            padding: 1rem;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            margin: 0.5rem 0;
            text-align: center;
            transition: all 0.3s;
        }}
        
        .species-card:hover {{
            border-color: #28a745;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .debug-info {{
            background: rgba(255, 243, 205, 0.95);
            color: #856404;
            padding: 0.75rem;
            border-radius: 5px;
            border: 1px solid #ffeaa7;
            margin: 0.5rem 0;
            font-size: 0.9em;
        }}
        
        .error-message {{
            background: rgba(248, 215, 218, 0.95);
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
            margin: 1rem 0;
        }}
        
        .success-message {{
            background: rgba(212, 237, 218, 0.95);
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            border: 1px solid #c3e6cb;
            margin: 1rem 0;
        }}
        
        .firestore-status {{
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }}
        
        .firestore-connected {{
            background: rgba(212, 237, 218, 0.95);
            border: 1px solid #c3e6cb;
            color: #155724;
        }}
        
        .firestore-disconnected {{
            background: rgba(248, 215, 218, 0.95);
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
        
        .confidence-bar {{
            background: rgba(233, 236, 239, 0.95);
            border-radius: 10px;
            height: 20px;
            margin: 0.5rem 0;
            overflow: hidden;
        }}
        
        .confidence-fill {{
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .camera-info {{
            background: rgba(227, 242, 253, 0.95);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            margin: 1rem 0;
        }}
        
        .upload-info {{
            background: rgba(243, 229, 245, 0.95);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #9c27b0;
            margin: 1rem 0;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.75rem 1.5rem;
            border-radius: 8px 8px 0 0;
        }}
        
        .stColumns > div {{
            padding: 0 0.25rem;
        }}
        
        .stButton > button {{
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0 !important;
            border-radius: 8px !important;
            width: 85% !important;
            max-width: 300px !important;
        }}
        
        .stButton {{
            margin-bottom: 0.5rem !important;
            display: flex !important;
            justify-content: center !important;
        }}
    </style>
    """, unsafe_allow_html=True)