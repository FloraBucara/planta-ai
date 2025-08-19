import streamlit as st
import time
from datetime import datetime
from utils.api_client import enviar_feedback, servidor_disponible, obtener_estadisticas, SERVER_URL
from ui.screens.upload import limpiar_sesion
from urllib.parse import quote

def pantalla_prediccion_feedback():
    """Pantalla de predicción con diseño tipo card moderno"""
    resultado = st.session_state.resultado_actual
    info_planta = resultado.get("info_planta", {})
    datos = info_planta.get('datos', {})
    
    # Crear un contenedor tipo card
    with st.container():
        # Card con bordes redondeados
        st.markdown("""
        <div style="
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border: 1px solid #e0e0e0;
        ">
        """, unsafe_allow_html=True)
        
        # PARTE SUPERIOR: Imagen de referencia del servidor
        nombre_cientifico = resultado.get("especie_predicha", '')
        
        if nombre_cientifico and SERVER_URL:
            # Convertir nombre a formato de carpeta
            nombre_carpeta = nombre_cientifico.replace(' ', '_')
            especie_encoded = quote(nombre_carpeta)
            imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
            
            try:
                st.image(
                    imagen_url,
                    use_container_width=True,
                    caption=f"🌿 {datos.get('nombre_comun', nombre_cientifico)}"
                )
            except Exception as e:
                # Si falla, usar imagen del usuario como fallback
                print(f"⚠️ Error cargando imagen del servidor: {e}")
                st.image(
                    st.session_state.imagen_actual,
                    use_container_width=True,
                    caption=f"🌿 {datos.get('nombre_comun', nombre_cientifico)}"
                )
        else:
            # Fallback si no hay servidor configurado
            st.image(
                st.session_state.imagen_actual,
                use_container_width=True,
                caption=f"🌿 {datos.get('nombre_comun', nombre_cientifico)}"
            )
        
        # Mostrar imagen del usuario justo debajo de la imagen de referencia
        with st.expander("Ver tu foto original"):
            st.image(st.session_state.imagen_actual, caption="Foto que subiste", use_container_width=True)
        
        # Nombre de la planta - simplificado para móviles
        st.markdown(f"### 🌿 {datos.get('nombre_comun', 'Nombre no disponible')}")
        st.markdown(f"*{datos.get('nombre_cientifico', 'N/A')}*")
        
        # Indicador de confianza - simplificado para móviles
        confianza = resultado["confianza"]
        porcentaje = int(confianza * 100)
        
        if porcentaje > 70:
            st.success(f"🎯 Confianza: {porcentaje}%")
        elif porcentaje > 40:
            st.warning(f"⚠️ Confianza: {porcentaje}%")
        else:
            st.error(f"❌ Confianza: {porcentaje}%")
        
        # Descripción - simplificada para móviles
        if datos.get('descripcion') and info_planta.get('fuente') == 'firestore':
            with st.expander("📝 Descripción"):
                st.write(datos.get('descripcion', ''))
        
        # Información taxonómica - simplificada para móviles
        if datos.get('taxonomia') and info_planta.get('fuente') == 'firestore':
            taxonomia = datos.get('taxonomia', {})
            with st.expander("🧬 Clasificación Taxonómica"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Reino:** {taxonomia.get('reino', 'N/A')}")
                    st.write(f"**Filo:** {taxonomia.get('filo', 'N/A')}")
                    st.write(f"**Clase:** {taxonomia.get('clase', 'N/A')}")
                with col2:
                    st.write(f"**Orden:** {taxonomia.get('orden', 'N/A')}")
                    st.write(f"**Familia:** {taxonomia.get('familia', 'N/A')}")
                    st.write(f"**Género:** {taxonomia.get('genero', 'N/A')}")
        
        # Cerrar contenedor
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Botones de feedback - simplificados
    st.markdown("### ¿Esta es tu planta?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
                "✅ ¡Sí, es correcta!", 
                type="primary", 
                use_container_width=True,
                help="Confirmar que la identificación es correcta"
            ):
                procesar_feedback_positivo(resultado)
        
        with col2:
            if st.button(
                "❌ No, es incorrecta", 
                type="secondary", 
                use_container_width=True,
                help="Ver otras opciones posibles"
            ):
                procesar_feedback_negativo(resultado)

def procesar_feedback_positivo(resultado):
    """Procesa el feedback positivo del usuario"""
    with st.spinner("💾 Guardando tu confirmación..."):
        respuesta = enviar_feedback(
            imagen_pil=st.session_state.imagen_actual,
            session_id=st.session_state.session_id,
            especie_predicha=resultado["especie_predicha"],
            confianza=resultado["confianza"],
            feedback_tipo="correcto",
            especie_correcta=resultado["especie_predicha"]
        )
    
        if respuesta.get("success"):
            st.success("🎉 ¡Gracias por confirmar!")
            st.success("✅ Imagen guardada para mejorar el modelo")
        
            if respuesta.get("progreso"):
                st.info(f"📊 Progreso para reentrenamiento: {respuesta['progreso']}%")
            
            if respuesta.get("necesita_reentrenamiento"):
                st.warning("🚀 ¡Suficientes imágenes para reentrenamiento!")
        else:
            st.warning(f"⚠️ {respuesta.get('mensaje', 'Error guardando feedback')}")
    
        st.balloons()
        time.sleep(2)
        limpiar_sesion()
        st.rerun()

def procesar_feedback_negativo(resultado):
    """Procesa el feedback negativo del usuario"""
    especie_rechazada = resultado["especie_predicha"]
    st.session_state.especies_descartadas.add(especie_rechazada)
    st.session_state.intento_actual += 1
    st.session_state.mostrar_top_especies = True
    st.rerun()