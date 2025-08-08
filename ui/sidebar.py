import streamlit as st
from datetime import datetime
from utils.api_client import servidor_disponible, obtener_estadisticas
from ui.screens.upload import limpiar_sesion

def mostrar_sidebar(estado_sistema):
    """Muestra el sidebar con información del sistema"""
    with st.sidebar:
        st.markdown("### ℹ️ Información del Sistema")
        st.markdown(f"🌿 **Especies:** {estado_sistema.get('especies', 'N/A')}")
        st.markdown(f"⏱️ **Actualización:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Estado de servicios
        st.markdown("---")
        st.markdown("### 🔌 Estado de Servicios")
        
        # Estado del sistema (simplificado)
        if st.session_state.get('firestore_initialized', False):
            st.success("✅ Sistema: Completamente funcional")
    
            # Mostrar estadísticas solo si el servidor está disponible
            if servidor_disponible():
                stats = obtener_estadisticas()
                if stats:
                    st.markdown("📊 **Estadísticas del sistema:**")
                    st.write(f"• Feedback total: {stats.get('feedback_total', 0)}")
                    st.write(f"• Imágenes procesadas: {stats.get('imagenes_guardadas', 0)}")
        else:
            st.info("ℹ️ Sistema funcionando en modo básico")
    
        # Botón de reset
        st.markdown("---")
        if st.button("🔄 Nueva Consulta", use_container_width=True):
            limpiar_sesion()
            st.rerun()
        
        # Debug info
        with st.expander("🔧 Debug Info"):
            st.write(f"**Session ID:** {st.session_state.get('session_id', 'None')}")
            st.write(f"**Intento:** {st.session_state.get('intento_actual', 0)}")
            st.write(f"**Descartadas:** {len(st.session_state.get('especies_descartadas', set()))}")
            if st.session_state.get('resultado_actual'):
                st.write(f"**Especie actual:** {st.session_state.resultado_actual.get('especie_predicha')}")