import streamlit as st
from pathlib import Path

def mostrar_header_estatico():
    """Muestra el header fijo en la parte superior sin hacer scroll"""
    # Intentar cargar logo local
    logo_path = Path("assets/logo.png")
    
    if logo_path.exists():
        # Header con logo
        st.markdown(f"""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(46, 125, 50, 0.2);
            padding: 1rem 0;
            text-align: center;
        ">
            <img src="data:image/png;base64,{get_base64_logo()}" 
                 style="max-height: 60px; max-width: 300px;" 
                 alt="BucaraFlora Logo">
            <p style="
                margin: 0.5rem 0 0 0;
                color: #2e7d32;
                font-weight: 500;
                font-size: 1rem;
            ">
                Sube una foto de tu planta y descubre qué especie es
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Header con texto solamente
        st.markdown("""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(46, 125, 50, 0.2);
            padding: 1rem 0;
            text-align: center;
        ">
            <h1 style="
                margin: 0;
                color: #2e7d32;
                font-size: 2rem;
                font-weight: bold;
                background: linear-gradient(90deg, #2E8B57, #98FB98);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">
                🌱 BucaraFlora - Identificador de Plantas IA
            </h1>
            <p style="
                margin: 0.5rem 0 0 0;
                color: #2e7d32;
                font-weight: 500;
                font-size: 1rem;
            ">
                Sube una foto de tu planta y descubre qué especie es
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Estado del sistema (posición fija)
    estado_html = ""
    if st.session_state.get('firestore_initialized'):
        estado_html = """
        <div style="
            position: fixed;
            top: 120px;
            right: 20px;
            z-index: 1001;
            background: rgba(212, 237, 218, 0.95);
            color: #155724;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            border: 1px solid #c3e6cb;
            font-size: 0.9rem;
            font-weight: 500;
        ">
            ✅ Sistema conectado y listo
        </div>
        """
    else:
        estado_html = """
        <div style="
            position: fixed;
            top: 120px;
            right: 20px;
            z-index: 1001;
            background: rgba(255, 243, 205, 0.95);
            color: #856404;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            border: 1px solid #ffeaa7;
            font-size: 0.9rem;
            font-weight: 500;
        ">
            ⚠️ Funciones limitadas
        </div>
        """
    
    st.markdown(estado_html, unsafe_allow_html=True)

def get_base64_logo():
    """Convierte el logo a base64"""
    try:
        import base64
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except:
        pass
    return ""

def mostrar_header():
    """Función original mantenida para compatibilidad"""
    # En pantallas que no sean home, usar header normal
    if not st.session_state.get('en_pantalla_home', False):
        mostrar_header_original()
    else:
        mostrar_header_estatico()

def mostrar_header_original():
    """Header original para otras pantallas"""
    logo_path = Path("assets/logo.png")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown('<h1 class="main-header">🌱 BucaraFlora - Identificador de Plantas IA</h1>', unsafe_allow_html=True)
    
    st.markdown("**Sube una foto de tu planta y descubre qué especie es**", unsafe_allow_html=True)
    
    if st.session_state.get('firestore_initialized'):
        st.success("✅ Sistema conectado y listo")
    else:
        st.warning("⚠️ Algunas funciones pueden estar limitadas")

# Resto de funciones originales se mantienen igual...
def mostrar_info_planta_completa(info_planta):
    """Muestra la información completa de la planta de forma visualmente atractiva"""
    datos = info_planta.get('datos', {})
    fuente = info_planta.get('fuente', 'desconocido')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🌿 {datos.get('nombre_comun', 'Nombre no disponible')}")
        st.markdown(f"**Nombre científico:** *{datos.get('nombre_cientifico', 'N/A')}*")
        
        descripcion = datos.get('descripcion', '')
        if descripcion and fuente == 'firestore':
            st.markdown("#### 📝 Descripción")
            st.markdown(f'<div class="info-card">{descripcion}</div>', unsafe_allow_html=True)
                    
        if datos.get('fuente'):
            st.markdown(f"**📚 Fuente:** {datos.get('fuente')}")
    
    with col2:
        mostrar_imagen_referencia(datos.get('nombre_cientifico', ''))

    if datos.get('taxonomia') and fuente == 'firestore':
        with st.expander("🧬 Ver Clasificación Taxonómica"):
            taxonomia = datos.get('taxonomia', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Clasificación Superior:**")
                st.write(f"• **Reino:** {taxonomia.get('reino', 'N/A')}")
                st.write(f"• **Filo:** {taxonomia.get('filo', 'N/A')}")
                st.write(f"• **Clase:** {taxonomia.get('clase', 'N/A')}")
            
            with col2:
                st.markdown("**Clasificación Inferior:**")
                st.write(f"• **Orden:** {taxonomia.get('orden', 'N/A')}")
                st.write(f"• **Familia:** {taxonomia.get('familia', 'N/A')}")
                st.write(f"• **Género:** {taxonomia.get('genero', 'N/A')}")
                st.write(f"• **Especie:** {taxonomia.get('especie', 'N/A')}")

def mostrar_imagen_referencia(nombre_cientifico):
    """Muestra la primera imagen disponible de la especie desde el servidor"""
    try:
        from utils.api_client import SERVER_URL
        from urllib.parse import quote
        
        if not SERVER_URL:
            return
        
        nombre_carpeta = nombre_cientifico.replace(' ', '_')
        especie_encoded = quote(nombre_carpeta)
        imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
        
        try:
            st.image(
                imagen_url,
                caption="Imagen de referencia",
                use_container_width=True
            )
        except Exception as e:
            pass
            
    except Exception as e:
        pass

def mostrar_imagen_referencia_sin_barra(nombre_cientifico):
    """Muestra imagen de referencia SIN la barra superior molesta"""
    try:
        from utils.api_client import SERVER_URL
        from urllib.parse import quote
        
        if not SERVER_URL:
            return
        
        nombre_carpeta = nombre_cientifico.replace(' ', '_')
        especie_encoded = quote(nombre_carpeta)
        imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
        
        try:
            st.image(
                imagen_url,
                use_container_width=True
            )
            st.markdown(
                '<p style="text-align: center; color: gray; font-size: 0.8em; margin-top: 0.5rem;">Imagen de referencia</p>',
                unsafe_allow_html=True
            )
        except:
            pass
            
    except:
        pass