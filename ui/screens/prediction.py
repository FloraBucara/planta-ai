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
        
        # Nombre de la planta - EXACTAMENTE como el título principal
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem; margin-top: 1rem;">
            <p style="
                font-size: 1.8rem; 
                color: #000000; 
                margin: 0;
                text-shadow: 
                    2px 2px 0 white,
                    -2px -2px 0 white,
                    2px -2px 0 white,
                    -2px 2px 0 white,
                    0 2px 0 white,
                    0 -2px 0 white,
                    2px 0 0 white,
                    -2px 0 0 white;
                font-weight: bold;
            ">
                <strong>🌿 {datos.get('nombre_comun', 'Nombre no disponible')}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <p style="
                font-size: 1.1rem; 
                color: #000000; 
                margin: 0;
                font-style: italic;
                text-shadow: 
                    2px 2px 0 white,
                    -2px -2px 0 white,
                    2px -2px 0 white,
                    -2px 2px 0 white,
                    0 2px 0 white,
                    0 -2px 0 white,
                    2px 0 0 white,
                    -2px 0 0 white;
                font-weight: bold;
            ">
                <strong>{datos.get('nombre_cientifico', 'N/A')}</strong>
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
        
        # Descripción - fija (no desplegable)
        if datos.get('descripcion') and info_planta.get('fuente') == 'firestore':
            st.markdown(f"""
            <div style="
                background: white; 
                padding: 20px; 
                margin: 15px 0; 
                border-radius: 10px; 
                border: 2px solid #e0e0e0;
                text-align: center;
            ">
                <h4 style="
                    color: #000000; 
                    margin-bottom: 15px;
                    text-shadow: 
                        2px 2px 0 white,
                        -2px -2px 0 white,
                        2px -2px 0 white,
                        -2px 2px 0 white,
                        0 2px 0 white,
                        0 -2px 0 white,
                        2px 0 0 white,
                        -2px 0 0 white;
                    font-weight: bold;
                ">📝 Descripción</h4>
                <p style="color: #333333; line-height: 1.5; margin: 0;">
                    {datos.get('descripcion', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # CSS FORZADO con JavaScript para expanders - TONOS VERDES
        st.markdown("""
        <style>
        /* CSS básico */
        div[data-testid="stExpander"] summary {
            background: #e8f5e8 !important;
            border: 2px solid #4CAF50 !important;
            border-radius: 10px !important;
            text-align: center !important;
            padding: 12px !important;
        }
        </style>
        
        <script>
        setTimeout(function() {
            // Buscar todos los expanders y aplicar estilos directamente
            const expanders = document.querySelectorAll('[data-testid="stExpander"]');
            expanders.forEach(function(expander) {
                const header = expander.querySelector('summary') || expander.querySelector('div:first-child');
                if (header) {
                    header.style.background = '#e8f5e8';
                    header.style.border = '2px solid #4CAF50';
                    header.style.borderRadius = '10px';
                    header.style.textAlign = 'center';
                    header.style.padding = '12px';
                }
                
                const content = expander.querySelector('div:last-child');
                if (content) {
                    content.style.background = 'white';
                    content.style.border = '1px solid #4CAF50';
                    content.style.borderTop = 'none';
                    content.style.borderRadius = '0 0 10px 10px';
                    content.style.padding = '20px';
                    content.style.textAlign = 'center';
                }
            });
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        # Cuidados - nueva sección antes de taxonomía
        if datos.get('cuidados') and info_planta.get('fuente') == 'firestore':
            with st.expander("🌱 Cuidados"):
                st.markdown(f"""
                <div style="text-align: center; background: white; padding: 10px;">
                    {datos.get('cuidados', '')}
                </div>
                """, unsafe_allow_html=True)
        
        # Información taxonómica - con estilo mejorado
        if datos.get('taxonomia') and info_planta.get('fuente') == 'firestore':
            taxonomia = datos.get('taxonomia', {})
            with st.expander("🧬 Clasificación Taxonómica"):
                st.markdown(f"""
                <div style="text-align: center; background: white; padding: 20px; border-radius: 10px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <p><strong>Reino:</strong> {taxonomia.get('reino', 'N/A')}</p>
                            <p><strong>Filo:</strong> {taxonomia.get('filo', 'N/A')}</p>
                            <p><strong>Clase:</strong> {taxonomia.get('clase', 'N/A')}</p>
                        </div>
                        <div>
                            <p><strong>Orden:</strong> {taxonomia.get('orden', 'N/A')}</p>
                            <p><strong>Familia:</strong> {taxonomia.get('familia', 'N/A')}</p>
                            <p><strong>Género:</strong> {taxonomia.get('genero', 'N/A')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Cerrar contenedor
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Botones de feedback - EXACTAMENTE como el título principal
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem; margin-top: 1rem;">
        <p style="
            font-size: 1.6rem; 
            color: #000000; 
            margin: 0;
            text-shadow: 
                2px 2px 0 white,
                -2px -2px 0 white,
                2px -2px 0 white,
                -2px 2px 0 white,
                0 2px 0 white,
                0 -2px 0 white,
                2px 0 0 white,
                -2px 0 0 white;
            font-weight: bold;
        ">
            <strong>¿Esta es tu planta?</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CSS para el botón con borde rojo
    st.markdown("""
    <style>
    div.stButton > button[kind="secondary"] {
        border: 2px solid #f44336 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Primer botón
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
                "✅ ¡Sí, es correcta!", 
                type="primary", 
                use_container_width=True,
                help="Confirmar que la identificación es correcta"
            ):
            procesar_feedback_positivo(resultado)
    
    # Segundo botón
    col1, col2, col3 = st.columns([1, 2, 1])
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