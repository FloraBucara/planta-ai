"""
Cliente para conectar con el servidor BucaraFlora
"""
import requests
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from datetime import datetime


# Configuración del servidor
SERVER_URL = "https://316bf979b0c9.ngrok-free.app"  # Cambiar a ngrok cuando lo tengamos

def verificar_servidor():
    """Verifica si el servidor está disponible"""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def enviar_feedback(imagen_pil, session_id, especie_predicha, confianza, 
                   feedback_tipo, especie_correcta):
    """
    Envía feedback al servidor
    
    Args:
        imagen_pil: Imagen PIL
        session_id: ID de la sesión
        especie_predicha: Especie que predijo el modelo
        confianza: Confianza de la predicción
        feedback_tipo: 'correcto', 'corregido'
        especie_correcta: Especie correcta según el usuario
    
    Returns:
        dict: Respuesta del servidor
    """
    try:
        # Convertir imagen a base64
        buffered = BytesIO()
        imagen_pil.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Preparar datos
        data = {
            "imagen_base64": img_base64,
            "session_id": session_id,
            "especie_predicha": especie_predicha,
            "confianza_prediccion": confianza,
            "feedback_tipo": feedback_tipo,
            "especie_correcta": especie_correcta
        }
        
        # Enviar al servidor
        response = requests.post(
            f"{SERVER_URL}/api/feedback/guardar_base64",
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "mensaje": f"Error del servidor: {response.status_code}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "mensaje": "No se pudo conectar con el servidor"
        }
    except Exception as e:
        return {
            "success": False,
            "mensaje": f"Error: {str(e)}"
        }

def obtener_estadisticas():
    """Obtiene estadísticas del servidor"""
    try:
        response = requests.get(f"{SERVER_URL}/api/feedback/estadisticas", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def obtener_estadisticas():
    """Obtiene estadísticas del servidor"""
    try:
        response = requests.get(f"{SERVER_URL}/api/feedback/estadisticas", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def obtener_estado_reentrenamiento():
    """Obtiene el estado del reentrenamiento"""
    try:
        response = requests.get(f"{SERVER_URL}/api/reentrenamiento/estado", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Cache para verificar servidor
@st.cache_data(ttl=60)  # Cache por 1 minuto
def servidor_disponible():
    """Verifica disponibilidad del servidor con cache"""
    return verificar_servidor()