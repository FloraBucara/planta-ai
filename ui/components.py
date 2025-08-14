import streamlit as st
from pathlib import Path
import base64  # Agregado para la opción de centrado con CSS

def mostrar_header():
    """Muestra el header principal de la aplicación con logo - CORREGIDO"""
    # Intentar cargar logo local
    logo_path = Path("assets/logo.png")
    
    # Logo centrado
    if logo_path.exists():
        # Opción con CSS - Centrado perfecto
        with open(logo_path, "rb") as file:
            logo_base64 = base64.b64encode(file.read()).decode()
        
        html_logo = f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: -2rem 0 0.25rem 0;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 300px; height: auto;" />
        </div>
        """
        # ↑↑↑ AQUÍ CAMBIAS EL TAMAÑO: width: 400px ↑↑↑
        st.markdown(html_logo, unsafe_allow_html=True)
    else:
        # Fallback: Título con texto si no hay logo
        html_titulo = """
        <div style="text-align: center; margin: -0.5rem 0 0.25rem 0;">
            <h1 style="background: linear-gradient(90deg, #2E8B57, #98FB98); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: bold; margin: 0;">
                🌱 BucaraFlora - Identificador de Plantas IA
            </h1>
        </div>
        """
        st.markdown(html_titulo, unsafe_allow_html=True)
    
    # Texto descriptivo centrado
    html_descripcion = """
    <div style="text-align: center; margin-bottom: 1rem; margin-top: 1rem;">
        <p style="font-size: 1.1rem; color: #666; margin: 0;">
            <strong>Sube una foto de tu planta y descubre qué especie es</strong>
        </p>
    </div>
    """
    st.markdown(html_descripcion, unsafe_allow_html=True)
        
def mostrar_info_planta_completa(info_planta):
    """
    Muestra la información completa de la planta de forma visualmente atractiva
    """
    datos = info_planta.get('datos', {})
    fuente = info_planta.get('fuente', 'desconocido')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Nombre común y científico
        st.markdown(f"### 🌿 {datos.get('nombre_comun', 'Nombre no disponible')}")
        st.markdown(f"**Nombre científico:** *{datos.get('nombre_cientifico', 'N/A')}*")
        
        # Descripción
        descripcion = datos.get('descripcion', '')
        if descripcion and fuente == 'firestore':
            st.markdown("#### 📝 Descripción")
            st.markdown(f'<div class="info-card">{descripcion}</div>', unsafe_allow_html=True)
                    
        if datos.get('fuente'):
            st.markdown(f"**📚 Fuente:** {datos.get('fuente')}")
    
    with col2:
        # Imagen desde servidor
        mostrar_imagen_referencia(datos.get('nombre_cientifico', ''))

    # Información taxonómica
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
        
        # Convertir a formato de carpeta
        nombre_carpeta = nombre_cientifico.replace(' ', '_')
        
        # Codificar URL
        especie_encoded = quote(nombre_carpeta)
        imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
        
        # Mostrar imagen directamente
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
        
        # Convertir a formato de carpeta
        nombre_carpeta = nombre_cientifico.replace(' ', '_')
        especie_encoded = quote(nombre_carpeta)
        imagen_url = f"{SERVER_URL}/api/image-referencia/{especie_encoded}"
        
        # Mostrar imagen SIN caption para evitar barra
        try:
            st.image(
                imagen_url,
                use_container_width=True
            )
            # Caption manual sin barra
            st.markdown(
                '<p style="text-align: center; color: gray; font-size: 0.8em; margin-top: 0.5rem;">Imagen de referencia</p>',
                unsafe_allow_html=True
            )
        except:
            pass
            
    except:
        pass