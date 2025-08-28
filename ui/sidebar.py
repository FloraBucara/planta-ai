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
        st.markdown("### 🔌 Esta pagina web " \
        "  es un proyecto de grado para" \
        "  el titulo profesional")
        st.markdown("---")
        st.markdown("Creado por Brando Lizarralde Y Angie Padilla")
        st.markdown("Directora de proyecto: Yuli Alvarez")
        
