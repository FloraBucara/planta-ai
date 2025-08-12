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
    """CSS SUPER SIMPLE - Debe funcionar 100%"""
    
    st.markdown("""
    <style>
        /* TEST: Cambiar TODOS los botones primary a ROJO para verificar que funciona */
        div[data-testid="stButton"] > button[kind="primary"] {
            background: red !important;
            color: white !important;
            border: 2px solid blue !important;
            font-size: 20px !important;
        }
        
        /* TEST: Cambiar TODOS los botones secondary a VERDE para verificar que funciona */
        div[data-testid="stButton"] > button[kind="secondary"] {
            background: green !important;
            color: white !important;
            border: 2px solid yellow !important;
            font-size: 20px !important;
        }
        
        /* TEST: Hacer TODOS los botones más grandes */
        .stButton > button {
            height: 60px !important;
            font-weight: bold !important;
        }
    </style>
    """, unsafe_allow_html=True)