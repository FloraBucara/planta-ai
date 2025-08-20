import streamlit as st
import time
from ui.components import mostrar_imagen_referencia_sin_barra
from ui.screens.upload import buscar_info_planta_firestore, limpiar_sesion
from utils.api_client import enviar_feedback
from utils.session_manager import session_manager

def pantalla_top_especies():
    """Pantalla de selección manual de las top 5 especies - VERSIÓN EXPANDIBLE"""
    # Marcar pantalla actual
    st.session_state.current_screen = 'selection'
    
    # Crear un contenedor tipo card con fondo blanco
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
            padding: 20px;
        ">
        """, unsafe_allow_html=True)
        
        # Título principal con estilo igual a prediction.py
        st.markdown("""
        <div style="text-align: center; margin-bottom: 0.5rem; margin-top: 1rem;">
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
                <strong>🤔 ¿Tal vez sea una de estas?</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Subtítulo con estilo
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <p style="
                font-size: 1.1rem; 
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
                Selecciona la especie correcta de las siguientes opciones:
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
        st.image(st.session_state.imagen_actual, caption="Tu planta")
    
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
    
    # Cerrar contenedor principal
    st.markdown("</div>", unsafe_allow_html=True)
            
def mostrar_especie_opcion(i, especie_data):
    """Muestra una opción de especie con información expandible"""
    # Buscar información de la especie
    info_planta = buscar_info_planta_firestore(especie_data["especie"])
    datos = info_planta.get('datos', {})
    
    # Container para cada especie
    with st.container():
        # Primera fila: Número y nombre común
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Número de opción
            st.markdown(f"### {i+1}")
        
        with col2:
            # Nombre común con estilo de fuente
            st.markdown(f"""
            <p style="
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
                font-size: 1.2rem;
                margin-top: 0.5rem;
            ">
                <strong>{datos.get('nombre_comun', 'Nombre no disponible')}</strong>
            </p>
            """, unsafe_allow_html=True)
        
        # Segunda fila: Imagen, nombre científico y confianza
        col1, col2, col3 = st.columns([1, 2, 3])
        
        with col1:
            # Espacio vacío para alineación
            st.write("")
        
        with col2:
            # Imagen de referencia
            mostrar_imagen_referencia_sin_barra(especie_data["especie"])
        
        with col3:
            # Nombre científico con estilo de fuente
            st.markdown(f"""
            <p style="
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
                font-style: italic;
            ">
                <strong>{especie_data['especie']}</strong>
            </p>
            """, unsafe_allow_html=True)
            
            # Círculo de confianza como en prediction.py
            porcentaje = int(especie_data["confianza"] * 100)
            color = "#4caf50" if porcentaje > 70 else "#ff9800" if porcentaje > 40 else "#f44336"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; margin: 1rem 0;">
                <div style="position: relative; width: 80px; height: 80px;">
                    <svg width="80" height="80" style="transform: rotate(-90deg);">
                        <circle cx="40" cy="40" r="30" 
                                stroke="#e0e0e0" 
                                stroke-width="6" 
                                fill="none"/>
                        <circle cx="40" cy="40" r="30" 
                                stroke="{color}" 
                                stroke-width="6" 
                                fill="none"
                                stroke-dasharray="{porcentaje * 1.88} 188"
                                stroke-linecap="round"/>
                    </svg>
                    <div style="
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        text-align: center;
                    ">
                        <div style="font-size: 1rem; font-weight: bold; color: {color};">
                            {porcentaje}%
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Texto de confianza con estilo de fuente
            st.markdown(f"""
            <p style="
                text-align: center;
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
                font-size: 0.9rem;
            ">
                <strong>Confianza</strong>
            </p>
            """, unsafe_allow_html=True)
            
            # Información expandible usando expander
            with st.expander("📋 Ver información completa"):
                mostrar_info_expandida(i, especie_data, datos, info_planta)

def mostrar_info_expandida(i, especie_data, datos, info_planta):
    """Muestra la información expandida de una especie"""
    
    # Información detallada
    if info_planta.get('fuente') == 'firestore':
        st.markdown("*✅ Información verificada de la base de datos*")
    else:
        st.info("ℹ️ Información básica disponible")
    
    # Descripción - fija (no desplegable) con borde verde
    if datos.get('descripcion'):
        st.markdown(f"""
        <div style="
            background: white; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 10px; 
            border: 2px solid #4CAF50;
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
    
    # Cuidados - sección desplegable
    if datos.get('cuidados') and info_planta.get('fuente') == 'firestore':
        with st.expander("🌱 Cuidados"):
            st.markdown(f"""
            <div style="text-align: center; background: white; padding: 20px; border-radius: 10px; border: 2px solid #4CAF50;">
                {datos.get('cuidados', '')}
            </div>
            """, unsafe_allow_html=True)
    
    # Taxonomía - sección desplegable con borde verde
    if datos.get('taxonomia') and info_planta.get('fuente') == 'firestore':
        taxonomia = datos['taxonomia']
        if taxonomia:
            with st.expander("🧬 Clasificación Taxonómica"):
                st.markdown(f"""
                <div style="text-align: center; background: white; padding: 20px; border-radius: 10px; border: 2px solid #4CAF50;">
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
    
    # Información adicional                   
    if datos.get('fuente'):
        st.markdown(f"""
        <p style="
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
            <strong>Fuente: {datos['fuente']}</strong>
        </p>
        """, unsafe_allow_html=True)
    
    # BOTÓN "ES ESTA" AL FINAL DE LA INFORMACIÓN EXPANDIDA
    if st.button(
        "✅ ¡Es esta planta!",
        key=f"select_final_{i}",
        type="primary",
        use_container_width=True
    ):
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