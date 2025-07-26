# debug_firestore.py - SCRIPT PARA DEBUGGEAR CONEXIÓN FIRESTORE

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils.firebase_config import firestore_manager
from config import FIREBASE_CONFIG
import json

def test_firestore_connection():
    """Test completo de conexión y datos de Firestore"""
    
    print("🔥 DEBUGGING CONEXIÓN FIRESTORE")
    print("=" * 60)
    
    # 1. Verificar archivo de credenciales
    print("\n📋 1. VERIFICANDO ARCHIVO DE CREDENCIALES:")
    cred_path = Path(FIREBASE_CONFIG["service_account_path"])
    print(f"   Ruta esperada: {cred_path}")
    print(f"   ¿Existe archivo? {cred_path.exists()}")
    
    if cred_path.exists():
        try:
            with open(cred_path, 'r', encoding='utf-8') as f:
                cred_data = json.load(f)
            print(f"   ✅ Archivo válido JSON")
            print(f"   📊 Project ID en archivo: {cred_data.get('project_id')}")
            print(f"   📊 Project ID en config: {FIREBASE_CONFIG['project_id']}")
            
            if cred_data.get('project_id') != FIREBASE_CONFIG['project_id']:
                print("   ⚠️ WARNING: Project IDs no coinciden!")
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
    else:
        print("   ❌ ARCHIVO NO ENCONTRADO")
        print("   💡 Descarga el archivo desde Firebase Console y colócalo aquí")
        return False
    
    # 2. Intentar inicializar Firestore
    print("\n🔥 2. INICIALIZANDO FIRESTORE:")
    if firestore_manager.initialize_firestore():
        print("   ✅ Firestore inicializado exitosamente")
    else:
        print("   ❌ Error inicializando Firestore")
        return False
    
    # 3. Listar todas las colecciones disponibles
    print("\n📂 3. EXPLORANDO COLECCIONES DISPONIBLES:")
    try:
        collections = firestore_manager.db.collections()
        collection_names = [col.id for col in collections]
        print(f"   📋 Colecciones encontradas: {collection_names}")
        
        # Verificar colección de plantas específicamente
        plantas_collection = FIREBASE_CONFIG["collections"]["plantas"]
        print(f"   🌱 Buscando colección de plantas: '{plantas_collection}'")
        
        if plantas_collection in collection_names:
            print(f"   ✅ Colección '{plantas_collection}' encontrada")
        else:
            print(f"   ❌ Colección '{plantas_collection}' NO encontrada")
            print(f"   💡 Colecciones disponibles: {collection_names}")
            
            # Sugerir colección alternativa
            if collection_names:
                print(f"   💡 ¿Tal vez tu colección se llama '{collection_names[0]}'?")
        
    except Exception as e:
        print(f"   ❌ Error listando colecciones: {e}")
    
    # 4. Explorar estructura de la colección de plantas
    print("\n🌿 4. EXPLORANDO ESTRUCTURA DE DATOS:")
    try:
        plantas_ref = firestore_manager.db.collection(FIREBASE_CONFIG["collections"]["plantas"])
        
        # Obtener primeros 3 documentos para ver estructura
        docs = plantas_ref.limit(3).stream()
        
        print("   📋 Primeros 3 documentos encontrados:")
        doc_count = 0
        for doc in docs:
            doc_count += 1
            data = doc.to_dict()
            
            print(f"\n   📄 Documento {doc_count} (ID: {doc.id}):")
            print(f"      📝 Campos disponibles: {list(data.keys())}")
            
            # Verificar campos importantes
            nombre_cientifico = data.get('nombre_cientifico')
            nombre_comun = data.get('nombre_comun')
            
            print(f"      🏷️ nombre_cientifico: '{nombre_cientifico}'")
            print(f"      🏷️ nombre_comun: '{nombre_comun}'")
            
            # Mostrar toda la estructura del primer documento
            if doc_count == 1:
                print(f"      📊 ESTRUCTURA COMPLETA DEL DOCUMENTO:")
                for key, value in data.items():
                    if isinstance(value, dict):
                        print(f"         {key}: {list(value.keys())} (dict)")
                    else:
                        print(f"         {key}: {str(value)[:50]}...")
        
        if doc_count == 0:
            print("   ❌ NO se encontraron documentos en la colección")
            print("   💡 Verifica que hayas subido datos a Firestore")
        else:
            print(f"   ✅ {doc_count} documentos encontrados")
            
    except Exception as e:
        print(f"   ❌ Error explorando colección: {e}")
    
    # 5. Test de búsqueda específica
    print("\n🔍 5. TESTING BÚSQUEDA ESPECÍFICA:")
    
    # Lista de nombres para probar
    nombres_test = [
        "Agave_americana_L",
        "Agave americana L",
        "Agave americana",
        "Mangifera_indica_L",
        "Aloe_maculata_All"
    ]
    
    for nombre in nombres_test:
        print(f"\n   🔍 Buscando: '{nombre}'")
        try:
            # Búsqueda directa
            plantas_ref = firestore_manager.db.collection(FIREBASE_CONFIG["collections"]["plantas"])
            query = plantas_ref.where('nombre_cientifico', '==', nombre).limit(1)
            docs = list(query.stream())
            
            if docs:
                doc_data = docs[0].to_dict()
                print(f"      ✅ ENCONTRADO: {doc_data.get('nombre_comun', 'Sin nombre común')}")
                print(f"      📝 nombre_cientifico en BD: '{doc_data.get('nombre_cientifico')}'")
            else:
                print(f"      ❌ No encontrado con nombre exacto")
                
                # Búsqueda parcial
                print(f"      🔍 Intentando búsqueda parcial...")
                all_docs = plantas_ref.limit(10).stream()
                found_similar = False
                
                for doc in all_docs:
                    doc_data = doc.to_dict()
                    doc_nombre = doc_data.get('nombre_cientifico', '')
                    
                    if nombre.lower() in doc_nombre.lower() or doc_nombre.lower() in nombre.lower():
                        print(f"      🎯 Nombre similar encontrado: '{doc_nombre}'")
                        found_similar = True
                        break
                
                if not found_similar:
                    print(f"      ❌ No hay nombres similares")
                    
        except Exception as e:
            print(f"      ❌ Error en búsqueda: {e}")
    
    # 6. Test de función de la aplicación
    print("\n🧪 6. TESTING FUNCIÓN DE LA APLICACIÓN:")
    try:
        # Test con la función actual
        info = firestore_manager.obtener_info_especie_basica("Agave_americana_L")
        
        print(f"   📋 Resultado de obtener_info_especie_basica:")
        print(f"      fuente_datos: {info.get('fuente_datos')}")
        print(f"      nombre_comun: {info.get('nombre_comun')}")
        print(f"      descripcion: {info.get('descripcion')[:100]}...")
        
        if info.get('fuente_datos') == 'firestore':
            print("   ✅ DATOS REALES DE FIRESTORE OBTENIDOS")
        else:
            print("   ❌ DATOS SIMULADOS - No se conectó a Firestore")
            
    except Exception as e:
        print(f"   ❌ Error en función de aplicación: {e}")
    
    # 7. Recomendaciones
    print("\n💡 7. RECOMENDACIONES:")
    print("   1. Verifica que el project_id en config.py coincida con Firebase")
    print("   2. Asegúrate de que los datos estén en la colección correcta")
    print("   3. Verifica el formato exacto de 'nombre_cientifico' en tus datos")
    print("   4. Confirma que tienes permisos de lectura en Firestore")
    
    return True

def fix_collection_name():
    """Ayuda a corregir el nombre de la colección si es necesario"""
    print("\n🔧 CORRIGIENDO NOMBRE DE COLECCIÓN:")
    
    try:
        collections = firestore_manager.db.collections()
        collection_names = [col.id for col in collections]
        
        print(f"Colecciones disponibles: {collection_names}")
        print(f"Colección actual en config: {FIREBASE_CONFIG['collections']['plantas']}")
        
        if collection_names:
            print("\n¿Cuál es el nombre correcto de tu colección de plantas?")
            for i, name in enumerate(collection_names):
                print(f"  {i+1}. {name}")
        
    except Exception as e:
        print(f"Error: {e}")

def show_sample_data_structure():
    """Muestra la estructura esperada de los datos"""
    print("\n📋 ESTRUCTURA ESPERADA DE DATOS EN FIRESTORE:")
    print("=" * 50)
    
    estructura_esperada = {
        "nombre_cientifico": "Agave_americana_L",
        "nombre_comun": "Agave Americano", 
        "descripcion": "Descripción de la planta...",
        "fecha_observacion": "2024-01-01",
        "fuente": "Observación directa",
        "imagen_url": "https://ejemplo.com/imagen.jpg",
        "taxonomia": {
            "reino": "Plantae",
            "filo": "Tracheophyta", 
            "clase": "Liliopsida",
            "orden": "Asparagales",
            "familia": "Asparagaceae",
            "genero": "Agave",
            "especie": "americana"
        }
    }
    
    print(json.dumps(estructura_esperada, indent=2, ensure_ascii=False))
    print("\n💡 Cada documento debe tener al menos 'nombre_cientifico' y 'nombre_comun'")

if __name__ == "__main__":
    # Ejecutar test completo
    test_firestore_connection()
    
    # Mostrar estructura esperada
    show_sample_data_structure()
    
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Ejecuta este script: python debug_firestore.py")
    print("2. Revisa los resultados para identificar el problema")
    print("3. Ajusta la configuración según los hallazgos")
    print("4. Si necesitas help, comparte la salida de este script")