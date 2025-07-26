import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))
from config import PATHS, RETRAINING_CONFIG

class SesionPrediccion:
    """Clase para manejar una sesión individual de predicción"""
    
    def __init__(self, imagen_original=None):
        self.session_id = str(uuid.uuid4())[:8]  # ID corto único
        self.imagen_original = imagen_original
        self.intento_actual = 1
        self.max_intentos = RETRAINING_CONFIG["max_attempts_per_prediction"]
        self.predicciones_anteriores = []
        self.especies_descartadas = set()
        self.timestamp_inicio = datetime.now()
        self.estado = "activa"  # activa, completada, abandonada
        self.resultado_final = None
    
    def agregar_prediccion(self, especie, confianza, correcto=None):
        """
        Agrega una predicción a la sesión
        
        Args:
            especie: Nombre de la especie predicha
            confianza: Nivel de confianza (0-1)
            correcto: True/False si el usuario confirmó, None si no respondió
        """
        prediccion = {
            "intento": self.intento_actual,
            "especie": especie,
            "confianza": float(confianza),
            "timestamp": datetime.now().isoformat(),
            "correcto": correcto
        }
        
        self.predicciones_anteriores.append(prediccion)
        
        if correcto is False:
            # Si es incorrecta, descartar esta especie para futuros intentos
            self.especies_descartadas.add(especie)
            self.intento_actual += 1
        elif correcto is True:
            # Sesión completada exitosamente
            self.estado = "completada"
            self.resultado_final = {
                "especie_final": especie,
                "intentos_necesarios": self.intento_actual,
                "metodo": "prediccion_automatica"
            }
    
    def completar_con_seleccion_manual(self, especie_seleccionada):
        """Completa la sesión con selección manual del usuario"""
        self.estado = "completada"
        self.resultado_final = {
            "especie_final": especie_seleccionada,
            "intentos_necesarios": self.intento_actual,
            "metodo": "seleccion_manual"
        }
    
    def abandonar_sesion(self):
        """Marca la sesión como abandonada"""
        self.estado = "abandonada"
    
    def necesita_top_especies(self):
        """Verifica si debe mostrar las top especies"""
        return self.intento_actual > self.max_intentos
    
    def tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido desde el inicio"""
        return datetime.now() - self.timestamp_inicio
    
    def to_dict(self):
        """Convierte la sesión a diccionario para serialización"""
        return {
            "session_id": self.session_id,
            "intento_actual": self.intento_actual,
            "max_intentos": self.max_intentos,
            "predicciones_anteriores": self.predicciones_anteriores,
            "especies_descartadas": list(self.especies_descartadas),
            "timestamp_inicio": self.timestamp_inicio.isoformat(),
            "estado": self.estado,
            "resultado_final": self.resultado_final,
            "tiempo_transcurrido": str(self.tiempo_transcurrido())
        }

class SessionManager:
    """Gestiona todas las sesiones de predicción activas"""
    
    def __init__(self):
        self.sesiones_activas = {}
        self.sesiones_archivo = PATHS["session_data_file"]
        self.max_sesiones_memoria = 100  # Máximo de sesiones en memoria
        self.tiempo_expiracion = timedelta(hours=2)  # Sesiones expiran en 2 horas
        
        # Cargar sesiones existentes
        self.cargar_sesiones()
    
    def crear_sesion(self, imagen_original=None):
        """
        Crea una nueva sesión de predicción
        
        Args:
            imagen_original: Imagen original del usuario
        
        Returns:
            SesionPrediccion: Nueva sesión creada
        """
        sesion = SesionPrediccion(imagen_original)
        self.sesiones_activas[sesion.session_id] = sesion
        
        # Limpiar sesiones viejas si hay demasiadas
        self._limpiar_sesiones_viejas()
        
        print(f"✅ Nueva sesión creada: {sesion.session_id}")
        return sesion
    
    def obtener_sesion(self, session_id):
        """
        Obtiene una sesión por su ID
        
        Args:
            session_id: ID de la sesión
        
        Returns:
            SesionPrediccion o None si no existe
        """
        return self.sesiones_activas.get(session_id)
    
    def actualizar_sesion(self, session_id, **kwargs):
        """Actualiza una sesión existente"""
        if session_id in self.sesiones_activas:
            sesion = self.sesiones_activas[session_id]
            
            # Actualizar atributos
            for key, value in kwargs.items():
                if hasattr(sesion, key):
                    setattr(sesion, key, value)
            
            return sesion
        return None
    
    def completar_sesion(self, session_id, especie_final, metodo="prediccion"):
        """
        Marca una sesión como completada
        
        Args:
            session_id: ID de la sesión
            especie_final: Especie confirmada
            metodo: Método de confirmación
        """
        if session_id in self.sesiones_activas:
            sesion = self.sesiones_activas[session_id]
            
            if metodo == "seleccion_manual":
                sesion.completar_con_seleccion_manual(especie_final)
            else:
                # Actualizar la última predicción como correcta
                if sesion.predicciones_anteriores:
                    sesion.predicciones_anteriores[-1]["correcto"] = True
                sesion.estado = "completada"
                sesion.resultado_final = {
                    "especie_final": especie_final,
                    "intentos_necesarios": sesion.intento_actual,
                    "metodo": metodo
                }
            
            # Guardar sesión completada
            self.guardar_sesion_completada(sesion)
            
            print(f"✅ Sesión completada: {session_id} -> {especie_final}")
            return sesion
        return None
    
    def _limpiar_sesiones_viejas(self):
        """Limpia sesiones viejas de la memoria"""
        ahora = datetime.now()
        sesiones_a_eliminar = []
        
        for session_id, sesion in self.sesiones_activas.items():
            if (ahora - sesion.timestamp_inicio) > self.tiempo_expiracion:
                sesiones_a_eliminar.append(session_id)
        
        for session_id in sesiones_a_eliminar:
            # Guardar sesión antes de eliminar si no está completada
            sesion = self.sesiones_activas[session_id]
            if sesion.estado == "activa":
                sesion.abandonar_sesion()
                self.guardar_sesion_completada(sesion)
            
            del self.sesiones_activas[session_id]
            print(f"🧹 Sesión expirada eliminada: {session_id}")
        
        # Si aún hay demasiadas, eliminar las más antiguas
        if len(self.sesiones_activas) > self.max_sesiones_memoria:
            sesiones_ordenadas = sorted(
                self.sesiones_activas.items(),
                key=lambda x: x[1].timestamp_inicio
            )
            
            for session_id, sesion in sesiones_ordenadas[:-self.max_sesiones_memoria]:
                if sesion.estado == "activa":
                    sesion.abandonar_sesion()
                    self.guardar_sesion_completada(sesion)
                del self.sesiones_activas[session_id]
                print(f"🧹 Sesión antigua eliminada: {session_id}")
    
    def cargar_sesiones(self):
        """Carga sesiones desde archivo (solo para estadísticas)"""
        try:
            if self.sesiones_archivo.exists():
                with open(self.sesiones_archivo, 'r', encoding='utf-8') as f:
                    # Solo cargar para estadísticas, no restaurar sesiones activas
                    pass
        except Exception as e:
            print(f"⚠️ No se pudieron cargar sesiones: {e}")
    
    def guardar_sesion_completada(self, sesion):
        """Guarda una sesión completada para estadísticas"""
        try:
            sesiones_historial = []
            
            # Cargar historial existente
            if self.sesiones_archivo.exists():
                with open(self.sesiones_archivo, 'r', encoding='utf-8') as f:
                    try:
                        sesiones_historial = json.load(f)
                    except json.JSONDecodeError:
                        sesiones_historial = []
            
            # Agregar nueva sesión
            sesiones_historial.append(sesion.to_dict())
            
            # Mantener solo las últimas 1000 sesiones
            if len(sesiones_historial) > 1000:
                sesiones_historial = sesiones_historial[-1000:]
            
            # Guardar
            with open(self.sesiones_archivo, 'w', encoding='utf-8') as f:
                json.dump(sesiones_historial, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Sesión guardada en historial: {sesion.session_id}")
            
        except Exception as e:
            print(f"❌ Error guardando sesión: {e}")
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de las sesiones
        
        Returns:
            dict: Estadísticas de uso
        """
        stats = {
            "sesiones_activas": len(self.sesiones_activas),
            "sesiones_historial": 0,
            "exito_primer_intento": 0,
            "exito_tres_intentos": 0,
            "requirio_seleccion_manual": 0,
            "sesiones_abandonadas": 0,
            "especies_mas_consultadas": {},
            "tiempo_promedio_sesion": 0
        }
        
        try:
            # Leer historial completo
            if self.sesiones_archivo.exists():
                with open(self.sesiones_archivo, 'r', encoding='utf-8') as f:
                    sesiones_historial = json.load(f)
                
                stats["sesiones_historial"] = len(sesiones_historial)
                
                if sesiones_historial:
                    # Analizar estadísticas
                    primer_intento = 0
                    tres_intentos = 0
                    manual = 0
                    abandonadas = 0
                    especies_count = {}
                    tiempos = []
                    
                    for sesion_data in sesiones_historial:
                        estado = sesion_data.get("estado", "")
                        resultado = sesion_data.get("resultado_final", {})
                        
                        if estado == "completada" and resultado:
                            intentos = resultado.get("intentos_necesarios", 0)
                            metodo = resultado.get("metodo", "")
                            especie = resultado.get("especie_final", "")
                            
                            if intentos == 1:
                                primer_intento += 1
                            if intentos <= 3:
                                tres_intentos += 1
                            if metodo == "seleccion_manual":
                                manual += 1
                            
                            # Contar especies
                            if especie:
                                especies_count[especie] = especies_count.get(especie, 0) + 1
                            
                            # Tiempo de sesión
                            tiempo_str = sesion_data.get("tiempo_transcurrido", "0:00:00")
                            try:
                                # Parse tiempo (formato "H:MM:SS.microseconds")
                                tiempo_parts = tiempo_str.split(":")
                                if len(tiempo_parts) >= 2:
                                    minutos = int(tiempo_parts[1])
                                    tiempos.append(minutos)
                            except:
                                pass
                                
                        elif estado == "abandonada":
                            abandonadas += 1
                    
                    # Calcular porcentajes
                    total_completadas = primer_intento + manual
                    if total_completadas > 0:
                        stats["exito_primer_intento"] = primer_intento / total_completadas
                        stats["exito_tres_intentos"] = tres_intentos / total_completadas
                        stats["requirio_seleccion_manual"] = manual / total_completadas
                    
                    stats["sesiones_abandonadas"] = abandonadas
                    
                    # Top 5 especies más consultadas
                    especies_ordenadas = sorted(especies_count.items(), key=lambda x: x[1], reverse=True)
                    stats["especies_mas_consultadas"] = dict(especies_ordenadas[:5])
                    
                    # Tiempo promedio
                    if tiempos:
                        stats["tiempo_promedio_sesion"] = sum(tiempos) / len(tiempos)
        
        except Exception as e:
            print(f"❌ Error calculando estadísticas: {e}")
        
        return stats

# ==================== NUEVO SESSION MANAGER MEJORADO ====================

class PlantPredictor:
    """Sistema principal de predicción de plantas"""
    
    def __init__(self):
        self.model_utils = None
        self.modelo_cargado = False
        self.cargar_modelo()
    
    def cargar_modelo(self):
        """Carga el modelo entrenado"""
        try:
            from model.model_utils import ModelUtils
            self.model_utils = ModelUtils()
            self.modelo_cargado = self.model_utils.cargar_modelo()
            
            if self.modelo_cargado:
                print(f"✅ Predictor: Modelo cargado: {len(self.model_utils.species_names)} especies")
            else:
                print("❌ Predictor: No se pudo cargar el modelo")
                
        except Exception as e:
            print(f"❌ Error cargando modelo en predictor: {e}")
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
            from utils.image_processing import procesar_imagen_simple
            imagen_procesada = procesar_imagen_simple(imagen)
            
            if imagen_procesada is None:
                return {
                    "error": "Error procesando imagen",
                    "mensaje": "No se pudo procesar la imagen"
                }
            
            # Debug info
            if especies_excluir:
                print(f"🚫 Predictor: Excluyendo {len(especies_excluir)} especies: {list(especies_excluir)[:3]}...")
            
            # Hacer predicción
            resultado = self.model_utils.predecir_especie(imagen_procesada, especies_excluir)
            
            if "error" in resultado:
                return resultado
            
            # Obtener información adicional de la especie
            from utils.firebase_config import obtener_info_planta
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
            
            print(f"✅ Predictor: {resultado['especie_predicha']} (confianza: {resultado['confianza']:.3f})")
            return respuesta
            
        except Exception as e:
            print(f"❌ Error en predicción: {e}")
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
            from utils.image_processing import procesar_imagen_simple
            imagen_procesada = procesar_imagen_simple(imagen)
            
            if imagen_procesada is None:
                return []
            
            print(f"🔍 Predictor: Obteniendo top {cantidad} especies, excluyendo {len(especies_excluir) if especies_excluir else 0}")
            
            # Obtener top especies
            top_especies = self.model_utils.obtener_top_especies(
                imagen_procesada, cantidad, especies_excluir
            )
            
            # Agregar información completa de cada especie
            especies_completas = []
            
            for especie_data in top_especies:
                from utils.firebase_config import obtener_info_planta
                info_especie = obtener_info_planta(especie_data["especie"])
                
                especie_completa = {
                    "especie": especie_data["especie"],
                    "confianza": especie_data["confianza"],
                    "info": info_especie
                }
                
                especies_completas.append(especie_completa)
            
            print(f"✅ Predictor: Retornando {len(especies_completas)} especies")
            return especies_completas
            
        except Exception as e:
            print(f"❌ Error obteniendo top especies: {e}")
            return []
    
    def guardar_resultado_feedback(self, imagen, especie_final, session_id, 
                                 correcto=True, metodo="prediccion"):
        """
        Guarda el resultado del feedback del usuario
        """
        try:
            # Guardar análisis en Firebase
            from utils.firebase_config import guardar_analisis
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
            print(f"❌ Error guardando feedback: {e}")
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

class EnhancedSessionManager:
    """Gestiona las sesiones de predicción en Streamlit con mejoras"""
    
    def __init__(self):
        self.predictor = PlantPredictor()
        self.session_manager = SessionManager()
    
    def iniciar_nueva_sesion(self, imagen_original):
        """Inicia una nueva sesión de predicción"""
        sesion = self.session_manager.crear_sesion(imagen_original)
        return sesion
    
    def procesar_intento_prediccion(self, sesion, imagen, especies_excluir=None):
        """
        Procesa un intento de predicción en la sesión - VERSIÓN MEJORADA
        
        Args:
            sesion: SesionPrediccion actual
            imagen: Imagen a predecir
            especies_excluir: Especies a excluir
        
        Returns:
            dict: Resultado de la predicción
        """
        # Debug: Verificar especies a excluir
        if especies_excluir:
            print(f"🚫 SessionManager: Excluyendo especies: {list(especies_excluir)}")
        else:
            print("ℹ️ SessionManager: Sin especies excluidas")
        
        # Hacer predicción
        resultado = self.predictor.predecir_planta(imagen, especies_excluir)
        
        if resultado.get("exito"):
            especie_predicha = resultado['especie_predicha']
            print(f"✅ SessionManager: Nueva predicción: {especie_predicha} ({resultado['confianza']:.3f})")
            
            # VERIFICAR: ¿La predicción está en las especies excluidas?
            if especies_excluir and especie_predicha in especies_excluir:
                print(f"⚠️ WARNING: El modelo sigue prediciendo una especie excluida: {especie_predicha}")
                # Forzar a obtener la siguiente mejor opción
                return self._obtener_siguiente_mejor_prediccion(imagen, especies_excluir)
            
            # Agregar predicción a la sesión
            sesion.agregar_prediccion(
                especie=especie_predicha,
                confianza=resultado["confianza"],
                correcto=None  # Usuario aún no ha confirmado
            )
        else:
            print(f"❌ SessionManager: Error en predicción: {resultado.get('mensaje', 'Desconocido')}")
        
        return resultado
    
    def _obtener_siguiente_mejor_prediccion(self, imagen, especies_excluir):
        """
        Obtiene la siguiente mejor predicción cuando la primera está excluida
        """
        try:
            print("🔄 SessionManager: Obteniendo siguiente mejor predicción...")
            
            # Obtener top 10 predicciones para tener más opciones
            top_especies = self.predictor.obtener_top_especies(imagen, cantidad=10, especies_excluir=especies_excluir)
            
            if top_especies and len(top_especies) > 0:
                # Tomar la primera que no esté excluida
                for especie_data in top_especies:
                    especie = especie_data["especie"]
                    if not especies_excluir or especie not in especies_excluir:
                        print(f"✅ SessionManager: Siguiente mejor predicción: {especie}")
                        
                        # Crear resultado en el formato esperado
                        return {
                            "exito": True,
                            "especie_predicha": especie,
                            "confianza": especie_data["confianza"],
                            "info_especie": especie_data["info"],
                            "top_predicciones": top_especies[:5],
                            "timestamp": datetime.now().isoformat(),
                            "metodo": "siguiente_mejor"
                        }
            
            # Si no encontramos ninguna, retornar error
            return {
                "error": "No se encontraron predicciones alternativas",
                "mensaje": "Todas las mejores predicciones están excluidas"
            }
            
        except Exception as e:
            print(f"❌ SessionManager: Error obteniendo siguiente predicción: {e}")
            return {
                "error": "Error obteniendo alternativas",
                "mensaje": str(e)
            }
    
    def confirmar_prediccion_correcta(self, sesion, especie_confirmada):
        """Confirma que la predicción fue correcta"""
        sesion.agregar_prediccion(
            especie=especie_confirmada,
            confianza=sesion.predicciones_anteriores[-1]["confianza"] if sesion.predicciones_anteriores else 0.0,
            correcto=True
        )
        
        # Guardar feedback
        return self.predictor.guardar_resultado_feedback(
            imagen=sesion.imagen_original,
            especie_final=especie_confirmada,
            session_id=sesion.session_id,
            correcto=True,
            metodo="prediccion"
        )
    
    def rechazar_prediccion(self, sesion, especie_rechazada):
        """Rechaza la predicción actual"""
        print(f"🚫 SessionManager: Rechazando predicción: {especie_rechazada}")
        
        # Actualizar sesión
        if sesion.predicciones_anteriores:
            sesion.predicciones_anteriores[-1]["correcto"] = False
        
        sesion.especies_descartadas.add(especie_rechazada)
        sesion.intento_actual += 1
        
        print(f"📊 SessionManager: Intento actual: {sesion.intento_actual}/{sesion.max_intentos}")
        print(f"🚫 SessionManager: Especies descartadas: {list(sesion.especies_descartadas)}")
        
        return sesion.necesita_top_especies()
    
    def completar_con_seleccion_manual(self, sesion, especie_seleccionada):
        """Completa la sesión con selección manual del usuario"""
        sesion.completar_con_seleccion_manual(especie_seleccionada)
        
        # Guardar feedback
        return self.predictor.guardar_resultado_feedback(
            imagen=sesion.imagen_original,
            especie_final=especie_seleccionada,
            session_id=sesion.session_id,
            correcto=False,  # No fue predicción correcta automática
            metodo="seleccion_manual"
        )
    
    def obtener_top_especies_para_seleccion(self, sesion):
        """Obtiene las top especies para selección manual"""
        cantidad = RETRAINING_CONFIG["top_species_to_show"]
        
        print(f"🔍 SessionManager: Obteniendo {cantidad} especies, excluyendo: {list(sesion.especies_descartadas)}")
        
        return self.predictor.obtener_top_especies(
            imagen=sesion.imagen_original,
            cantidad=cantidad,
            especies_excluir=sesion.especies_descartadas
        )

# Instancia global del gestor de sesiones mejorado
session_manager = EnhancedSessionManager()

def crear_nueva_sesion(imagen_original=None):
    """Función de conveniencia para crear una nueva sesión"""
    return session_manager.iniciar_nueva_sesion(imagen_original)

def obtener_sesion_activa(session_id):
    """Función de conveniencia para obtener una sesión"""
    return session_manager.session_manager.obtener_sesion(session_id)

def completar_sesion_exitosa(session_id, especie_final, metodo="prediccion"):
    """Función de conveniencia para completar una sesión"""
    return session_manager.session_manager.completar_sesion(session_id, especie_final, metodo)

def obtener_estadisticas_sesiones():
    """Función de conveniencia para obtener estadísticas"""
    return session_manager.session_manager.obtener_estadisticas()

def verificar_sistema_prediccion():
    """Verifica que el sistema de predicción esté funcionando"""
    try:
        predictor = PlantPredictor()
        
        if not predictor.verificar_modelo_disponible():
            return {
                "disponible": False,
                "error": "Modelo no disponible",
                "solucion": "Ejecuta: python model/train_model.py"
            }
        
        # Test básico
        import numpy as np
        test_image = np.random.random((224, 224, 3)).astype(np.float32)
        resultado = predictor.predecir_planta(test_image)
        
        if resultado.get("exito"):
            return {
                "disponible": True,
                "especies": len(predictor.model_utils.species_names),
                "test_especie": resultado["especie_predicha"],
                "test_confianza": resultado["confianza"]
            }
        else:
            return {
                "disponible": False,
                "error": resultado.get("error", "Error desconocido")
            }
            
    except Exception as e:
        return {
            "disponible": False,
            "error": f"Error en sistema: {e}"
        }

if __name__ == "__main__":
    # Test del sistema de sesiones
    print("🔄 TESTING SISTEMA DE SESIONES MEJORADO")
    print("=" * 50)
    
    # Crear sesión de prueba
    sesion = crear_nueva_sesion()
    print(f"✅ Sesión creada: {sesion.session_id}")
    
    # Simular predicciones
    sesion.agregar_prediccion("Agave_americana_L", 0.85, False)
    print(f"✅ Predicción 1 agregada (incorrecta)")
    
    sesion.agregar_prediccion("Aloe_maculata_All", 0.92, True)
    print(f"✅ Predicción 2 agregada (correcta)")
    
    # Completar sesión
    completar_sesion_exitosa(sesion.session_id, "Aloe_maculata_All")
    print(f"✅ Sesión completada")
    
    # Mostrar estadísticas
    stats = obtener_estadisticas_sesiones()
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   - Sesiones activas: {stats['sesiones_activas']}")
    print(f"   - Sesiones en historial: {stats['sesiones_historial']}")
    
    print(f"\n✅ Sistema de sesiones funcionando correctamente")