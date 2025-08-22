"""
Cliente para conectar con el servidor BucaraFlora
"""
import requests
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from datetime import datetime


SERVER_URL = "https://720729e5ea60.ngrok-free.app"

def verificar_servidor():
    """Verifica la disponibilidad del servidor realizando una petición de salud."""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def enviar_feedback(imagen_pil, session_id, especie_predicha, confianza, 
                   feedback_tipo, especie_correcta):
    """Envía feedback de usuario sobre predicciones del modelo al servidor."""
    try:
        buffered = BytesIO()
        imagen_pil.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        data = {
            "imagen_base64": img_base64,
            "session_id": session_id,
            "especie_predicha": especie_predicha,
            "confianza_prediccion": confianza,
            "feedback_tipo": feedback_tipo,
            "especie_correcta": especie_correcta
        }
        
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
    """Obtiene estadísticas generales del servidor y el sistema de feedback."""
    try:
        response = requests.get(f"{SERVER_URL}/api/feedback/estadisticas", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def obtener_estado_reentrenamiento():
    """Consulta el estado actual del proceso de reentrenamiento del modelo."""
    try:
        response = requests.get(f"{SERVER_URL}/api/reentrenamiento/estado", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=60)
def servidor_disponible():
    """Verifica la disponibilidad del servidor utilizando cache para optimizar peticiones."""
    return verificar_servidor()