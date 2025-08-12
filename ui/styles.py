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
    """Aplica todos los estilos CSS de la aplicación incluyendo fondo"""
    
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
        
        /* Hacer los contenedores semi-transparentes para que se vea el fondo */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }}
        
        /* Sidebar con transparencia */
        section[data-testid="stSidebar"] > div {{
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }}
        """
    
    st.markdown(f"""
    <style>
        {css_fondo}
        
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
        }}
        
        /* ==================== BOTONES PRINCIPALES ==================== */
        
        /* Botón Identificar Planta - Verde degradado llamativo */
        .stButton > button[key="btn_identify_plant"] {{
            background: linear-gradient(90deg, #00C851, #007E33) !important;
            color: white !important;
            border: none !important;
            padding: 1.2rem 2rem !important;
            border-radius: 0.75rem !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 20px rgba(0, 200, 81, 0.4) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }}
        
        .stButton > button[key="btn_identify_plant"]:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 200, 81, 0.5) !important;
            background: linear-gradient(90deg, #007E33, #00C851) !important;
        }}
        
        /* Botones principales sin cambios - Verde estándar */
        .stButton > button[key="btn_upload"], 
        .stButton > button[key="btn_camera"] {{
            background: linear-gradient(90deg, #2E8B57, #228B22) !important;
            color: white !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3) !important;
        }}
        
        .stButton > button[key="btn_upload"]:hover,
        .stButton > button[key="btn_camera"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(46, 139, 87, 0.4) !important;
            background: linear-gradient(90deg, #228B22, #2E8B57) !important;
        }}
        
        /* ==================== BOTONES DE CONFIRMACIÓN ==================== */
        
        /* Botones "Sí, es correcta" y "Es esta planta" - Verde degradado */
        .stButton > button[key="btn_correct"],
        .stButton > button[key^="btn_confirm_species"] {{
            background: linear-gradient(90deg, #28a745, #20c997) !important;
            color: white !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
        }}
        
        .stButton > button[key="btn_correct"]:hover,
        .stButton > button[key="btn_confirm_species"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4) !important;
            background: linear-gradient(90deg, #20c997, #28a745) !important;
        }}
        
        /* ==================== BOTONES NEGATIVOS ==================== */
        
        /* Botones "No, es incorrecta" y "No es ninguna de estas" - Rojo degradado NOTORIO */
        .stButton > button[key="btn_incorrect"],
        .stButton > button[key="btn_none_of_these"] {{
            background: linear-gradient(90deg, #ff4757, #c44569) !important;
            color: white !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3) !important;
        }}
        
        .stButton > button[key="btn_incorrect"]:hover,
        .stButton > button[key="btn_none_of_these"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4) !important;
            background: linear-gradient(90deg, #c44569, #ff4757) !important;
        }}
        
        /* ==================== BOTONES EXPANDIBLES ==================== */
        
        /* Botón "Ver información completa" - Verde claro */
        .stButton > button[key^="btn_expand_show"] {{
            background: linear-gradient(90deg, #48d668, #4CAF50) !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 1.2rem !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 3px 10px rgba(72, 214, 104, 0.3) !important;
        }}
        
        .stButton > button[key="btn_expand_show"]:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 15px rgba(72, 214, 104, 0.4) !important;
            background: linear-gradient(90deg, #4CAF50, #48d668) !important;
        }}
        
        /* Botón "Ocultar información" - Verde oscuro */
        .stButton > button[key^="btn_expand_hide"] {{
            background: linear-gradient(90deg, #1B5E20, #2E7D32) !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 1.2rem !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 3px 10px rgba(27, 94, 32, 0.3) !important;
        }}
        
        .stButton > button[key="btn_expand_hide"]:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 15px rgba(27, 94, 32, 0.4) !important;
            background: linear-gradient(90deg, #2E7D32, #1B5E20) !important;
        }}
        
        /* ==================== BOTÓN REGRESAR ==================== */

        /* Botón "Regresar" - Verde + Gris (AMBAS PANTALLAS) */
        .stButton > button[key="btn_back"],
        .stButton > button[key="btn_back_camera"] {{
            background: linear-gradient(90deg, #28a745, #6c757d) !important;
            color: white !important;
            border: none !important;
            padding: 0.85rem 1.5rem !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 3px 12px rgba(40, 167, 69, 0.25) !important;
        }}

        .stButton > button[key="btn_back"]:hover,
        .stButton > button[key="btn_back_camera"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 18px rgba(40, 167, 69, 0.35) !important;
            background: linear-gradient(90deg, #6c757d, #28a745) !important;
        }}
        
        /* ==================== BOTONES SECUNDARIOS ==================== */
        
        /* Otros botones secundarios - Gris degradado */
        .stButton > button[key="btn_new_query"] {{
            background: linear-gradient(90deg, #6c757d, #5a6268) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 1.25rem !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 3px 10px rgba(108, 117, 125, 0.3) !important;
        }}
        
        .stButton > button[key="btn_new_query"]:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4) !important;
            background: linear-gradient(90deg, #5a6268, #6c757d) !important;
        }}
        
        /* ==================== OTROS ESTILOS EXISTENTES ==================== */
        
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
            gap: 2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 1rem 2rem;
            border-radius: 8px 8px 0 0;
        }}
    </style>
    """, unsafe_allow_html=True)