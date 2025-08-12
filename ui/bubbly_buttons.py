# ui/bubbly_buttons.py
# Componente para botones con efecto bubbly (burbujas)

import streamlit as st

def aplicar_estilos_bubbly():
    """Aplica los estilos CSS para botones bubbly"""
    st.markdown("""
    <style>
        /* Variables CSS para BucaraFlora */
        :root {
            --green-primary: #2E8B57;
            --green-secondary: #228B22;
            --button-text-color: #fff;
        }

        /* Botón Bubbly Base */
        .bubbly-button {
            font-family: 'Helvetica', 'Arial', sans-serif !important;
            display: inline-block !important;
            font-size: 1.1em !important;
            font-weight: 600 !important;
            padding: 1em 2em !important;
            margin: 20px auto !important;
            -webkit-appearance: none !important;
            appearance: none !important;
            background-color: var(--green-primary) !important;
            color: var(--button-text-color) !important;
            border-radius: 12px !important;
            border: none !important;
            cursor: pointer !important;
            position: relative !important;
            transition: transform ease-in 0.1s, box-shadow ease-in 0.25s !important;
            box-shadow: 0 4px 25px rgba(46, 139, 87, 0.4) !important;
            width: 100% !important;
            max-width: 300px !important;
        }

        .bubbly-button:focus {
            outline: 0 !important;
        }

        /* Pseudoelementos para las burbujas */
        .bubbly-button:before, 
        .bubbly-button:after {
            position: absolute !important;
            content: '' !important;
            display: block !important;
            width: 140% !important;
            height: 100% !important;
            left: -20% !important;
            z-index: -1000 !important;
            transition: all ease-in-out 0.5s !important;
            background-repeat: no-repeat !important;
        }

        /* Burbujas superiores */
        .bubbly-button:before {
            display: none !important;
            top: -75% !important;
            background-image:  
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, transparent 20%, var(--green-primary) 20%, transparent 30%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%), 
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, transparent 10%, var(--green-primary) 15%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%) !important;
            background-size: 10% 10%, 20% 20%, 15% 15%, 20% 20%, 18% 18%, 10% 10%, 15% 15%, 10% 10%, 18% 18% !important;
        }

        /* Burbujas inferiores */
        .bubbly-button:after {
            display: none !important;
            bottom: -75% !important;
            background-image:  
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%), 
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, transparent 10%, var(--green-primary) 15%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%),
                radial-gradient(circle, var(--green-primary) 20%, transparent 20%) !important;
            background-size: 15% 15%, 20% 20%, 18% 18%, 20% 20%, 15% 15%, 10% 10%, 20% 20% !important;
        }

        /* Estado activo */
        .bubbly-button:active {
            transform: scale(0.95) !important;
            background-color: var(--green-secondary) !important;
            box-shadow: 0 2px 25px rgba(46, 139, 87, 0.2) !important;
        }

        /* Animación cuando se activa */
        .bubbly-button.animate:before {
            display: block !important;
            animation: topBubbles ease-in-out 0.75s forwards !important;
        }

        .bubbly-button.animate:after {
            display: block !important;
            animation: bottomBubbles ease-in-out 0.75s forwards !important;
        }

        /* Keyframes para burbujas superiores */
        @keyframes topBubbles {
            0% {
                background-position: 5% 90%, 10% 90%, 10% 90%, 15% 90%, 25% 90%, 25% 90%, 40% 90%, 55% 90%, 70% 90%;
            }
            50% {
                background-position: 0% 80%, 0% 20%, 10% 40%, 20% 0%, 30% 30%, 22% 50%, 50% 50%, 65% 20%, 90% 30%;
            }
            100% {
                background-position: 0% 70%, 0% 10%, 10% 30%, 20% -10%, 30% 20%, 22% 40%, 50% 40%, 65% 10%, 90% 20%;
                background-size: 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%;
            }
        }

        /* Keyframes para burbujas inferiores */
        @keyframes bottomBubbles {
            0% {
                background-position: 10% -10%, 30% 10%, 55% -10%, 70% -10%, 85% -10%, 70% -10%, 70% 0%;
            }
            50% {
                background-position: 0% 80%, 20% 80%, 45% 60%, 60% 100%, 75% 70%, 95% 60%, 105% 0%;
            }
            100% {
                background-position: 0% 90%, 20% 90%, 45% 70%, 60% 110%, 75% 80%, 95% 70%, 110% 10%;
                background-size: 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%;
            }
        }

        /* Ocultar botones Streamlit por defecto */
        .stButton > button {
            display: none !important;
        }

        /* Contenedor para centrar botón */
        .bubbly-button-container {
            display: flex !important;
            justify-content: center !important;
            margin: 1rem 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def bubbly_button(texto, key, icono="🌱"):
    """
    Crea un botón con efecto bubbly
    
    Args:
        texto: Texto del botón
        key: Key único para Streamlit
        icono: Emoji o icono a mostrar
    
    Returns:
        bool: True si el botón fue presionado
    """
    
    # Aplicar estilos
    aplicar_estilos_bubbly()
    
    # HTML del botón bubbly
    button_html = f"""
    <div class="bubbly-button-container">
        <button class="bubbly-button" 
                onclick="
                    this.classList.add('animate');
                    setTimeout(() => this.classList.remove('animate'), 800);
                    setTimeout(() => window.parent.document.querySelector('[data-testid=\\"stButton\\"][data-key=\\"{key}\\"] button').click(), 200);
                ">
            {icono} {texto}
        </button>
    </div>
    """
    
    # Mostrar botón personalizado
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Botón invisible de Streamlit para capturar clicks
    return st.button("", key=key, help=texto)

# Funciones específicas para cada botón
def boton_subir_imagen(key="btn_subir"):
    """Botón para subir imagen con efecto bubbly"""
    return bubbly_button("Subir imagen desde mi dispositivo", key, "📁")

def boton_tomar_foto(key="btn_foto"):
    """Botón para tomar foto con efecto bubbly"""
    return bubbly_button("Tomar foto con la cámara", key, "📷")

def boton_identificar(key="btn_identificar"):
    """Botón para identificar planta con efecto bubbly"""
    return bubbly_button("Identificar Planta", key, "🌱")