import numpy as np
import sys
from pathlib import Path
from datetime import datetime
import requests
import json

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from config import RETRAINING_CONFIG, API_CONFIG
from model.model_utils import ModelUtils
from utils.image_processing import procesar_imagen_simple
from utils.firebase_config import obtener_info_planta, guardar_analisis


class PlantPredictor:
    """Sistema principal de predicción de plantas"""
    
    def __init__(self):
        self.model_utils = None
        self.modelo_cargado = False
        self.cargar_modelo()
    
    def cargar_modelo(self):
        """Carga el modelo entrenado"""
        try:
            self.model_utils = ModelUtils()
            self.modelo_cargado = self.model_utils.cargar_modelo()
            
            if self.modelo_cargado:
                print(f"✅ Modelo cargado: {len(self.model_utils.species_names)} especies")
            else:
                print("❌ No se pudo cargar el modelo")
                
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            self.modelo_cargado = False
    
    def verificar_modelo_disponible(self):
        """Verifica si el modelo está disponible"""
        return self.modelo_cargado and self.model_utils is not None
    
    def predecir_planta(self, imagen, especies_excluir=None):
        """
        Predice la especie de una planta
        
        Args:
            imagen: Imagen a analizar (PIL Image, numpy array, etc.)
            especies_excluir: Lista de especies a excluir
        
        Returns:
            dict: Resultado de la predicción
        """
        if not self.verificar_modelo_disponible():
            return {
                "error": "Modelo no disponible",
                "mensaje": "El modelo no está cargado o entrenado"
            }
        
        try:
            # Procesar imagen
            imagen_procesada = procesar_imagen_simple(imagen)
            
            if imagen_procesada is None:
                return {
                    "error": "Error procesando imagen",
                    "mensaje": "No se pudo procesar la imagen"
                }
            
            # Hacer predicción
            resultado = self.model_utils.predecir_especie(imagen_procesada, especies_excluir)
            
            if "error" in resultado:
                return resultado
            
            # Obtener información adicional de la especie
            info_especie = obtener_info_planta(resultado["especie_predicha"])
            
            # Preparar respuesta completa
            respuesta = {
                "exito": True,
                "especie_predicha": resultado["especie_predicha"],
                "confianza": resultado["confianza"],
                "info_especie": info_especie,
                "top_predicciones": resultado["top_predicciones"][:5],  # Top 5
                "timestamp": datetime.now().isoformat()
            }
            
            return respuesta
            
        except Exception as e:
            return {
                "error": "Error en predicción",
                "mensaje": str(e)
            }
    
    def obtener_top_especies(self, imagen, cantidad=6, especies_excluir=None):
        """
        Obtiene las top especies más probables
        
        Args:
            imagen: Imagen a analizar
            cantidad: Número de especies a retornar
            especies_excluir: Especies a excluir
        
        Returns:
            list: Lista de especies con información completa
        """
        if not self.verificar_modelo_disponible():
            return []
        
        try:
            # Procesar imagen
            imagen_procesada = procesar_imagen_simple(imagen)
            
            if imagen_procesada is None:
                return []
            
            # Obtener top especies
            top_especies = self.model_utils.obtener_top_especies(
                imagen_procesada, cantidad, especies_excluir
            )
            
            # Agregar información completa de cada especie
            especies_completas = []
            
            for especie_data in top_especies:
                info_especie = obtener_info_planta(especie_data["especie"])
                
                especie_completa = {
                    "especie": especie_data["especie"],
                    "confianza": especie_data["confianza"],
                    "info": info_especie
                }
                
                especies_completas.append(especie_completa)
            
            return especies_completas
            
        except Exception as e:
            print(f"❌ Error obteniendo top especies: {e}")
            return []
    
    def guardar_resultado_feedback(self, imagen, especie_final, session_id, 
                                 correcto=True, metodo="prediccion"):
        """
        Guarda el resultado del feedback del usuario
        
        Args:
            imagen: Imagen original
            especie_final: Especie confirmada por el usuario
            session_id: ID de la sesión
            correcto: Si la predicción fue correcta
            metodo: Método usado (prediccion, seleccion_manual)
        
        Returns:
            dict: Resultado del guardado
        """
        try:
            # Guardar análisis en Firebase
            datos_analisis = {
                "especie_final": especie_final,
                "session_id": session_id,
                "correcto": correcto,
                "metodo": metodo,
                "timestamp": datetime.now().isoformat()
            }
            
            guardar_analisis(datos_analisis)
            
            # Enviar imagen a API para guardado local (vía Ngrok)
            resultado_api = self._enviar_imagen_a_api(
                imagen, especie_final, session_id, correcto, metodo
            )
            
            return {
                "exito": True,
                "mensaje": "Feedback guardado correctamente",
                "api_response": resultado_api
            }
            
        except Exception as e:
            return {
                "error": "Error guardando feedback",
                "mensaje": str(e)
            }
    
    def _enviar_imagen_a_api(self, imagen, especie, session_id, correcto, metodo):
        """Envía imagen a la API para guardado (vía Ngrok)"""
        try:
            # Convertir imagen a base64
            import base64
            import io
            from PIL import Image
            
            # Asegurar que es PIL Image
            if not isinstance(imagen, Image.Image):
                if isinstance(imagen, np.ndarray):
                    imagen = Image.fromarray((imagen * 255).astype(np.uint8))
                else:
                    return {"error": "Formato de imagen no soportado"}
            
            # Convertir a base64
            img_buffer = io.BytesIO()
            imagen.save(img_buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Preparar datos para API
            api_data = {
                "image_data": img_str,
                "especie": especie,
                "session_id": session_id,
                "correcto": correcto,
                "metodo": metodo
            }
            
            # Intentar enviar a API (esto funcionará cuando tengas Ngrok corriendo)
            # Por ahora, simular el envío
            print(f"📤 Simulando envío a API: {especie} ({'correcto' if correcto else 'corregido'})")
            
            return {
                "status": "simulado",
                "mensaje": "Imagen enviada a API (simulado)"
            }
            
            # Cuando tengas Ngrok funcionando, usa esto:
            # api_url = "URL_DE_NGROK/api/save_image"
            # response = requests.post(api_url, json=api_data, timeout=10)
            # return response.json()
            
        except Exception as e:
            return {"error": f"Error enviando a API: {e}"}

