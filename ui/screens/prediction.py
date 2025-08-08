import streamlit as st
import time
from datetime import datetime
from ui.components import mostrar_info_planta_completa
from utils.api_client import enviar_feedback, servidor_disponible, obtener_estadisticas
from ui.screens.upload import limpiar_sesion

def pantalla_prediccion_feedback():
    """Pantalla de predicción con botones de feedback"""
    resultado = st.session_state.resultado_actual
    
    # Mostrar imagen del usuario
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.imagen_actual, caption="Tu planta", use_container_width=True)
    
    # Card de predicción
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Mostrar información de la planta
    info_planta = resultado.get("info_planta", {})
    mostrar_info_planta_completa(info_planta)
    
    # Barra de confianza
    confianza = resultado["confianza"]
    porcentaje = int(confianza * 100)
    
    st.markdown(f"""
    <div class="confidence-bar">
        <div class="confidence-fill" style="width: {porcentaje}%;"></div>
    </div>
    <p style="text-align: center; margin: 0.5rem 0; font-weight: bold;">
        Confianza de la predicción: {porcentaje}%
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Botones de feedback
    st.markdown("---")
    st.markdown("### ¿Es correcta esta identificación?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ ¡Sí, es correcta!", type="primary", use_container_width=True):
            with st.spinner("💾 Guardando tu confirmación..."):
                # Enviar feedback positivo
                respuesta = enviar_feedback(
                    imagen_pil=st.session_state.imagen_actual,
                    session_id=st.session_state.session_id,
                    especie_predicha=resultado["especie_predicha"],
                    confianza=resultado["confianza"],
                    feedback_tipo="correcto",
                    especie_correcta=resultado["especie_predicha"]  # Misma especie
                )
            
                if respuesta.get("success"):
                    st.success("🎉 ¡Gracias por confirmar!")
                    st.success("✅ Imagen guardada para mejorar el modelo")
                
                    # Mostrar progreso de reentrenamiento
                    if respuesta.get("progreso"):
                        st.info(f"📊 Progreso para reentrenamiento: {respuesta['progreso']}%")
                    
                    if respuesta.get("necesita_reentrenamiento"):
                        st.warning("🚀 ¡Suficientes imágenes para reentrenamiento!")
                else:
                    st.warning(f"⚠️ {respuesta.get('mensaje', 'Error guardando feedback')}")
            
                st.balloons()
                time.sleep(2)
            
                # Limpiar y volver al inicio
                limpiar_sesion()
                st.rerun()
    
    with col2:
        if st.button("❌ No, es incorrecta", type="secondary", use_container_width=True):
            # Procesar feedback negativo
            especie_rechazada = resultado["especie_predicha"]
            st.session_state.especies_descartadas.add(especie_rechazada)
            st.session_state.intento_actual += 1
            
            # Mostrar directamente las top 5 especies
            st.session_state.mostrar_top_especies = True
            st.rerun()