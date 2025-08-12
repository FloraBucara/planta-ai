# ui/expand_buttons.py
# Componente para botones expandibles (ver/ocultar información)

import streamlit as st

def aplicar_estilos_expandibles():
    """Aplica los estilos CSS para botones expandibles"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css?family=Mukta:700');
        
        :root {
            --bg: #f0f8ff;
            --white: #fff;
            --green: #2E8B57;
            --blue: #4A90E2;
        }
        
        .expand-button {
            position: relative !important;
            display: inline-block !important;
            cursor: pointer !important;
            outline: none !important;
            border: 0 !important;
            vertical-align: middle !important;
            text-decoration: none !important;
            background: transparent !important;
            padding: 0 !important;
            font-size: inherit !important;
            font-family: 'Mukta', sans-serif !important;
            width: 100% !important;
            max-width: 280px !important;
            height: auto !important;
            margin: 0.5rem auto !important;
        }
        
        .circle {
            transition: all 0.45s cubic-bezier(0.65,0,.076,1) !important;
            position: relative !important;
            display: block !important;
            margin: 0 !important;
            width: 3rem !important;
            height: 3rem !important;
            background: var(--green) !important;
            border-radius: 1.5rem !important;
            box-shadow: 0 3px 12px rgba(46, 139, 87, 0.3) !important;
        }
        
        .circle.collapse {
            background: var(--blue) !important;
            box-shadow: 0 3px 12px rgba(74, 144, 226, 0.3) !important;
        }
        
        .icon {
            transition: all 0.45s cubic-bezier(0.65,0,.076,1) !important;
            position: absolute !important;
            top: 0 !important;
            bottom: 0 !important;
            margin: auto !important;
            background: var(--white) !important;
        }
        
        /* Flecha hacia abajo (expandir) */
        .icon.arrow-down {
            left: 0.9rem !important;
            width: 1.2rem !important;
            height: 0.12rem !important;
            background: none !important;
        }
        
        .icon.arrow-down::before {
            position: absolute !important;
            content: '' !important;
            top: -0.2rem !important;
            right: 0.45rem !important;
            width: 0.5rem !important;
            height: 0.5rem !important;
            border-bottom: 0.12rem solid #fff !important;
            border-right: 0.12rem solid #fff !important;
            transform: rotate(45deg) !important;
        }
        
        /* Flecha hacia arriba (contraer) */
        .icon.arrow-up {
            left: 0.9rem !important;
            width: 1.2rem !important;
            height: 0.12rem !important;
            background: none !important;
        }
        
        .icon.arrow-up::before {
            position: absolute !important;
            content: '' !important;
            top: 0.2rem !important;
            right: 0.45rem !important;
            width: 0.5rem !important;
            height: 0.5rem !important;
            border-top: 0.12rem solid #fff !important;
            border-right: 0.12rem solid #fff !important;
            transform: rotate(-45deg) !important;
        }
        
        .button-text {
            transition: all 0.45s cubic-bezier(0.65,0,.076,1) !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            padding: 0.75rem 0 !important;
            margin: 0 0 0 2rem !important;
            color: var(--green) !important;
            font-weight: 600 !important;
            line-height: 1.6 !important;
            text-align: center !important;
            font-size: 0.95rem !important;
        }
        
        .button-text.collapse-text {
            color: var(--blue) !important;
        }
        
        /* Hover effects para expandir */
        .expand-button:hover .circle {
            width: 100% !important;
            box-shadow: 0 5px 18px rgba(46, 139, 87, 0.4) !important;
        }
        
        .expand-button:hover .circle.collapse {
            box-shadow: 0 5px 18px rgba(74, 144, 226, 0.4) !important;
        }
        
        .expand-button:hover .icon.arrow-down {
            transform: translate(1.8rem, 0) !important;
        }
        
        .expand-button:hover .icon.arrow-up {
            transform: translate(1.8rem, 0) !important;
        }
        
        .expand-button:hover .button-text {
            color: var(--white) !important;
        }
        
        .expand-button:hover .button-text.collapse-text {
            color: var(--white) !important;
        }

        /* Ocultar botones Streamlit por defecto */
        .stButton > button {
            display: none !important;
        }

        .expand-button-container {
            display: flex !important;
            justify-content: center !important;
            margin: 0.5rem 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def expand_button(texto, key, tipo="expand", icono_flecha="▼"):
    """
    Crea un botón expandible
    
    Args:
        texto: Texto del botón
        key: Key único para Streamlit
        tipo: "expand" (verde) o "collapse" (azul)
        icono_flecha: Flecha a mostrar
    
    Returns:
        bool: True si el botón fue presionado
    """
    
    aplicar_estilos_expandibles()
    
    # Determinar clases CSS según el tipo
    circle_class = "circle"
    text_class = "button-text"
    icon_class = "icon arrow-down"
    
    if tipo == "collapse":
        circle_class += " collapse"
        text_class += " collapse-text"
        icon_class = "icon arrow-up"
    
    # HTML del botón expandible
    button_html = f"""
    <div class="expand-button-container">
        <button class="expand-button" 
                onclick="document.querySelector('[data-testid=\\"stButton\\"][data-key=\\"{key}\\"] button').click();">
            <span class="{circle_class}">
                <span class="{icon_class}"></span>
            </span>
            <span class="{text_class}">{icono_flecha} {texto}</span>
        </button>
    </div>
    """
    
    # Mostrar botón personalizado
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Botón invisible de Streamlit para capturar clicks
    return st.button("", key=key, help=texto)

# Funciones específicas para los casos de uso
def boton_ver_informacion(key="btn_ver_info"):
    """Botón para 'Ver información completa' """
    return expand_button(
        texto="Ver información completa",
        key=key,
        tipo="expand",
        icono_flecha="▼"
    )

def boton_ocultar_informacion(key="btn_ocultar_info"):
    """Botón para 'Ocultar información' """
    return expand_button(
        texto="Ocultar información",
        key=key,
        tipo="collapse",
        icono_flecha="▲"
    )

def boton_expandible_toggle(texto_expandir, texto_contraer, key, expandido=False):
    """
    Botón que cambia entre expandir y contraer automáticamente
    
    Args:
        texto_expandir: Texto cuando está contraído
        texto_contraer: Texto cuando está expandido
        key: Key único para Streamlit
        expandido: Estado actual (True = expandido, False = contraído)
    
    Returns:
        bool: True si el botón fue presionado
    """
    
    if expandido:
        return boton_ocultar_informacion(key)
    else:
        return boton_ver_informacion(key)