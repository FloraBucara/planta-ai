import streamlit as st
from pathlib import Path
import base64

def mostrar_header():
    """Muestra el header principal de la aplicación con logo centrado y texto descriptivo."""
    logo_path = Path("assets/logo.png")
    
    if logo_path.exists():
        with open(logo_path, "rb") as file:
            logo_base64 = base64.b64encode(file.read()).decode()
        
        html_logo = f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: -2.5rem 0 0.25rem 0;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 300px; height: auto;" />
        </div>
        """
        st.markdown(html_logo, unsafe_allow_html=True)
    else:
        html_titulo = """
        <div style="text-align: center; margin: -0.5rem 0 0.25rem 0;">
            <h1 style="background: linear-gradient(90deg, #2E8B57, #98FB98); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: bold; margin: 0;">
                🌱 BucaraFlora - Identificador de Plantas IA
            </h1>
        </div>
        """
        st.markdown(html_titulo, unsafe_allow_html=True)
    
    html_descripcion = """
    <div style="text-align: center; margin-bottom: 1rem; margin-top: 1rem;">
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
            <strong>Sube una foto de tu planta y descubre qué especie es</strong>
        </p>
    </div>
    """
    st.markdown(html_descripcion, unsafe_allow_html=True)
        
def mostrar_info_planta_completa(info_planta):
    """Muestra información completa de una planta con formato visualmente atractivo y organizado."""
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
    """Muestra la primera imagen disponible de la especie desde el servidor API."""
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
    """Muestra imagen de referencia sin la barra superior de Streamlit para mejor presentación."""
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