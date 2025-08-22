import onnxruntime as ort
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from config import PATHS, RETRAINING_CONFIG

class ModelUtils:
    """Utilidades para cargar y usar el modelo ONNX"""
    
    def __init__(self):
        self.session = None
        self.species_names = None
        self.num_classes = None
        self.metadata = None
    
    def cargar_modelo(self):
        """Carga el modelo ONNX desde archivo y sus metadatos asociados."""
        try:
            model_file = PATHS["model_file"].parent / "plant_classifier.onnx"
            
            if not model_file.exists():
                print(f"❌ Modelo ONNX no encontrado: {model_file}")
                return False
            
            self.session = ort.InferenceSession(str(model_file))
            print(f"✅ Modelo ONNX cargado: {model_file}")
            
            metadata_file = PATHS["model_file"].parent / "model_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                
                self.species_names = self.metadata.get("species_names", [])
                self.num_classes = self.metadata.get("num_classes", 0)
                
                print(f"✅ Metadatos cargados: {len(self.species_names)} especies")
            else:
                if PATHS["species_list_file"].exists():
                    with open(PATHS["species_list_file"], 'r', encoding='utf-8') as f:
                        self.species_names = json.load(f)
                    self.num_classes = len(self.species_names)
                    print(f"⚠️ Metadatos cargados desde backup: {self.num_classes} especies")
                else:
                    print(f"❌ No se encontraron metadatos ni lista de especies")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False
    
    def predecir_especie(self, imagen_procesada, especies_excluir=None):
        """Predice la especie de planta a partir de una imagen procesada usando el modelo ONNX."""
        if self.session is None:
            return {"error": "Modelo no cargado"}
        
        try:
            if imagen_procesada.dtype != np.float32:
                imagen_procesada = imagen_procesada.astype(np.float32)
            
            input_name = self.session.get_inputs()[0].name
            output = self.session.run(None, {input_name: imagen_procesada})
            
            logits = output[0][0]  # Primer output, primera muestra
            
            exp_logits = np.exp(logits - np.max(logits))
            predicciones = exp_logits / np.sum(exp_logits)
            predicciones_originales = predicciones.copy()
            
            if especies_excluir:
                print(f"🚫 ModelUtils: Excluyendo {len(especies_excluir)} especies")
                especies_excluidas_indices = []
                
                for especie in especies_excluir:
                    if especie in self.species_names:
                        idx = self.species_names.index(especie)
                        especies_excluidas_indices.append(idx)
                        predicciones[idx] = 1e-10
                        print(f"   🚫 Excluida: {especie} (índice {idx})")
                
                suma_predicciones = np.sum(predicciones)
                if suma_predicciones > 0:
                    predicciones = predicciones / suma_predicciones
            
            indices_ordenados = np.argsort(predicciones_originales)[::-1]
            
            idx_prediccion = None
            for idx in indices_ordenados:
                especie_candidata = self.species_names[idx]
                if especies_excluir is None or especie_candidata not in especies_excluir:
                    idx_prediccion = idx
                    confianza = float(predicciones_originales[idx])
                    especie_predicha = especie_candidata
                    break
            
            if idx_prediccion is None:
                idx_prediccion = indices_ordenados[0]
                confianza = float(predicciones_originales[idx_prediccion])
                especie_predicha = self.species_names[idx_prediccion]
                print(f"⚠️ Todas las especies están excluidas, usando: {especie_predicha}")
            
            top_indices = np.argsort(predicciones_originales)[::-1]
            top_predicciones = []
            
            for idx in top_indices[:10]:
                especie_top = self.species_names[idx]
                confianza_top = float(predicciones_originales[idx])
                
                if especies_excluir is None or especie_top not in especies_excluir:
                    top_predicciones.append({
                        "especie": especie_top,
                        "confianza": confianza_top,
                        "indice": int(idx)
                    })
            
            resultado = {
                "especie_predicha": especie_predicha,
                "confianza": confianza,
                "indice_especie": int(idx_prediccion),
                "top_predicciones": top_predicciones
            }
            
            print(f"✅ ModelUtils: Predicción final: {especie_predicha} (confianza: {confianza:.4f})")
            return resultado
            
        except Exception as e:
            print(f"❌ ERROR en predicción: {e}")
            return {"error": f"Error en predicción: {e}"}
    
    def obtener_top_especies(self, imagen_procesada, top_k=6, especies_excluir=None):
        """Obtiene las K especies con mayor probabilidad de predicción."""
        prediccion = self.predecir_especie(imagen_procesada, especies_excluir)
        
        if "error" in prediccion:
            print(f"❌ Error en obtener_top_especies: {prediccion['error']}")
            return []
        
        top_especies = prediccion["top_predicciones"][:top_k]
        return top_especies
    
    def validar_modelo_entrenado(self):
        """Valida que el modelo esté correctamente cargado y funcional."""
        validacion = {
            "modelo_cargado": self.session is not None,
            "metadatos_disponibles": self.metadata is not None,
            "especies_disponibles": len(self.species_names) if self.species_names else 0,
            "errores": [],
            "advertencias": [],
            "es_valido": False
        }
        
        if self.session is None:
            validacion["errores"].append("Modelo ONNX no cargado")
            return validacion
        
        try:
            test_image = np.random.random((1, 224, 224, 3)).astype(np.float32)
            
            input_name = self.session.get_inputs()[0].name
            output = self.session.run(None, {input_name: test_image})
            
            if output[0].shape[1] == self.num_classes:
                validacion["prediccion_prueba"] = "exitosa"
                validacion["es_valido"] = True
            else:
                validacion["errores"].append("Error en forma de predicción de prueba")
                
        except Exception as e:
            validacion["errores"].append(f"Error en predicción de prueba: {e}")
        
        return validacion
    
    def obtener_info_modelo(self):
        """Retorna información detallada sobre el modelo cargado."""
        if self.session is None:
            return {"error": "Modelo no cargado"}
        
        info = {
            "cargado": True,
            "especies": self.num_classes,
            "nombres_especies": self.species_names[:10] if self.species_names else [],
            "tipo_modelo": "ONNX Runtime",
            "input_shape": self.session.get_inputs()[0].shape,
            "output_shape": self.session.get_outputs()[0].shape
        }
        
        if self.metadata:
            info.update({
                "fecha_entrenamiento": self.metadata.get("timestamp", "N/A"),
                "metricas": self.metadata.get("metricas", {}),
                "configuracion": self.metadata.get("model_config", {})
            })
        
        return info
    
    def verificar_necesidad_reentrenamiento(self):
        """Evalua si el modelo necesita ser reentrenado basándose en criterios configurados."""
        from utils.image_processing import obtener_estadisticas_dataset
        
        stats = obtener_estadisticas_dataset()
        nuevas = stats["imagenes_nuevas"]
        
        criterios = RETRAINING_CONFIG
        
        total_nuevas = nuevas["total"]
        especies_con_nuevas = nuevas["especies_afectadas"]
        
        cumple_total = total_nuevas >= criterios["min_images_total"]
        cumple_especies = especies_con_nuevas >= criterios["min_species_with_new_images"]
        
        ultimo_entrenamiento = "N/A"
        if self.metadata:
            ultimo_entrenamiento = self.metadata.get("timestamp", "N/A")
        
        resultado = {
            "necesita_reentrenamiento": cumple_total and cumple_especies,
            "criterios": {
                "total_imagenes": {
                    "actual": total_nuevas,
                    "requerido": criterios["min_images_total"],
                    "cumple": cumple_total
                },
                "especies_afectadas": {
                    "actual": especies_con_nuevas,
                    "requerido": criterios["min_species_with_new_images"],
                    "cumple": cumple_especies
                }
            },
            "ultimo_entrenamiento": ultimo_entrenamiento,
            "estadisticas_actuales": stats
        }
        
        return resultado
    
    def obtener_especies_similares(self, especie_objetivo, cantidad=5):
        """Encuentra especies similares a la especie objetivo basándose en taxonomía."""
        if not self.species_names or especie_objetivo not in self.species_names:
            return []
        
        try:
            genero_objetivo = especie_objetivo.split('_')[0]
            
            especies_similares = []
            for especie in self.species_names:
                if especie != especie_objetivo and especie.startswith(genero_objetivo):
                    especies_similares.append(especie)
                
                if len(especies_similares) >= cantidad:
                    break
            
            return especies_similares
            
        except Exception as e:
            print(f"❌ Error obteniendo especies similares: {e}")
            return []

def cargar_modelo_global():
    """Carga el modelo ONNX y lo retorna listo para usar."""
    model_utils = ModelUtils()
    
    if model_utils.cargar_modelo():
        return model_utils
    else:
        return None

def verificar_estado_modelo():
    """Verifica el estado actual del modelo y retorna información de diagnóstico."""
    model_utils = ModelUtils()
    
    if not model_utils.cargar_modelo():
        return {
            "disponible": False,
            "error": "No se pudo cargar el modelo ONNX"
        }
    
    validacion = model_utils.validar_modelo_entrenado()
    info = model_utils.obtener_info_modelo()
    necesidad_retrain = model_utils.verificar_necesidad_reentrenamiento()
    
    return {
        "disponible": True,
        "valido": validacion["es_valido"],
        "info": info,
        "validacion": validacion,
        "reentrenamiento": necesidad_retrain
    }

if __name__ == "__main__":
    print("🤖 INFORMACIÓN DEL MODELO ONNX")
    print("=" * 50)
    
    estado = verificar_estado_modelo()
    
    if not estado["disponible"]:
        print(f"❌ {estado['error']}")
    else:
        info = estado["info"]
        print(f"✅ Modelo ONNX disponible")
        print(f"\n📊 INFORMACIÓN:")
        print(f"   - Tipo: {info['tipo_modelo']}")
        print(f"   - Especies: {info['especies']}")
        print(f"   - Input shape: {info['input_shape']}")
        print(f"   - Output shape: {info['output_shape']}")