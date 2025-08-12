# ui/loading_buttons.py
# Componente para botones con efecto loading

import streamlit as st

def aplicar_estilos_loading():
    """Aplica los estilos CSS para botones con loading"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600&display=swap');

        @keyframes loading {
            0%   { cy: 10; }
            25%  { cy: 3; }
            50%  { cy: 10; }
        }

        /* Botón Loading Principal */
        .loading-btn {
            background: none !important;
            border: none !important;
            color: #ffffff !important;
            cursor: pointer !important;
            font-family: 'Quicksand', sans-serif !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            height: 50px !important;
            outline: none !important;
            overflow: hidden !important;
            padding: 0 15px !important;
            position: relative !important;
            width: 100% !important;
            max-width: 250px !important;
            border-radius: 25px !important;
            transition: all 0.3s ease !important;
            margin: 10px auto !important;
            display: block !important;
        }

        .loading-btn::before {
            background: linear-gradient(135deg, #2E8B57, #228B22) !important;
            border-radius: 25px !important;
            box-shadow: 
                0 4px 15px rgba(46, 139, 87, 0.3),
                0 2px 5px rgba(0, 0, 0, 0.2) inset !important;
            content: '' !important;
            display: block !important;
            height: 100% !important;
            margin: 0 auto !important;
            position: relative !important;
            transition: all 0.3s cubic-bezier(0.39, 1.86, 0.64, 1) !important;
            width: 100% !important;
        }

        .loading-btn.confirm::before {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52) !important;
            box-shadow: 
                0 4px 15px rgba(255, 107, 107, 0.3),
                0 2px 5px rgba(0, 0, 0, 0.2) inset !important;
        }

        /* Estados del botón */
        .loading-btn.ready .submit-message svg {
            opacity: 1 !important;
            top: 1px !important;
            transition: top 0.4s ease 0.6s, opacity 0.3s linear 0.6s !important;
        }

        .loading-btn.ready .submit-message .button-text span {
            top: 0 !important;
            opacity: 1 !important;
            transition: all 0.2s ease calc(var(--dr, 0s) + 0.6s) !important;
        }

        .loading-btn.loading::before {
            transition: transform 0.3s ease !important;
            transform: scaleX(0.8) !important;
        }

        .loading-btn.loading .loading-message {
            opacity: 1 !important;
        }

        .loading-btn.loading .loading-circle {
            animation-duration: 1s !important;
            animation-iteration-count: infinite !important;
            animation-name: loading !important;
        }

        .loading-btn.complete .submit-message svg {
            top: -30px !important;
            transition: none !important;
        }

        .loading-btn.complete .submit-message .button-text span {
            top: -8px !important;
            transition: none !important;
        }

        .loading-btn.complete .loading-message {
            top: 80px !important;
        }

        .loading-btn.complete .success-message .button-text span {
            left: 0 !important;
            opacity: 1 !important;
            transition: all 0.2s ease calc(var(--d, 0s) + 1s) !important;
        }

        .loading-btn.complete .success-message svg { 
            stroke-dashoffset: 0 !important;
            transition: stroke-dashoffset 0.3s ease-in-out 1.4s !important;
        }

        /* Contenido del botón */
        .button-text span {
            opacity: 0;
            position: relative;
            font-weight: 600;
        }

        .message {
            left: 50%;
            position: absolute;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
        }

        .message svg {
            display: inline-block;
            fill: none;
            margin-right: 8px;
            stroke-linecap: round;
            stroke-linejoin: round;
            stroke-width: 2.5;
        }

        .submit-message .button-text span {
            top: 8px;
            transition: all 0.2s ease var(--d, 0s);
        }

        .submit-message svg {
            color: #ffffff;
            margin-left: -1px;
            opacity: 0;
            position: relative;
            top: 30px;
            transition: top 0.4s ease, opacity 0.3s linear;
            width: 16px;
        }

        .loading-message {
            opacity: 0;
            transition: opacity 0.3s linear 0.3s, top 0.4s cubic-bezier(0.22, 0, 0.41, -0.57);
        }

        .loading-message svg {
            fill: #ffffff;
            margin: 0;
            width: 24px;
        }

        .success-message .button-text span {
            left: 8px;
            transition: all 0.2s ease var(--dr, 0s);
        }
        
        .success-message svg {
            color: #90EE90;
            stroke-dasharray: 20;
            stroke-dashoffset: 20;
            transition: stroke-dashoffset 0.3s ease-in-out;
            width: 16px;
        }

        .loading-circle:nth-child(2) { animation-delay: 0.1s; }
        .loading-circle:nth-child(3) { animation-delay: 0.2s; }

        /* Hover effects */
        .loading-btn:hover::before {
            transform: scale(1.02) !important;
            box-shadow: 
                0 6px 20px rgba(46, 139, 87, 0.4),
                0 2px 5px rgba(0, 0, 0, 0.2) inset !important;
        }

        .loading-btn.confirm:hover::before {
            box-shadow: 
                0 6px 20px rgba(255, 107, 107, 0.4),
                0 2px 5px rgba(0, 0, 0, 0.2) inset !important;
        }

        /* Ocultar botones Streamlit por defecto */
        .stButton > button {
            display: none !important;
        }

        .loading-button-container {
            display: flex !important;
            justify-content: center !important;
            margin: 1rem 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def loading_button(texto, key, tipo="success", icono="✅", texto_loading="Guardando...", texto_success="¡Guardado!"):
    """
    Crea un botón con efecto de loading
    
    Args:
        texto: Texto inicial del botón
        key: Key único para Streamlit  
        tipo: "success" (verde) o "confirm" (rojo)
        icono: Emoji inicial
        texto_loading: Texto durante loading
        texto_success: Texto al completar
    
    Returns:
        bool: True si el botón fue presionado
    """
    
    aplicar_estilos_loading()
    
    # Generar ID único para el botón
    button_id = f"loading_btn_{key}"
    
    # Determinar clase CSS
    css_class = "loading-btn ready"
    if tipo == "confirm":
        css_class += " confirm"
    
    # HTML del botón
    button_html = f"""
    <div class="loading-button-container">
        <button class="{css_class}" id="{button_id}" 
                onclick="triggerLoadingButton('{button_id}'); document.querySelector('[data-testid=\\"stButton\\"][data-key=\\"{key}\\"] button').click();">
            
            <!-- Estado inicial -->
            <div class="message submit-message">
                <svg viewBox="0 0 16 16">
                    <path d="M8 0L10 6L16 8L10 10L8 16L6 10L0 8L6 6L8 0Z"/>
                </svg>
                <span class="button-text">
                    <span style="--d: 0.1s">{icono}</span>
                    <span style="--d: 0.2s">{texto}</span>
                </span>
            </div>

            <!-- Estado loading -->
            <div class="message loading-message">
                <svg viewBox="0 0 24 24">
                    <circle class="loading-circle" cx="4" cy="12" r="3"/>
                    <circle class="loading-circle" cx="12" cy="12" r="3"/>
                    <circle class="loading-circle" cx="20" cy="12" r="3"/>
                </svg>
            </div>

            <!-- Estado success -->
            <div class="message success-message">
                <svg viewBox="0 0 16 16">
                    <path d="M3 8l3 3 7-7"/>
                </svg>
                <span class="button-text">
                    <span style="--d: 0.1s">{texto_success}</span>
                </span>
            </div>
        </button>
    </div>
    
    <script>
        function triggerLoadingButton(buttonId) {{
            const button = document.getElementById(buttonId);
            if (!button) return;
            
            // Start loading
            button.className = button.className.replace('ready', 'loading');
            
            // Complete after 1.5 seconds
            setTimeout(() => {{
                button.className = button.className.replace('loading', 'complete');
            }}, 1500);
            
            // Reset after 3 seconds
            setTimeout(() => {{
                if (button.className.includes('confirm')) {{
                    button.className = 'loading-btn ready confirm';
                }} else {{
                    button.className = 'loading-btn ready';
                }}
            }}, 3000);
        }}
    </script>
    """
    
    # Mostrar botón personalizado
    st.markdown(button_html, unsafe_allow_html=True)
    
    # Botón invisible de Streamlit para capturar clicks
    return st.button("", key=key, help=texto)

# Funciones específicas para los casos de uso
def boton_confirmacion_correcta(key="btn_confirmacion"):
    """Botón para '¡Sí, es correcta!' """
    return loading_button(
        texto="¡Sí, es correcta!",
        key=key,
        tipo="success",
        icono="✅",
        texto_loading="Guardando...",
        texto_success="¡Guardado exitosamente!"
    )

def boton_seleccion_planta(key="btn_seleccion", nombre_planta="esta planta"):
    """Botón para '¡Es esta planta!' """
    return loading_button(
        texto=f"¡Es {nombre_planta}!",
        key=key,
        tipo="confirm", 
        icono="🌿",
        texto_loading="Confirmando...",
        texto_success="¡Selección confirmada!"
    )