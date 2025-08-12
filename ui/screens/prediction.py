import streamlit as st
import time
from datetime import datetime
from utils.api_client import enviar_feedback, servidor_disponible, obtener_estadisticas, SERVER_URL
from ui.screens.upload import limpiar_sesion
from ui.styles import crear_boton_personalizado
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
        
        # PARTE INFERIOR: Información
        st.markdown("""
        <div style="
            background: white;
            padding: 2rem;
            margin-top: -4px;
        ">
        """, unsafe_allow_html=True)
        
        # Nombre de la planta (centrado)
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #2e7d32; margin: 0;">
                🌿 {datos.get('nombre_comun', 'Nombre no disponible')}
            </h2>
            <p style="color: #666; font-style: italic; font-size: 1.1rem; margin: 0.5rem 0;">
                {datos.get('nombre_cientifico', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Indicador de confianza circular (centrado)
        confianza = resultado["confianza"]
        porcentaje = int(confianza * 100)
        color = "#4caf50" if porcentaje > 70 else "#ff9800" if porcentaje > 40 else "#f44336"
        
        # Usar HTML para crear el círculo
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: 2rem 0;">
            <div style="position: relative; width: 100px; height: 100px;">
                <svg width="100" height="100" style="transform: rotate(-90deg);">
                    <circle cx="50" cy="50" r="40" 
                            stroke="#e0e0e0" 
                            stroke-width="8" 
                            fill="none"/>
                    <circle cx="50" cy="50" r="40" 
                            stroke="{color}" 
                            stroke-width="8" 
                            fill="none"
                            stroke-dasharray="{porcentaje * 2.51} 251"
                            stroke-linecap="round"/>
                </svg>
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                ">
                    <div style="font-size: 1.5rem; font-weight: bold; color: {color};">
                        {porcentaje}%
                    </div>
                    <div style="font-size: 0.8rem; color: #666;">
                        Confianza
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Descripción
        if datos.get('descripcion') and info_planta.get('fuente') == 'firestore':
            st.markdown("---")
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            ">
                <h4 style="color: #2e7d32;">📝 Descripción</h4>
                <p style="color: #424242; line-height: 1.6;">
                    {datos.get('descripcion', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Información taxonómica
        if datos.get('taxonomia') and info_planta.get('fuente') == 'firestore':
            taxonomia = datos.get('taxonomia', {})
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            ">
                <h4 style="color: #2e7d32;">🧬 Clasificación Taxonómica</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <div><strong>Reino:</strong> {taxonomia.get('reino', 'N/A')}</div>
                    <div><strong>Orden:</strong> {taxonomia.get('orden', 'N/A')}</div>
                    <div><strong>Filo:</strong> {taxonomia.get('filo', 'N/A')}</div>
                    <div><strong>Familia:</strong> {taxonomia.get('familia', 'N/A')}</div>
                    <div><strong>Clase:</strong> {taxonomia.get('clase', 'N/A')}</div>
                    <div><strong>Género:</strong> {taxonomia.get('genero', 'N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Cerrar divs
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # BOTONES DE FEEDBACK - CON NUEVOS ESTILOS PERSONALIZADOS
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>¿Esta es tu planta?</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BOTÓN CONFIRMAR - VERDE DEGRADADO
        if crear_boton_personalizado(
            "✅ ¡Sí, es correcta!",
            "btn-base btn-confirm",
            "btn_correct_prediction"
        ):
            procesar_feedback_positivo(resultado)
    
    with col2:
        # BOTÓN INCORRECTO - ROJO DEGRADADO NOTORIO
        if crear_boton_personalizado(
            "❌ No, es incorrecta",
            "btn-base btn-incorrect",
            "btn_incorrect_prediction"
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