import streamlit as st
import time
from ui.components import mostrar_imagen_referencia_sin_barra
from ui.screens.upload import buscar_info_planta_firestore, limpiar_sesion
from utils.api_client import enviar_feedback
from utils.session_manager import session_manager
from ui.loading_buttons import boton_seleccion_planta
from ui.expand_buttons import boton_expandible_toggle

def pantalla_top_especies():
    """Pantalla de selección manual de las top 5 especies - VERSIÓN EXPANDIBLE"""
    st.markdown("### 🤔 ¿Tal vez sea una de estas?")
    st.info("Selecciona la especie correcta de las siguientes opciones:")
    
    # Obtener top 5 especies
    with st.spinner("🔍 Buscando especies similares..."):
        especies_excluir = list(st.session_state.especies_descartadas)
        top_especies = session_manager.predictor.obtener_top_especies(
            st.session_state.imagen_actual,
            cantidad=5,
            especies_excluir=especies_excluir
        )
    
    if not top_especies:
        st.error("❌ Error obteniendo especies similares")
        return
    
    # Mostrar imagen original
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.imagen_actual, caption="Tu planta", use_container_width=True)
    
    st.markdown("---")
    
    # Mostrar las 5 especies con información expandible
    for i, especie_data in enumerate(top_especies):
        mostrar_especie_opcion(i, especie_data)
    
    # Opción "No es ninguna de estas"
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("❌ No es ninguna de estas", type="secondary", use_container_width=True):
            # Establecer mensaje para mostrar en inicio
            st.session_state.mensaje_inicio = "no_identificada"
            
            # Limpiar y volver al inicio
            limpiar_sesion()
            st.rerun()
            
def mostrar_especie_opcion(i, especie_data):
    """Muestra una opción de especie con información expandible"""
    # Buscar información de la especie
    info_planta = buscar_info_planta_firestore(especie_data["especie"])
    datos = info_planta.get('datos', {})
    
    # Container para cada especie
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 3])
        
        with col1:
            # Número de opción
            st.markdown(f"### {i+1}")
        
        with col2:
            # Imagen de referencia
            mostrar_imagen_referencia_sin_barra(especie_data["especie"])
        
        with col3:
            # Información básica
            st.markdown(f"**{datos.get('nombre_comun', 'Nombre no disponible')}**")
            st.markdown(f"*{especie_data['especie']}*")
            
            # Barra de confianza
            porcentaje = int(especie_data["confianza"] * 100)
            st.markdown(f"""
            <div class="confidence-bar" style="height: 10px; background: #e9ecef; border-radius: 5px; margin: 0.5rem 0; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: {porcentaje}%; transition: width 0.3s ease;"></div>
            </div>
            <p style="text-align: center; font-size: 0.9em; margin: 0;">
                Confianza: {porcentaje}%
            </p>
            """, unsafe_allow_html=True)
            
            # Botón expandir/contraer información
            expand_key = f"expand_{i}"
            expandido = st.session_state.get(expand_key, False)

            if boton_expandible_toggle(
                texto_expandir="Ver información completa",
                texto_contraer="Ocultar información", 
                key=f"toggle_{i}",
                expandido=expandido
            ):
                st.session_state[expand_key] = not expandido
                st.rerun()
            
            # Mostrar información expandida si está activada
            if st.session_state.get(expand_key, False):
                mostrar_info_expandida(i, especie_data, datos, info_planta)
    
    # Separador entre especies
    st.markdown("---")

def mostrar_info_expandida(i, especie_data, datos, info_planta):
    """Muestra la información expandida de una especie"""
    st.markdown("---")
    
    # Información detallada
    if info_planta.get('fuente') == 'firestore':
        st.markdown("*✅ Información verificada de la base de datos*")
    else:
        st.info("ℹ️ Información básica disponible")
    
    # Descripción
    if datos.get('descripcion'):
        st.markdown("**📝 Descripción:**")
        st.write(datos['descripcion'])
    
    # Taxonomía
    if datos.get('taxonomia') and info_planta.get('fuente') == 'firestore':
        taxonomia = datos['taxonomia']
        if taxonomia:
            st.markdown("**🧬 Clasificación Taxonómica:**")
            col_tax1, col_tax2 = st.columns(2)
            
            with col_tax1:
                st.write(f"• **Reino:** {taxonomia.get('reino', 'N/A')}")
                st.write(f"• **Filo:** {taxonomia.get('filo', 'N/A')}")
                st.write(f"• **Clase:** {taxonomia.get('clase', 'N/A')}")
            
            with col_tax2:
                st.write(f"• **Orden:** {taxonomia.get('orden', 'N/A')}")
                st.write(f"• **Familia:** {taxonomia.get('familia', 'N/A')}")
                st.write(f"• **Género:** {taxonomia.get('genero', 'N/A')}")
    
    # Información adicional                   
    if datos.get('fuente'):
        st.markdown(f"**📚 Fuente:** {datos['fuente']}")
    
    st.markdown("---")
    
    # BOTÓN "ES ESTA" AL FINAL DE LA INFORMACIÓN EXPANDIDA
    if boton_seleccion_planta(f"select_final_{i}", datos.get('nombre_comun', 'esta planta')):
        procesar_seleccion_especie(especie_data, datos)

def procesar_seleccion_especie(especie_data, datos):
    """Procesa la selección de una especie por el usuario"""
    with st.spinner("💾 Guardando tu selección..."):
        # Enviar feedback de corrección
        respuesta = enviar_feedback(
            imagen_pil=st.session_state.imagen_actual,
            session_id=st.session_state.session_id,
            especie_predicha=st.session_state.resultado_actual["especie_predicha"],
            confianza=st.session_state.resultado_actual["confianza"],
            feedback_tipo="corregido",
            especie_correcta=especie_data["especie"]
        )

        if respuesta.get("success"):
            st.success(f"🎉 ¡Gracias! Has identificado tu planta como **{datos.get('nombre_comun', especie_data['especie'])}**")
            st.success("✅ Imagen guardada para mejorar el modelo")
    
            # Mostrar progreso
            if respuesta.get("progreso"):
                st.info(f"📊 Progreso para reentrenamiento: {respuesta['progreso']}%")
    
            if respuesta.get("necesita_reentrenamiento"):
                st.warning("🚀 ¡Suficientes imágenes para reentrenamiento!")
        else:
            st.warning(f"⚠️ {respuesta.get('mensaje', 'Error guardando feedback')}")

        st.balloons()
        time.sleep(2)

        # Limpiar estados de botones y volver al inicio
        for j in range(5):
            for state_key in [f'expand_{j}', f'boton_presionado_{j}']:
                if state_key in st.session_state:
                    del st.session_state[state_key]
        
        limpiar_sesion()
        st.rerun()