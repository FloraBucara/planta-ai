# step2_convert_model.py
# PASO 2: Convertir modelo TensorFlow a ONNX

import tensorflow as tf
import tf2onnx
import onnxruntime as ort
import numpy as np
import json
from pathlib import Path
import time

def convert_tensorflow_to_onnx():
    """
    Convierte el modelo TensorFlow existente a formato ONNX
    """
    print("🔄 PASO 2: CONVERSIÓN TENSORFLOW → ONNX")
    print("=" * 60)
    
    # Configurar rutas de archivos
    tf_model_path = Path("model/plant_classifier.h5")
    onnx_model_path = Path("model/plant_classifier.onnx")
    species_path = Path("model/species_list.json")
    
    # Verificar que los archivos originales existen
    print("📂 VERIFICANDO ARCHIVOS ORIGINALES...")
    
    if not tf_model_path.exists():
        print(f"❌ No se encontró el modelo TensorFlow: {tf_model_path}")
        print("💡 Asegúrate de que el archivo plant_classifier.h5 esté en la carpeta model/")
        return False
    
    if not species_path.exists():
        print(f"❌ No se encontró la lista de especies: {species_path}")
        print("💡 Asegúrate de que el archivo species_list.json esté en la carpeta model/")
        return False
    
    print(f"✅ Modelo TensorFlow encontrado: {tf_model_path}")
    print(f"✅ Lista de especies encontrada: {species_path}")
    
    # Paso 1: Cargar modelo TensorFlow
    print("\n🔄 CARGANDO MODELO TENSORFLOW...")
    try:
        # Suprimir logs verbosos de TensorFlow
        tf.get_logger().setLevel('ERROR')
        
        model = tf.keras.models.load_model(str(tf_model_path))
        
        print(f"✅ Modelo TensorFlow cargado exitosamente")
        print(f"   📊 Input shape: {model.input_shape}")
        print(f"   📊 Output shape: {model.output_shape}")
        print(f"   📊 Parámetros totales: {model.count_params():,}")
        
        # Obtener información del modelo
        input_shape = model.input_shape
        output_shape = model.output_shape
        
    except Exception as e:
        print(f"❌ Error cargando modelo TensorFlow: {e}")
        return False
    
    # Paso 2: Cargar lista de especies
    print("\n📋 CARGANDO LISTA DE ESPECIES...")
    try:
        with open(species_path, 'r', encoding='utf-8') as f:
            species_list = json.load(f)
        
        print(f"✅ Lista de especies cargada: {len(species_list)} especies")
        print(f"   🌿 Primeras 3: {species_list[:3]}")
        
        # Verificar consistencia
        expected_classes = output_shape[-1]
        actual_species = len(species_list)
        
        if expected_classes != actual_species:
            print(f"⚠️ WARNING: Inconsistencia detectada:")
            print(f"   Modelo espera: {expected_classes} clases")
            print(f"   Lista tiene: {actual_species} especies")
            
            # Continuar pero advertir
            print("   Continuando con la conversión...")
        
    except Exception as e:
        print(f"❌ Error cargando lista de especies: {e}")
        return False
    
    # Paso 3: Preparar para conversión
    print("\n🔧 PREPARANDO CONVERSIÓN...")
    
    # Definir especificación de entrada (batch variable)
    input_signature = [tf.TensorSpec(
        shape=(None, 224, 224, 3), 
        dtype=tf.float32, 
        name="input_image"
    )]
    
    print(f"✅ Especificación de entrada preparada: {input_signature[0].shape}")
    
    # Paso 4: Convertir a ONNX
    print("\n🚀 INICIANDO CONVERSIÓN A ONNX...")
    print("   ⏱️ Esto puede tardar 1-2 minutos...")
    
    start_time = time.time()
    
    try:
        # Realizar conversión
        onnx_model, _ = tf2onnx.convert.from_keras(
            model,
            input_signature=input_signature,
            opset=13,  # Versión ONNX estable y compatible
            output_path=str(onnx_model_path)
        )
        
        conversion_time = time.time() - start_time
        
        print(f"✅ Conversión completada exitosamente!")
        print(f"   ⏱️ Tiempo de conversión: {conversion_time:.2f} segundos")
        print(f"   💾 Modelo ONNX guardado: {onnx_model_path}")
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}")
        print("💡 Posibles soluciones:")
        print("   - Verifica que el modelo TensorFlow sea válido")
        print("   - Asegúrate de tener suficiente memoria disponible")
        print("   - Intenta reiniciar Python y ejecutar de nuevo")
        return False
    
    # Paso 5: Verificar archivos generados
    print("\n📁 VERIFICANDO ARCHIVOS GENERADOS...")
    
    if not onnx_model_path.exists():
        print(f"❌ El archivo ONNX no se generó: {onnx_model_path}")
        return False
    
    # Comparar tamaños
    tf_size = tf_model_path.stat().st_size / (1024 * 1024)  # MB
    onnx_size = onnx_model_path.stat().st_size / (1024 * 1024)  # MB
    reduction = ((tf_size - onnx_size) / tf_size) * 100
    
    print(f"✅ Archivo ONNX generado correctamente")
    print(f"📊 COMPARACIÓN DE TAMAÑOS:")
    print(f"   TensorFlow (.h5): {tf_size:.2f} MB")
    print(f"   ONNX (.onnx): {onnx_size:.2f} MB")
    print(f"   Reducción: {reduction:.1f}%")
    
    # Paso 6: Probar modelo ONNX
    print("\n🧪 PROBANDO MODELO ONNX...")
    
    try:
        # Cargar sesión ONNX
        print("   🔄 Cargando modelo ONNX...")
        ort_session = ort.InferenceSession(str(onnx_model_path))
        
        # Obtener información de entrada y salida
        input_details = ort_session.get_inputs()[0]
        output_details = ort_session.get_outputs()[0]
        
        print(f"   ✅ Modelo ONNX cargado correctamente")
        print(f"   📊 Input: {input_details.name} {input_details.shape}")
        print(f"   📊 Output: {output_details.name} {output_details.shape}")
        
        # Crear imagen de prueba
        print("   🔄 Creando imagen de prueba...")
        test_image = np.random.random((1, 224, 224, 3)).astype(np.float32)
        
        # Hacer predicción con ONNX
        print("   🔄 Haciendo predicción de prueba con ONNX...")
        start_time = time.time()
        
        onnx_predictions = ort_session.run(
            [output_details.name], 
            {input_details.name: test_image}
        )[0]
        
        onnx_inference_time = time.time() - start_time
        
        # Hacer predicción con TensorFlow (para comparar)
        print("   🔄 Haciendo predicción de prueba con TensorFlow...")
        start_time = time.time()
        
        tf_predictions = model.predict(test_image, verbose=0)
        
        tf_inference_time = time.time() - start_time
        
        # Comparar resultados
        print(f"\n📊 COMPARACIÓN DE PREDICCIONES:")
        print(f"   ⏱️ Tiempo ONNX: {onnx_inference_time:.4f}s")
        print(f"   ⏱️ Tiempo TensorFlow: {tf_inference_time:.4f}s")
        print(f"   🚀 Speedup: {tf_inference_time/onnx_inference_time:.2f}x más rápido")
        
        # Verificar que las predicciones son similares
        max_diff = np.max(np.abs(onnx_predictions - tf_predictions))
        print(f"   📏 Diferencia máxima: {max_diff:.6f}")
        
        if max_diff < 1e-5:
            print(f"   ✅ Predicciones idénticas (diferencia < 1e-5)")
        elif max_diff < 1e-3:
            print(f"   ✅ Predicciones muy similares (diferencia < 1e-3)")
        else:
            print(f"   ⚠️ Predicciones difieren significativamente")
        
        # Mostrar top predicción
        onnx_top_idx = np.argmax(onnx_predictions[0])
        tf_top_idx = np.argmax(tf_predictions[0])
        
        print(f"\n🎯 RESULTADOS DE PRUEBA:")
        print(f"   ONNX top predicción: Clase {onnx_top_idx} ({species_list[onnx_top_idx]})")
        print(f"   TensorFlow top predicción: Clase {tf_top_idx} ({species_list[tf_top_idx]})")
        
        if onnx_top_idx == tf_top_idx:
            print(f"   ✅ Ambos modelos predicen la misma clase")
        else:
            print(f"   ⚠️ Los modelos predicen clases diferentes")
        
    except Exception as e:
        print(f"❌ Error probando modelo ONNX: {e}")
        return False
    
    # Paso 7: Resumen final
    print(f"\n🎉 CONVERSIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    print("📋 RESUMEN:")
    print(f"   ✅ Modelo original: {tf_model_path}")
    print(f"   ✅ Modelo convertido: {onnx_model_path}")
    print(f"   📊 Reducción de tamaño: {reduction:.1f}%")
    print(f"   🚀 Mejora de velocidad: {tf_inference_time/onnx_inference_time:.2f}x")
    print(f"   🌿 Especies soportadas: {len(species_list)}")
    
    print(f"\n💡 PRÓXIMOS PASOS:")
    print(f"   2. ✅ COMPLETADO: Conversión del modelo")
    print(f"   3. ⏳ SIGUIENTE: Actualizar código de Streamlit")
    
    return True

def show_next_steps():
    """Muestra información sobre los próximos pasos"""
    print("\n" + "="*60)
    print("🎯 ESTADO ACTUAL:")
    print("="*60)
    print("1. ✅ COMPLETADO: Instalación de dependencias")
    print("2. ✅ COMPLETADO: Conversión del modelo TensorFlow → ONNX")
    print("3. ⏳ SIGUIENTE: Actualizar código de Streamlit para usar ONNX")
    print("4. ⏸️  PENDIENTE: Actualizar requirements.txt")
    print("5. ⏸️  PENDIENTE: Deploy a Streamlit Cloud")
    
    print("\n💡 ARCHIVOS GENERADOS:")
    print("   - model/plant_classifier.onnx (nuevo modelo)")
    print("   - model/plant_classifier.h5 (modelo original, conservado)")
    print("   - model/species_list.json (sin cambios)")

if __name__ == "__main__":
    print("🚀 MIGRACIÓN A ONNX RUNTIME - PASO 2")
    print("Conversión del modelo TensorFlow → ONNX")
    print()
    
    success = convert_tensorflow_to_onnx()
    
    if success:
        show_next_steps()
        print("\n🟢 PASO 2 COMPLETADO - Confirma que todo funciona antes de continuar")
    else:
        print("\n🔴 PASO 2 FALLÓ - Revisa los errores antes de continuar")
        print("\n💡 Si hay problemas:")
        print("   - Verifica que model/plant_classifier.h5 existe")
        print("   - Verifica que model/species_list.json exists")
        print("   - Asegúrate de tener suficiente memoria (>4GB)")
        print("   - Reinicia Python y vuelve a intentar")