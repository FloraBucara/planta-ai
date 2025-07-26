import tensorflow as tf
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))
from config import PATHS, RETRAINING_CONFIG

class ModelUtils:
    """Utilidades para cargar y usar el modelo entrenado"""
    
    def __init__(self):
        self.model = None
        self.species_names = None
        self.num_classes = None
        self.metadata = None
    
    def cargar_modelo(self):
        """
        Carga el modelo entrenado y sus metadatos
        
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            # Verificar que existe el archivo del modelo
            if not PATHS["model_file"].exists():
                print(f"❌ Modelo no encontrado: {PATHS['model_file']}")
                return False
            
            # Cargar modelo
            self.model = tf.keras.models.load_model(PATHS["model_file"])
            print(f"✅ Modelo cargado: {PATHS['model_file']}")
            
            # Cargar metadatos
            metadata_file = PATHS["model_file"].parent / "model_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                
                self.species_names = self.metadata.get("species_names", [])
                self.num_classes = self.metadata.get("num_classes", 0)
                
                print(f"✅ Metadatos cargados: {len(self.species_names)} especies")
            else:
                # Intentar cargar desde species_list.json como backup
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
        """
        Predice la especie de una imagen - VERSIÓN CORREGIDA
        
        Args:
            imagen_procesada: Imagen ya procesada (numpy array con batch dimension)
            especies_excluir: Lista de especies a excluir de la predicción
        
        Returns:
            dict: Información de la predicción
        """
        if self.model is None:
            return {"error": "Modelo no cargado"}
        
        try:
            # Hacer predicción inicial
            predicciones = self.model.predict(imagen_procesada, verbose=0)
            predicciones = predicciones[0]  # Remover dimensión batch
            predicciones_originales = predicciones.copy()  # Guardar copia original
            
            # 🔧 DEBUG: Verificar exclusiones
            if especies_excluir:
                print(f"🚫 ModelUtils: Excluyendo {len(especies_excluir)} especies")
                especies_excluidas_indices = []
                
                # Aplicar exclusiones si se especifican
                for especie in especies_excluir:
                    if especie in self.species_names:
                        idx = self.species_names.index(especie)
                        especies_excluidas_indices.append(idx)
                        # Poner probabilidad muy baja (no 0 para evitar división por 0)
                        predicciones[idx] = 1e-10
                        print(f"   🚫 Excluida: {especie} (índice {idx}, prob original: {predicciones_originales[idx]:.4f})")
                
                # Re-normalizar probabilidades
                suma_predicciones = np.sum(predicciones)
                if suma_predicciones > 0:
                    predicciones = predicciones / suma_predicciones
                    print(f"✅ ModelUtils: Predicciones re-normalizadas (suma: {suma_predicciones:.4f})")
                else:
                    print("⚠️ WARNING: Suma de predicciones es 0 después de exclusiones")
                    # Fallback: restaurar predicciones originales y tomar siguiente mejor
                    predicciones = predicciones_originales.copy()
                    for idx in especies_excluidas_indices:
                        predicciones[idx] = 0
            
            # Obtener índice de la predicción principal
            idx_prediccion = np.argmax(predicciones)
            confianza = float(predicciones[idx_prediccion])
            especie_predicha = self.species_names[idx_prediccion]
            
            # 🔧 VERIFICACIÓN CRÍTICA: ¿La predicción está en especies excluidas?
            if especies_excluir and especie_predicha in especies_excluir:
                print(f"⚠️ CRITICAL: Predicción '{especie_predicha}' está en especies excluidas!")
                
                # Buscar la siguiente mejor que NO esté excluida
                indices_ordenados = np.argsort(predicciones)[::-1]  # De mayor a menor
                
                prediccion_encontrada = False
                for idx in indices_ordenados:
                    especie_candidata = self.species_names[idx]
                    if especies_excluir is None or especie_candidata not in especies_excluir:
                        idx_prediccion = idx
                        confianza = float(predicciones[idx])
                        especie_predicha = especie_candidata
                        print(f"✅ OVERRIDE: Usando '{especie_predicha}' en su lugar (confianza: {confianza:.4f})")
                        prediccion_encontrada = True
                        break
                
                if not prediccion_encontrada:
                    print("❌ CRITICAL: No se encontró ninguna especie válida!")
                    return {
                        "error": "No hay especies válidas disponibles",
                        "mensaje": "Todas las especies posibles están excluidas"
                    }
            
            # 🔧 SEGUNDA VERIFICACIÓN: Confianza mínima
            if confianza < 1e-8:
                print(f"⚠️ WARNING: Confianza muy baja: {confianza}")
                # Buscar alternativa con mejor confianza
                indices_ordenados = np.argsort(predicciones_originales)[::-1]
                for idx in indices_ordenados:
                    especie_candidata = self.species_names[idx]
                    confianza_candidata = float(predicciones_originales[idx])
                    if (especies_excluir is None or especie_candidata not in especies_excluir) and confianza_candidata > 1e-8:
                        idx_prediccion = idx
                        confianza = confianza_candidata
                        especie_predicha = especie_candidata
                        print(f"✅ FALLBACK: Usando '{especie_predicha}' (confianza original: {confianza:.4f})")
                        break
            
            # Obtener top-K predicciones (sin especies excluidas)
            top_indices = np.argsort(predicciones_originales)[::-1]
            top_predicciones = []
            
            for idx in top_indices:
                especie_top = self.species_names[idx]
                confianza_top = float(predicciones_originales[idx])
                
                # Solo incluir si no está excluida
                if especies_excluir is None or especie_top not in especies_excluir:
                    top_predicciones.append({
                        "especie": especie_top,
                        "confianza": confianza_top,
                        "indice": int(idx)
                    })
                
                # Limitar a top 10
                if len(top_predicciones) >= 10:
                    break
            
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
        """
        Obtiene las top-K especies más probables
        
        Args:
            imagen_procesada: Imagen procesada
            top_k: Número de especies a retornar
            especies_excluir: Especies a excluir
        
        Returns:
            list: Lista de especies ordenadas por probabilidad
        """
        prediccion = self.predecir_especie(imagen_procesada, especies_excluir)
        
        if "error" in prediccion:
            print(f"❌ Error en obtener_top_especies: {prediccion['error']}")
            return []
        
        # Retornar solo las primeras top_k
        top_especies = prediccion["top_predicciones"][:top_k]
        
        print(f"✅ ModelUtils: Retornando {len(top_especies)} especies (solicitadas: {top_k})")
        for i, esp in enumerate(top_especies[:3]):  # Log de las primeras 3
            print(f"   {i+1}. {esp['especie']} ({esp['confianza']:.4f})")
        
        return top_especies
    
    def validar_modelo_entrenado(self):
        """
        Valida que el modelo esté correctamente entrenado y funcional
        
        Returns:
            dict: Información detallada sobre la validación
        """
        validacion = {
            "modelo_cargado": self.model is not None,
            "metadatos_disponibles": self.metadata is not None,
            "especies_disponibles": len(self.species_names) if self.species_names else 0,
            "errores": [],
            "advertencias": []
        }
        
        if self.model is None:
            validacion["errores"].append("Modelo no cargado")
            return validacion
        
        # Verificar arquitectura
        try:
            input_shape = self.model.input_shape
            output_shape = self.model.output_shape
            
            validacion["input_shape"] = input_shape
            validacion["output_shape"] = output_shape
            validacion["total_parametros"] = self.model.count_params()
            
            # Verificar que el output coincida con el número de especies
            if output_shape[-1] != self.num_classes:
                validacion["errores"].append(
                    f"Output del modelo ({output_shape[-1]}) no coincide con número de especies ({self.num_classes})"
                )
        
        except Exception as e:
            validacion["errores"].append(f"Error verificando arquitectura: {e}")
        
        # Verificar que se puede hacer una predicción de prueba
        try:
            # Crear imagen de prueba
            test_image = np.random.random((1, 224, 224, 3)).astype(np.float32)
            test_pred = self.model.predict(test_image, verbose=0)
            
            if test_pred.shape[1] == self.num_classes:
                validacion["prediccion_prueba"] = "exitosa"
            else:
                validacion["errores"].append("Error en forma de predicción de prueba")
                
        except Exception as e:
            validacion["errores"].append(f"Error en predicción de prueba: {e}")
        
        # Verificar metadatos
        if self.metadata:
            validacion["fecha_entrenamiento"] = self.metadata.get("timestamp", "N/A")
            validacion["configuracion_modelo"] = self.metadata.get("model_config", {})
        
        # Determinar si es válido
        validacion["es_valido"] = len(validacion["errores"]) == 0
        
        return validacion
    
    def obtener_info_modelo(self):
        """
        Obtiene información completa del modelo
        
        Returns:
            dict: Información del modelo
        """
        if self.model is None:
            return {"error": "Modelo no cargado"}
        
        info = {
            "cargado": True,
            "especies": self.num_classes,
            "nombres_especies": self.species_names[:10] if self.species_names else [],  # Primeras 10
            "parametros_totales": self.model.count_params(),
            "input_shape": self.model.input_shape,
            "output_shape": self.model.output_shape
        }
        
        if self.metadata:
            info.update({
                "fecha_entrenamiento": self.metadata.get("timestamp", "N/A"),
                "metricas": self.metadata.get("metricas", {}),
                "configuracion": self.metadata.get("model_config", {})
            })
        
        return info
    
    def verificar_necesidad_reentrenamiento(self):
        """
        Verifica si es necesario reentrenar el modelo según los criterios configurados
        
        Returns:
            dict: Información sobre necesidad de reentrenamiento
        """
        from utils.image_processing import obtener_estadisticas_dataset
        
        # Obtener estadísticas actuales
        stats = obtener_estadisticas_dataset()
        nuevas = stats["imagenes_nuevas"]
        
        # Criterios de reentrenamiento
        criterios = RETRAINING_CONFIG
        
        total_nuevas = nuevas["total"]
        especies_con_nuevas = nuevas["especies_afectadas"]
        
        # Verificar criterios
        cumple_total = total_nuevas >= criterios["min_images_total"]
        cumple_especies = especies_con_nuevas >= criterios["min_species_with_new_images"]
        
        # Verificar último reentrenamiento
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
        """
        Obtiene especies similares basándose en características del modelo
        
        Args:
            especie_objetivo: Nombre de la especie objetivo
            cantidad: Número de especies similares a retornar
        
        Returns:
            list: Lista de especies similares
        """
        if not self.species_names or especie_objetivo not in self.species_names:
            return []
        
        try:
            # Para un modelo más sofisticado, esto podría usar embeddings
            # Por ahora, retornar especies del mismo género o familia
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
    
    def test_prediccion_con_exclusiones(self, test_image=None, especies_a_excluir=None):
        """
        Función de test para verificar que las exclusiones funcionan correctamente
        
        Args:
            test_image: Imagen de prueba (si None, genera una aleatoria)
            especies_a_excluir: Lista de especies a excluir para el test
        
        Returns:
            dict: Resultados del test
        """
        if not self.model:
            return {"error": "Modelo no cargado"}
        
        try:
            # Crear imagen de prueba si no se proporciona
            if test_image is None:
                test_image = np.random.random((1, 224, 224, 3)).astype(np.float32)
            
            print(f"\n🧪 TEST DE EXCLUSIONES:")
            print(f"{'='*40}")
            
            # Predicción sin exclusiones
            resultado_sin_exclusion = self.predecir_especie(test_image)
            if "error" in resultado_sin_exclusion:
                return resultado_sin_exclusion
            
            print(f"📊 SIN EXCLUSIONES:")
            print(f"   Predicción: {resultado_sin_exclusion['especie_predicha']}")
            print(f"   Confianza: {resultado_sin_exclusion['confianza']:.4f}")
            
            # Predicción con exclusiones
            if especies_a_excluir:
                print(f"\n🚫 EXCLUYENDO: {especies_a_excluir}")
                resultado_con_exclusion = self.predecir_especie(test_image, especies_a_excluir)
                
                if "error" in resultado_con_exclusion:
                    print(f"❌ Error con exclusiones: {resultado_con_exclusion['error']}")
                    return resultado_con_exclusion
                
                print(f"📊 CON EXCLUSIONES:")
                print(f"   Predicción: {resultado_con_exclusion['especie_predicha']}")
                print(f"   Confianza: {resultado_con_exclusion['confianza']:.4f}")
                
                # Verificar que la exclusión funcionó
                if resultado_con_exclusion['especie_predicha'] in especies_a_excluir:
                    print(f"❌ ERROR: La predicción sigue en especies excluidas!")
                    return {"error": "Test de exclusión falló"}
                else:
                    print(f"✅ SUCCESS: Exclusión funcionó correctamente")
                
                return {
                    "test_exitoso": True,
                    "sin_exclusion": resultado_sin_exclusion,
                    "con_exclusion": resultado_con_exclusion,
                    "exclusion_funciono": resultado_con_exclusion['especie_predicha'] not in especies_a_excluir
                }
            else:
                return {
                    "test_exitoso": True,
                    "sin_exclusion": resultado_sin_exclusion,
                    "nota": "No se proporcionaron especies para excluir"
                }
                
        except Exception as e:
            print(f"❌ Error en test: {e}")
            return {"error": f"Error en test: {e}"}

def cargar_modelo_global():
    """
    Función de conveniencia para cargar el modelo globalmente
    
    Returns:
        ModelUtils: Instancia con modelo cargado o None si falla
    """
    model_utils = ModelUtils()
    
    if model_utils.cargar_modelo():
        return model_utils
    else:
        return None

def verificar_estado_modelo():
    """
    Función para verificar rápidamente el estado del modelo
    
    Returns:
        dict: Estado del modelo
    """
    model_utils = ModelUtils()
    
    if not model_utils.cargar_modelo():
        return {
            "disponible": False,
            "error": "No se pudo cargar el modelo"
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

def test_exclusiones_modelo():
    """
    Función para testear que las exclusiones funcionen correctamente
    """
    print("🧪 TESTING EXCLUSIONES DEL MODELO")
    print("=" * 50)
    
    model_utils = ModelUtils()
    if not model_utils.cargar_modelo():
        print("❌ No se pudo cargar el modelo para test")
        return False
    
    # Test con especies conocidas
    especies_test = model_utils.species_names[:3] if model_utils.species_names else []
    
    if len(especies_test) < 2:
        print("❌ No hay suficientes especies para test")
        return False
    
    # Hacer test
    resultado = model_utils.test_prediccion_con_exclusiones(
        especies_a_excluir=[especies_test[0]]
    )
    
    if resultado.get("test_exitoso"):
        print("\n✅ TEST DE EXCLUSIONES EXITOSO")
        return True
    else:
        print(f"\n❌ TEST DE EXCLUSIONES FALLÓ: {resultado.get('error', 'Error desconocido')}")
        return False

if __name__ == "__main__":
    # Si ejecutas este archivo directamente, muestra información del modelo
    print("🤖 INFORMACIÓN DEL MODELO")
    print("=" * 50)
    
    estado = verificar_estado_modelo()
    
    if not estado["disponible"]:
        print(f"❌ {estado['error']}")
        print("\n💡 Para entrenar un modelo inicial ejecuta:")
        print("   python model/train_model.py")
    else:
        info = estado["info"]
        validacion = estado["validacion"]
        retrain = estado["reentrenamiento"]
        
        print(f"✅ Modelo disponible y {'válido' if estado['valido'] else 'con problemas'}")
        print(f"\n📊 INFORMACIÓN GENERAL:")
        print(f"   - Especies: {info['especies']}")
        print(f"   - Parámetros: {info['parametros_totales']:,}")
        print(f"   - Input shape: {info['input_shape']}")
        print(f"   - Fecha entrenamiento: {info.get('fecha_entrenamiento', 'N/A')}")
        
        if 'metricas' in info and info['metricas']:
            metricas = info['metricas']
            print(f"\n📈 MÉTRICAS:")
            print(f"   - Precisión: {metricas.get('accuracy', 'N/A'):.3f}")
            print(f"   - Top-3 Accuracy: {metricas.get('top3_accuracy', 'N/A'):.3f}")
            print(f"   - Loss: {metricas.get('loss', 'N/A'):.3f}")
        
        print(f"\n🔄 REENTRENAMIENTO:")
        if retrain["necesita_reentrenamiento"]:
            print(f"   ✅ Es recomendable reentrenar")
            print(f"   📊 Nuevas imágenes: {retrain['criterios']['total_imagenes']['actual']}")
            print(f"   🌿 Especies afectadas: {retrain['criterios']['especies_afectadas']['actual']}")
        else:
            print(f"   ⏰ No necesita reentrenamiento aún")
            total = retrain['criterios']['total_imagenes']
            especies = retrain['criterios']['especies_afectadas']
            print(f"   📊 Nuevas imágenes: {total['actual']}/{total['requerido']}")
            print(f"   🌿 Especies afectadas: {especies['actual']}/{especies['requerido']}")
        
        if not estado["valido"] and validacion["errores"]:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            for error in validacion["errores"]:
                print(f"   - {error}")
        
        # Ejecutar test de exclusiones
        print(f"\n🧪 EJECUTANDO TEST DE EXCLUSIONES...")
        test_exclusiones_modelo()