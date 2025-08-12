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

def crear_boton_personalizado(texto, clase_css, key, use_container_width=True):
    """
    Crea un botón personalizado con clase CSS específica
    
    Args:
        texto: Texto del botón
        clase_css: Clase CSS a aplicar
        key: Key única para el botón
        use_container_width: Si usar todo el ancho del contenedor
    
    Returns:
        bool: True si el botón fue clickeado
    """
    # Crear un ID único basado en la key
    button_id = f"btn_{key}"
    width_style = "width: 100%;" if use_container_width else ""
    
    # HTML del botón personalizado
    st.markdown(f"""
    <button 
        class="{clase_css}" 
        id="{button_id}"
        style="{width_style}"
        onclick="
            // Encontrar el botón oculto de Streamlit y clickearlo
            const hiddenButton = document.querySelector('[data-testid=\\'stButton\\'] button[data-baseweb=\\'button\\'][aria-label=\\'{key}\\']') || 
                                 document.querySelector('button[data-testid=\\'{key}\\']') ||
                                 document.querySelector('[key=\\'{key}\\'] button');
            if (hiddenButton) {{
                hiddenButton.click();
            }}
            
            // Efecto visual
            this.style.transform = 'translateY(-3px)';
            setTimeout(() => {{ 
                this.style.transform = this.classList.contains('btn-identify-plant') ? 'translateY(-3px)' : 'translateY(-2px)'; 
            }}, 150);
        "
    >
        {texto}
    </button>
    """, unsafe_allow_html=True)
    
    # Botón oculto que maneja la lógica de Streamlit
    # Usar un container invisible
    with st.container():
        st.markdown('<div style="height: 0; overflow: hidden;">', unsafe_allow_html=True)
        clicked = st.button("", key=key, help=f"Hidden button for {key}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    return clicked

def aplicar_estilos():
    """Aplica todos los estilos CSS con botones personalizados"""
    
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
        
        /* ==================== CLASES BASE PARA BOTONES PERSONALIZADOS ==================== */
        
        .btn-base {{
            display: block;
            width: 100%;
            padding: 1rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            font-weight: 600;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            color: white;
            margin: 0.5rem 0;
            font-family: "Source Sans Pro", sans-serif;
            line-height: 1.2;
        }}
        
        .btn-base:hover {{
            transform: translateY(-2px);
        }}
        
        .btn-base:active {{
            transform: translateY(0px);
        }}
        
        /* ==================== 1. BOTÓN IDENTIFICAR PLANTA ==================== */
        .btn-identify-plant {{
            background: linear-gradient(90deg, #00C851, #007E33) !important;
            padding: 1.2rem 2rem !important;
            border-radius: 0.75rem !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 6px 20px rgba(0, 200, 81, 0.4) !important;
        }}
        
        .btn-identify-plant:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 200, 81, 0.5) !important;
            background: linear-gradient(90deg, #007E33, #00C851) !important;
        }}
        
        /* ==================== 2. BOTONES PRINCIPALES ==================== */
        .btn-primary-green {{
            background: linear-gradient(90deg, #2E8B57, #228B22) !important;
            box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3) !important;
        }}
        
        .btn-primary-green:hover {{
            box-shadow: 0 6px 20px rgba(46, 139, 87, 0.4) !important;
            background: linear-gradient(90deg, #228B22, #2E8B57) !important;
        }}
        
        /* ==================== 3. BOTONES DE CONFIRMACIÓN ==================== */
        .btn-confirm {{
            background: linear-gradient(90deg, #28a745, #20c997) !important;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
        }}
        
        .btn-confirm:hover {{
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4) !important;
            background: linear-gradient(90deg, #20c997, #28a745) !important;
        }}
        
        /* ==================== 4. BOTONES NEGATIVOS ==================== */
        .btn-incorrect {{
            background: linear-gradient(90deg, #ff4757, #c44569) !important;
            box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3) !important;
        }}
        
        .btn-incorrect:hover {{
            box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4) !important;
            background: linear-gradient(90deg, #c44569, #ff4757) !important;
        }}
        
        /* ==================== 5. BOTONES EXPANDIBLES ==================== */
        .btn-expand-show {{
            background: linear-gradient(90deg, #48d668, #4CAF50) !important;
            padding: 0.8rem 1.2rem !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(72, 214, 104, 0.3) !important;
        }}
        
        .btn-expand-show:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 15px rgba(72, 214, 104, 0.4) !important;
            background: linear-gradient(90deg, #4CAF50, #48d668) !important;
        }}
        
        .btn-expand-hide {{
            background: linear-gradient(90deg, #1B5E20, #2E7D32) !important;
            padding: 0.8rem 1.2rem !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(27, 94, 32, 0.3) !important;
        }}
        
        .btn-expand-hide:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 15px rgba(27, 94, 32, 0.4) !important;
            background: linear-gradient(90deg, #2E7D32, #1B5E20) !important;
        }}
        
        /* ==================== 6. BOTÓN REGRESAR ==================== */
        .btn-back {{
            background: linear-gradient(90deg, #28a745, #6c757d) !important;
            padding: 0.85rem 1.5rem !important;
            font-weight: 600 !important;
            box-shadow: 0 3px 12px rgba(40, 167, 69, 0.25) !important;
        }}
        
        .btn-back:hover {{
            box-shadow: 0 5px 18px rgba(40, 167, 69, 0.35) !important;
            background: linear-gradient(90deg, #6c757d, #28a745) !important;
        }}
        
        /* ==================== 7. BOTONES SECUNDARIOS ==================== */
        .btn-secondary {{
            background: linear-gradient(90deg, #6c757d, #5a6268) !important;
            padding: 0.75rem 1.25rem !important;
            font-weight: 500 !important;
            box-shadow: 0 3px 10px rgba(108, 117, 125, 0.3) !important;
        }}
        
        .btn-secondary:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4) !important;
            background: linear-gradient(90deg, #5a6268, #6c757d) !important;
        }}
        
        /* ==================== BOTONES STREAMLIT ORIGINALES (FALLBACK) ==================== */
        
        /* Por si quedan botones normales de Streamlit */
        div[data-testid="stButton"] > button[kind="primary"] {{
            background: linear-gradient(90deg, #2E8B57, #228B22) !important;
            color: white !important;
            border: none !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        div[data-testid="stButton"] > button[kind="secondary"] {{
            background: linear-gradient(90deg, #ff4757, #c44569) !important;
            color: white !important;
            border: none !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        /* ==================== OTROS ESTILOS ==================== */
        
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