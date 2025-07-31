# utils/firebase_streamlit.py - FIREBASE OPTIMIZADO PARA STREAMLIT
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from pathlib import Path
import sys

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))
from config import FIREBASE_CONFIG

@st.cache_resource
def initialize_firebase():
    """Inicializa Firebase una sola vez para toda la aplicación Streamlit"""
    try:
        # Verificar si ya está inicializado
        if firebase_admin._apps:
            print("🔥 Firebase ya inicializado")
            return firestore.client()
        
        # Ruta del archivo de credenciales
        cred_path = Path(FIREBASE_CONFIG["service_account_path"])
        
        if not cred_path.exists():
            print(f"❌ Archivo de credenciales no encontrado: {cred_path}")
            return None
        
        # Inicializar Firebase
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_CONFIG["project_id"]
        })
        
        db = firestore.client()
        print("✅ Firebase inicializado exitosamente para Streamlit")
        return db
        
    except Exception as e:
        print(f"❌ Error inicializando Firebase: {e}")
        return None

@st.cache_data(ttl=600)  # Cache por 10 minutos
def get_plant_from_firestore(species_name):
    """Obtiene información de planta desde Firestore con cache"""
    try:
        # Obtener conexión
        db = initialize_firebase()
        
        if not db:
            return None
        
        # Buscar en la colección 'planta'
        collection_name = FIREBASE_CONFIG["collections"]["plantas"]
        plantas_ref = db.collection(collection_name)
        
        # Normalizar nombre para búsqueda
        search_variations = [
            species_name,
            species_name.replace('_', ' '),
            species_name.replace('_', ' ') + '.',
            species_name.replace('_', ' ').replace('(', ' (').replace(')', ') ')
        ]
        
        # Probar cada variación
        for variation in search_variations:
            query = plantas_ref.where('nombre_cientifico', '==', variation).limit(1)
            docs = list(query.stream())
            
            if docs:
                doc_data = docs[0].to_dict()
                print(f"✅ Encontrado en Firestore: {variation}")
                
                return {
                    "found": True,
                    "nombre_comun": doc_data.get('nombre_comun', 'Nombre no disponible'),
                    "nombre_cientifico": doc_data.get('nombre_cientifico', species_name),
                    "descripcion": doc_data.get('descripcion', 'Descripción no disponible'),
                    "familia": doc_data.get('taxonomia', {}).get('familia', '') if isinstance(doc_data.get('taxonomia'), dict) else '',
                    "origen": doc_data.get('fecha_observacion', ''),
                    "fuente": doc_data.get('fuente', ''),
                    "imagenes": doc_data.get('imagenes', []),
                    "taxonomia": doc_data.get('taxonomia', {}) if isinstance(doc_data.get('taxonomia'), dict) else {},
                    "fuente_datos": "Firebase Firestore"
                }
        
        # No encontrado
        print(f"❌ No encontrado en Firestore: {species_name}")
        return None
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de Firestore: {e}")
        return None

def get_plant_info_complete(species_name):
    """Función principal para obtener información completa de planta"""
    try:
        # Intentar obtener desde Firestore
        firestore_data = get_plant_from_firestore(species_name)
        
        if firestore_data and firestore_data.get("found"):
            return firestore_data
        
        # Fallback: información básica
        return {
            "found": False,
            "nombre_comun": "Especie identificada",
            "nombre_cientifico": species_name,
            "descripcion": "Esta especie está en nuestra base de datos de 335 plantas colombianas.",
            "familia": "",
            "origen": "",
            "fuente": "",
            "imagenes": [],
            "taxonomia": {},
            "fuente_datos": "Base de datos local"
        }
        
    except Exception as e:
        print(f"❌ Error en get_plant_info_complete: {e}")
        return {
            "found": False,
            "nombre_comun": "Error al cargar información",
            "nombre_cientifico": species_name,
            "descripcion": f"Error conectando con la base de datos: {str(e)}",
            "familia": "",
            "origen": "",
            "fuente": "",
            "imagenes": [],
            "taxonomia": {},
            "fuente_datos": "Error"
        }

def test_firebase_connection():
    """Función para probar la conexión desde Streamlit"""
    try:
        db = initialize_firebase()
        
        if not db:
            return {"success": False, "error": "No se pudo inicializar Firebase"}
        
        # Test con una especie conocida
        test_result = get_plant_from_firestore("Agave_americana_L")
        
        if test_result and test_result.get("found"):
            return {
                "success": True, 
                "message": "Conexión exitosa",
                "test_species": test_result["nombre_comun"]
            }
        else:
            return {
                "success": False, 
                "error": "Conexión establecida pero no se encontraron datos"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Test para verificar que funciona
if __name__ == "__main__":
    print("🧪 Testing Firebase para Streamlit...")
    result = test_firebase_connection()
    print(f"Resultado: {result}")