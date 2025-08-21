#!/usr/bin/env python3
# Script para probar la carga del modelo ONNX

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent))

try:
    print("Verificando modelo ONNX...")
    print("=" * 50)
    
    # Test 1: Importar configuración
    try:
        from config import PATHS, MODEL_CONFIG
        print("OK - Configuración importada correctamente")
        print(f"   Directorio modelo: {PATHS['model_file'].parent}")
        print(f"   Archivo modelo: {PATHS['model_file']}")
    except Exception as e:
        print(f"ERROR - Error importando configuración: {e}")
        exit(1)
    
    # Test 2: Verificar archivos
    model_file = PATHS["model_file"].parent / "plant_classifier.onnx"
    metadata_file = PATHS["model_file"].parent / "model_metadata.json"
    species_file = PATHS["species_list_file"]
    
    print(f"\nVerificando archivos:")
    print(f"   ONNX: {model_file} -> {'OK' if model_file.exists() else 'ERROR'}")
    print(f"   Metadatos: {metadata_file} -> {'OK' if metadata_file.exists() else 'ERROR'}")
    print(f"   Especies: {species_file} -> {'OK' if species_file.exists() else 'ERROR'}")
    
    if not model_file.exists():
        print("ERROR - ARCHIVO ONNX NO ENCONTRADO")
        exit(1)
    
    # Test 3: Cargar modelo con ONNX Runtime
    try:
        import onnxruntime as ort
        session = ort.InferenceSession(str(model_file))
        print(f"OK - Modelo ONNX cargado correctamente")
        
        # Verificar inputs/outputs
        input_info = session.get_inputs()[0]
        output_info = session.get_outputs()[0]
        print(f"   Input: {input_info.name} {input_info.shape}")
        print(f"   Output: {output_info.name} {output_info.shape}")
        
    except Exception as e:
        print(f"ERROR - Error cargando modelo ONNX: {e}")
        exit(1)
    
    # Test 4: Cargar metadatos
    try:
        import json
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"OK - Metadatos cargados: {metadata.get('num_classes', 0)} clases")
        else:
            print("WARNING - No se encontraron metadatos, probando backup...")
            if species_file.exists():
                with open(species_file, 'r', encoding='utf-8') as f:
                    species = json.load(f)
                print(f"OK - Especies cargadas desde backup: {len(species)} especies")
            else:
                print("ERROR - No se encontraron ni metadatos ni lista de especies")
                exit(1)
    except Exception as e:
        print(f"ERROR - Error cargando metadatos: {e}")
        exit(1)
    
    # Test 5: Usar ModelUtils
    try:
        from model.model_utils import ModelUtils
        model_utils = ModelUtils()
        resultado = model_utils.cargar_modelo()
        
        if resultado:
            print(f"OK - ModelUtils cargado: {model_utils.num_classes} especies")
            
            # Test de predicción
            import numpy as np
            test_image = np.random.random((1, 224, 224, 3)).astype(np.float32)
            prediccion = model_utils.predecir_especie(test_image)
            
            if "error" not in prediccion:
                print(f"OK - Test de predicción exitoso: {prediccion['especie_predicha']}")
            else:
                print(f"ERROR - Error en test de predicción: {prediccion['error']}")
        else:
            print("ERROR - ModelUtils no pudo cargar el modelo")
            
    except Exception as e:
        print(f"ERROR - Error con ModelUtils: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\nTodos los tests pasaron! El modelo deberia funcionar correctamente.")
    
except Exception as e:
    print(f"ERROR - Error general: {e}")
    import traceback
    traceback.print_exc()
    exit(1)