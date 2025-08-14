import streamlit as st
from pathlib import Path
import base64
from utils.api_client import SERVER_URL

def pantalla_splash():
    """Pantalla de bienvenida y autorización del servidor"""
    
    # Logo centrado
    logo_path = Path("assets/logo.png")
    
    if logo_path.exists():
        # Mostrar logo grande en splash
        with open(logo_path, "rb") as file:
            logo_base64 = base64.b64encode(file.read()).decode()
        
        html_logo = f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: 2rem 0;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 450px; height: auto;" />
        </div>
        """
        st.markdown(html_logo, unsafe_allow_html=True)
    else:
        # Fallback: Título grande
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="
                background: linear-gradient(90deg, #2E8B57, #98FB98);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 3rem;
                font-weight: bold;
                margin: 0;
            ">🌱 BucaraFlora</h1>
            <h2 style="color: #2E8B57; margin-top: 1rem;">Identificador de Plantas con IA</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Texto explicativo del proyecto - CON FONDO CONSISTENTE
    st.markdown("""
    <div class="splash-card" style="
        text-align: center; 
        max-width: 600px; 
        margin: 0 auto 2rem auto; 
        background: rgba(248, 249, 250, 0.95);
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #2E8B57;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h3 style="color: #2E8B57; margin-bottom: 1rem;">
            📚 Proyecto de Grado
        </h3>
        <p style="
            font-size: 1.1rem; 
            color: #333; 
            line-height: 1.6;
            margin-bottom: 1.5rem;
            text-shadow: 
                1px 1px 2px white,
                -1px -1px 2px white,
                1px -1px 2px white,
                -1px 1px 2px white;
        ">
            <strong>BucaraFlora</strong> es un sistema de identificación de plantas colombianas 
            desarrollado con Inteligencia Artificial como proyecto de grado universitario.
        </p>
        <p style="
            font-size: 1rem; 
            color: #666; 
            line-height: 1.5;
            margin-bottom: 1.5rem;
            text-shadow: 
                0.5px 0.5px 1px white,
                -0.5px -0.5px 1px white,
                0.5px -0.5px 1px white,
                -0.5px 0.5px 1px white;
        ">
            Este sistema puede identificar <strong>335 especies</strong> de plantas nativas y 
            ornamentales de Colombia utilizando técnicas avanzadas de Machine Learning 
            y procesamiento de imágenes.
        </p>
        <div style="
            background: rgba(255, 243, 205, 0.95);
            padding: 1rem;
            border-radius: 8px;
            border-left: 3px solid #ffc107;
            margin-bottom: 1rem;
            backdrop-filter: blur(5px);
        ">
            <p style="
                font-size: 0.95rem; 
                color: #856404; 
                margin: 0;
                font-weight: bold;
                text-shadow: 
                    0.5px 0.5px 1px rgba(255,255,255,0.8),
                    -0.5px -0.5px 1px rgba(255,255,255,0.8);
            ">
                ⚠️ <strong>Autorización Requerida</strong><br>
                Para utilizar el sistema, primero debes autorizar el acceso al servidor 
                de procesamiento de imágenes.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Información técnica opcional
    with st.expander("🔧 Información Técnica del Proyecto"):
        st.markdown("""
        **Tecnologías utilizadas:**
        - 🤖 **Modelo:** MobileNetV2 con Transfer Learning
        - ⚡ **Runtime:** ONNX Runtime para máximo rendimiento  
        - 🐍 **Backend:** Python con FastAPI
        - 🎨 **Frontend:** Streamlit
        - 🗄️ **Base de datos:** Firebase Firestore
        - 🌐 **Deployment:** Streamlit Cloud + ngrok
        
        **Métricas del modelo:**
        - 📊 **Accuracy:** ~63% en 335 especies
        - ⚡ **Velocidad:** ~20-50ms por predicción
        - 📱 **Compatibilidad:** Python 3.13, multiplataforma
        """)
    
    # Botón de autorización centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Verificar si hay URL del servidor
        if SERVER_URL:
            # Mostrar información del servidor configurado
            st.markdown(f"""
            <div style="
                background: rgba(232, 245, 233, 0.95);
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #28a745;
                margin: 1rem 0;
                backdrop-filter: blur(5px);
            ">
                <h4 style="color: #155724; margin-bottom: 1rem;">
                    🌐 Servidor Configurado
                </h4>
                <p style="
                    color: #333;
                    margin-bottom: 0.5rem;
                    font-family: monospace;
                    background: rgba(255,255,255,0.8);
                    padding: 0.5rem;
                    border-radius: 5px;
                ">
                    <strong>URL:</strong> {SERVER_URL}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            server_status = verificar_estado_servidor()
            
            if server_status == "conectado":
                # Servidor ya autorizado y funcionando
                st.success("✅ Servidor autorizado y funcionando correctamente")
                
                if st.button(
                    "🚀 Continuar al Sistema",
                    type="primary",
                    use_container_width=True,
                    key="btn_continue"
                ):
                    st.session_state.splash_completado = True
                    st.rerun()
            else:
                # Servidor configurado pero necesita autorización
                st.warning("⚠️ Servidor configurado - Requiere autorización")
                
                if st.button(
                    "🔐 Autorizar Servidor",
                    type="primary", 
                    use_container_width=True,
                    key="btn_authorize"
                ):
                    # Abrir en nueva pestaña
                    st.markdown(f"""
                    <script>
                        window.open('{SERVER_URL}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar instrucciones
                    st.info("""
                    📋 **Instrucciones:**
                    1. Se abrió una nueva pestaña con el servidor
                    2. Autoriza el acceso cuando te lo solicite ngrok
                    3. Regresa a esta pestaña y presiona el botón de abajo
                    """)
                    
                    # Botón para continuar después de autorizar
                    if st.button("✅ Ya autoricé - Continuar", key="btn_continue_after"):
                        st.session_state.splash_completado = True
                        st.rerun()
        else:
            # NO hay URL configurada
            st.error("❌ Servidor no configurado")
            
            st.markdown("""
            <div style="
                background: rgba(248, 215, 218, 0.95);
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #dc3545;
                margin: 1rem 0;
                backdrop-filter: blur(5px);
            ">
                <h4 style="color: #721c24; margin-bottom: 1rem;">
                    🔧 Configuración Requerida
                </h4>
                <p style="color: #721c24; margin-bottom: 1rem;">
                    El servidor no está configurado en <code>api_client.py</code>
                </p>
                <p style="
                    color: #333;
                    font-size: 0.9rem;
                    background: rgba(255,255,255,0.8);
                    padding: 1rem;
                    border-radius: 5px;
                    font-family: monospace;
                    margin: 0;
                ">
                    <strong>Para desarrolladores:</strong><br>
                    Actualiza la variable SERVER_URL en utils/api_client.py:<br><br>
                    SERVER_URL = "https://tu-ngrok-url.ngrok-free.app"
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón para continuar sin servidor (modo demo)
            if st.button(
                "🔄 Continuar en Modo Demo",
                type="secondary",
                use_container_width=True,
                key="btn_demo"
            ):
                st.session_state.splash_completado = True
                st.rerun()
            
            # Información sobre el modo demo
            st.markdown("""
            <div style="
                background: rgba(255, 248, 225, 0.95);
                padding: 1rem;
                border-radius: 8px;
                border-left: 3px solid #ff9800;
                margin-top: 1rem;
                backdrop-filter: blur(5px);
            ">
                <p style="
                    color: #ef6c00;
                    font-size: 0.9rem;
                    margin: 0;
                    text-shadow: 0.5px 0.5px 1px rgba(255,255,255,0.8);
                ">
                    📝 <strong>Modo Demo:</strong> Podrás usar el identificador de plantas, 
                    pero las funciones de servidor estarán deshabilitadas.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer con información adicional - CON FONDO CONSISTENTE
    st.markdown("""
    <div style="
        text-align: center; 
        margin-top: 3rem; 
        padding: 2rem;
        border-top: 1px solid rgba(238, 238, 238, 0.8);
        color: #666;
        font-size: 0.9rem;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        backdrop-filter: blur(5px);
        text-shadow: 
            0.5px 0.5px 1px white,
            -0.5px -0.5px 1px white;
    ">
        <p>🎓 Desarrollado como proyecto de grado universitario</p>
        <p>🌱 Contribuyendo a la conservación de la biodiversidad colombiana</p>
    </div>
    """, unsafe_allow_html=True)

def verificar_estado_servidor():
    """Verifica si el servidor está disponible y autorizado"""
    try:
        from utils.api_client import servidor_disponible
        if servidor_disponible():
            return "conectado"
        else:
            return "desconectado"
    except:
        return "error"