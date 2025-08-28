import streamlit as st
from datetime import datetime
from utils.api_client import servidor_disponible, obtener_estadisticas
from ui.screens.upload import limpiar_sesion

def mostrar_sidebar(estado_sistema):
    """Muestra el sidebar con información del sistema"""
    with st.sidebar:
        st.markdown("### ℹ️ Información del Sistema")
        st.markdown(f"🌿 **Flora:** {estado_sistema.get('especies', 'N/A')}")
        st.markdown(f"⏱️ **Actualización:** {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        st.markdown("### 🔌 Esta pagina web es un proyecto de grado para el titulo profesional</div>")
        st.markdown("<div style='text-align: center'>Creado por:</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center'>Brandon Lizarralde</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center'>Angie Padilla</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center'>Directora de proyecto:</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center'>Yuli Alvarez</div>", unsafe_allow_html=True)
        
