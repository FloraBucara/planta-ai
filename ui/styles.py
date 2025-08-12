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
    """Aplica todos los estilos CSS de la aplicación - VERSIÓN QUE FUNCIONA"""
    
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
        
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }}
        
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
        
        /* ==================== ESTILOS GENERALES DE BOTONES ==================== */
        .stButton > button {{
            border: none !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
        }}
        
        /* ==================== BOTONES POR TEXTO (FUNCIONA SIEMPRE) ==================== */
        
        /* BOTÓN IDENTIFICAR PLANTA - Verde llamativo */
        .stButton > button:has-text("🔍 Identificar Planta"),
        .stButton > button[aria-label*="Identificar"],
        button:contains("Identificar Planta") {{
            background: linear-gradient(90deg, #00C851, #007E33) !important;
            color: white !important;
            padding: 1.2rem 2rem !important;
            border-radius: 0.75rem !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            box-shadow: 0 6px 20px rgba(0, 200, 81, 0.4) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }}
        
        .stButton > button:has-text("🔍 Identificar Planta"):hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 200, 81, 0.5) !important;
            background: linear-gradient(90deg, #007E33, #00C851) !important;
        }}
        
        /* BOTONES PRINCIPALES - Verde estándar */
        .stButton > button:has-text("📁 Subir imagen"),
        .stButton > button:has-text("📷 Tomar foto") {{
            background: linear-gradient(90deg, #2E8B57, #228B22) !important;
            color: white !important;
            padding: 1rem 1.5rem !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3) !important;
        }}
        
        .stButton > button:has-text("📁 Subir imagen"):hover,
        .stButton > button:has-text("📷 Tomar foto"):hover {{
            box-shadow: 0 6px 20px rgba(46, 139, 87, 0.4) !important;
            background: linear-gradient(90deg, #228B22, #2E8B57) !important;
        }}
        
        /* BOTONES DE CONFIRMACIÓN - Verde degradado */
        .stButton > button:has-text("✅ ¡Sí, es correcta!"),
        .stButton > button:has-text("✅ ¡Es esta planta!") {{
            background: linear-gradient(90deg, #28a745, #20c997) !important;
            color: white !important;
            padding: 1rem 1.5rem !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
        }}
        
        .stButton > button:has-text("✅ ¡Sí, es correcta!"):hover,
        .stButton > button:has-text("✅ ¡Es esta planta!"):hover {{
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4) !important;
            background: linear-gradient(90deg, #20c997, #28a745) !important;
        }}
        
        /* BOTONES NEGATIVOS - Rojo degradado NOTORIO */
        .stButton > button:has-text("❌ No, es incorrecta"),
        .stButton > button:has-text("❌ No es ninguna de estas") {{
            background: linear-gradient(90deg, #ff4757, #c44569) !important;
            color: white !important;
            padding: 1rem 1.5rem !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3) !important;
        }}
        
        .stButton > button:has-text("❌ No, es incorrecta"):hover,
        .stButton > button:has-text("❌ No es ninguna de estas"):hover {{
            box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4) !important;
            background: linear-gradient(90deg, #c44569, #ff4757) !important;
        }}
        
        /* BOTONES EXPANDIBLES */
        .stButton > button:has-text("▼ Ver información"),
        .stButton > button[aria-label*="Ver información"] {{
            background: linear-gradient(90deg, #48d668, #4CAF50) !important;
            color: white !important;
            padding: 0.8rem 1.2rem !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(72, 214, 104, 0.3) !important;
        }}
        
        .stButton > button:has-text("▲ Ocultar información") {{
            background: linear-gradient(90deg, #1B5E20, #2E7D32) !important;
            color: white !important;
            padding: 0.8rem 1.2rem !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(27, 94, 32, 0.3) !important;
        }}
        
        .stButton > button:has-text("▼ Ver información"):hover,
        .stButton > button:has-text("▲ Ocultar información"):hover {{
            transform: translateY(-1px) !important;
        }}
        
        /* BOTÓN REGRESAR - Verde + Gris */
        .stButton > button:has-text("← Regresar") {{
            background: linear-gradient(90deg, #28a745, #6c757d) !important;
            color: white !important;
            padding: 0.85rem 1.5rem !important;
            font-size: 1rem !important;
            box-shadow: 0 3px 12px rgba(40, 167, 69, 0.25) !important;
        }}
        
        .stButton > button:has-text("← Regresar"):hover {{
            box-shadow: 0 5px 18px rgba(40, 167, 69, 0.35) !important;
            background: linear-gradient(90deg, #6c757d, #28a745) !important;
        }}
        
        /* BOTÓN NUEVA CONSULTA - Gris degradado */
        .stButton > button:has-text("🔄 Nueva Consulta") {{
            background: linear-gradient(90deg, #6c757d, #5a6268) !important;
            color: white !important;
            padding: 0.75rem 1.25rem !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(108, 117, 125, 0.3) !important;
        }}
        
        .stButton > button:has-text("🔄 Nueva Consulta"):hover {{
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