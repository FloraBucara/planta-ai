import streamlit as st

def pantalla_error_sistema():
    """Pantalla cuando el sistema no está disponible"""
    st.markdown('<div class="error-message">', unsafe_allow_html=True)
    st.markdown("### ❌ Sistema No Disponible")
    st.markdown("El modelo de identificación no está cargado o entrenado.")
    st.markdown("**Posibles soluciones:**")
    st.markdown("- Entrenar el modelo inicial: `python model/train_model.py`")
    st.markdown("- Verificar que existe el archivo del modelo")
    st.markdown("- Contactar al administrador del sistema")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Verificar sistema nuevamente"):
        st.rerun()