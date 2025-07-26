# diagnostico_firestore.py - Script para diagnosticar problemas con Firestore

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent))

def test_firestore_connection():
    """Test completo de conexión y datos de Firestore"""
    print("🔥 DIAGNÓSTICO COMPLETO DE FIRESTORE")
    print("=" * 60)
    
    # Test 1: Importar módulos
    print("\n1️⃣ TESTING IMPORTS...")
    try:
        from utils.firebase_config import firestore_manager, obtener_info_planta
        from config import FIREBASE_CONFIG
        print("✅ Imports correctos")
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False
    
    # Test 2: Inicializar Firestore
    print("\n2️⃣ TESTING INICIALIZACIÓN...")
    try:
        if firestore_manager.initialize_firestore():
            print("✅ Firestore inicializado")
        else:
            print("❌ Error inicializando Firestore")
            return False
    except Exception as e:
        print(f"❌ Excepción en inicialización: {e}")
        return False
    
    # Test 3: Verificar configuración
    print("\n3️⃣ TESTING CONFIGURACIÓN...")
    print(f"📊 Proyecto ID: {FIREBASE_CONFIG['project_id']}")
    print(f"📋 Colección plantas: {FIREBASE_CONFIG['collections']['plantas']}")
    print(f"🔑 Campo ID: {FIREBASE_CONFIG['plantas_schema']['id_field']}")
    
    # Test 4: Listar documentos en la colección
    print("\n4️⃣ TESTING ACCESO A COLECCIÓN...")
    try:
        collection_name = FIREBASE_CONFIG['collections']['plantas']
        print(f"🔍 Buscando en colección: '{collection_name}'")
        
        # Acceso directo a Firestore
        db = firestore_manager.db
        plantas_ref = db.collection(collection_name)
        
        # Obtener primeros 5 documentos
        docs = plantas_ref.limit(5).stream()
        documentos_encontrados = []
        
        for doc in docs:
            data = doc.to_dict()
            documentos_encontrados.append({
                'id': doc.id,
                'nombre_cientifico': data.get('nombre_cientifico', 'NO_ENCONTRADO'),
                'nombre_comun': data.get('nombre_comun', 'NO_ENCONTRADO'),
                'tiene_descripcion': 'descripcion' in data,
                'tiene_taxonomia': 'taxonomia' in data,
                'campos_disponibles': list(data.keys())
            })
        
        print(f"📋 Documentos encontrados: {len(documentos_encontrados)}")
        
        if documentos_encontrados:
            print("\n📝 PRIMER DOCUMENTO ENCONTRADO:")
            primer_doc = documentos_encontrados[0]
            for key, value in primer_doc.items():
                print(f"   {key}: {value}")
        else:
            print("❌ NO SE ENCONTRARON DOCUMENTOS en la colección")
            return False
            
    except Exception as e:
        print(f"❌ Error accediendo a colección: {e}")
        return False
    
    # Test 5: Buscar especie específica
    print("\n5️⃣ TESTING BÚSQUEDA POR NOMBRE CIENTÍFICO...")
    try:
        # Usar el primer nombre científico encontrado
        if documentos_encontrados:
            test_especie = documentos_encontrados[0]['nombre_cientifico']
            print(f"🔍 Buscando especie: '{test_especie}'")
            
            # Buscar con la función del sistema
            info = obtener_info_planta(test_especie)
            print(f"📋 Resultado de búsqueda:")
            print(f"   Nombre científico: {info.get('nombre_cientifico', 'NO_ENCONTRADO')}")
            print(f"   Nombre común: {info.get('nombre_comun', 'NO_ENCONTRADO')}")
            print(f"   Descripción: {info.get('descripcion', 'NO_ENCONTRADO')[:100]}...")
            print(f"   Fuente datos: {info.get('fuente_datos', 'NO_ENCONTRADO')}")
            print(f"   Tiene taxonomía: {'taxonomia' in info}")
            
            if info.get('fuente_datos') == 'firestore':
                print("✅ Datos obtenidos desde Firestore")
            else:
                print("⚠️ Datos simulados - No se encontró en Firestore")
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    # Test 6: Probar especies del modelo
    print("\n6️⃣ TESTING ESPECIES DEL MODELO...")
    try:
        from model.model_utils import ModelUtils
        model_utils = ModelUtils()
        
        if model_utils.cargar_modelo():
            print(f"📊 Especies en el modelo: {len(model_utils.species_names)}")
            
            # Probar las primeras 3 especies del modelo
            especies_test = model_utils.species_names[:3]
            print(f"🔍 Testing primeras 3 especies del modelo:")
            
            for especie in especies_test:
                print(f"\n   🌱 Testing: {especie}")
                info = obtener_info_planta(especie)
                
                es_firestore = info.get('fuente_datos') == 'firestore'
                tiene_descripcion = bool(info.get('descripcion', '').strip())
                tiene_taxonomia = bool(info.get('taxonomia', {}))
                
                print(f"      Firestore: {'✅' if es_firestore else '❌'}")
                print(f"      Descripción: {'✅' if tiene_descripcion else '❌'}")
                print(f"      Taxonomía: {'✅' if tiene_taxonomia else '❌'}")
                
        else:
            print("❌ No se pudo cargar el modelo")
            
    except Exception as e:
        print(f"❌ Error testing especies del modelo: {e}")
    
    # Test 7: Verificar estructura esperada vs real
    print("\n7️⃣ TESTING ESTRUCTURA DE DATOS...")
    if documentos_encontrados:
        primer_doc_id = documentos_encontrados[0]['id']
        print(f"🔍 Analizando estructura del documento: {primer_doc_id}")
        
        try:
            doc_ref = db.collection(collection_name).document(primer_doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                print(f"\n📋 ESTRUCTURA COMPLETA DEL DOCUMENTO:")
                print_structure(data, "   ")
            else:
                print("❌ Documento no existe")
                
        except Exception as e:
            print(f"❌ Error analizando estructura: {e}")
    
    print(f"\n🏁 DIAGNÓSTICO COMPLETADO")
    return True

def print_structure(data, indent=""):
    """Imprime la estructura de un diccionario de forma legible"""
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{indent}{key}: {{")
            print_structure(value, indent + "   ")
            print(f"{indent}}}")
        elif isinstance(value, list):
            print(f"{indent}{key}: [lista con {len(value)} elementos]")
        else:
            value_str = str(value)[:50] + ("..." if len(str(value)) > 50 else "")
            print(f"{indent}{key}: {value_str}")

if __name__ == "__main__":
    test_firestore_connection()