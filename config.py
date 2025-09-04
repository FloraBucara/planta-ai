import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PLANTAS_DIR = DATA_DIR / "plantas"
MODEL_DIR = PROJECT_ROOT / "model"
UTILS_DIR = PROJECT_ROOT / "utils"
LOGS_DIR = PROJECT_ROOT / "logs"

MODEL_CONFIG = {
    "input_shape": (224, 224, 3),
    "target_size": (224, 224),
    "batch_size": 32,
    "epochs": 50,
    "learning_rate": 0.0001,
    "validation_split": 0.2,
    "model_name": "plant_classifier.onnx",
    "backup_model_name": "plant_classifier_backup.onnx",
    "species_list_name": "species_list.json",
    "base_model": "MobileNetV2",
    "freeze_base": True,
    "fine_tune_layers": 20,
    "image_quality": 85
}


FIREBASE_CONFIG = {
    "project_id": "bucaraflora-f0161",
    "service_account_path": "proyecto-firebase-key.json",
    "database_type": "firestore",
    "collections": {
        "plantas": "planta",
        "analisis_usuarios": "analisis_usuarios",
        "estadisticas_sistema": "estadisticas_sistema", 
        "logs_entrenamientos": "logs_entrenamientos",
        "sesiones_usuarios": "sesiones_usuarios",
        "metricas_modelo": "metricas_modelo"
    },
    "plantas_schema": {
        "id_field": "nombre_cientifico",
        "required_fields": [
            "nombre_cientifico",
            "nombre_comun", 
            "descripcion",
            "cuidados",
            "imagen_url",
            "taxonomia"
        ],
        "taxonomia_fields": [
            "clase", "especie", "familia", 
            "filo", "genero", "orden", "reino"
        ]
    }
}

API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False,
    "save_image_endpoint": "/api/save_image",
    "get_stats_endpoint": "/api/stats",
    "retrain_endpoint": "/api/retrain",
    "training_status_endpoint": "/api/training_status",
    "admin_key": "bucaraflora_admin_2025_secret_key"
}

NGROK_CONFIG = {
    "auth_token": "tu_ngrok_auth_token_aqui",
    "region": "us",
    "subdomain": None
}

STREAMLIT_CONFIG = {
    "page_title": "🌱 BucaraFlora - Identificador de Plantas IA",
    "page_icon": "🌱",
    "layout": "centered",
    "initial_sidebar_state": "collapsed",
    "max_file_size": 10,
    "allowed_extensions": ["jpg", "jpeg", "png"],
    "image_quality": 85
}

SYSTEM_STATES = {
    "training_idle": "idle",
    "training_in_progress": "training",
    "training_completed": "completed",
    "training_failed": "failed",
    "training_validating": "validating"
}

PATHS = {
    "model_file": MODEL_DIR / MODEL_CONFIG["model_name"],
    "backup_model_file": MODEL_DIR / MODEL_CONFIG["backup_model_name"],
    "species_list_file": MODEL_DIR / MODEL_CONFIG["species_list_name"],
    "training_log_file": LOGS_DIR / "training_logs.txt",
    "session_data_file": DATA_DIR / "sessions.json",
    "system_log_file": LOGS_DIR / "system.log"
}

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

MESSAGES = {
    "prediction_success": "🎉 ¡Identificación exitosa!",
    "prediction_failed": "🤔 No pudimos identificar tu planta con certeza.",
    "image_saved": "✅ Imagen guardada para mejorar el modelo.",
    "training_started": "🚀 Re-entrenamiento iniciado en segundo plano.",
    "training_completed": "✅ Modelo actualizado exitosamente.",
    "training_failed": "❌ Error en el re-entrenamiento.",
    "insufficient_images": "⏰ Esperando más imágenes para re-entrenar.",
    "new_photo_suggestion": "💡 Intenta con otra foto desde un ángulo diferente."
}

def create_directories():
    """Crea los directorios necesarios si no existen"""
    directories = [DATA_DIR, MODEL_DIR, LOGS_DIR]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        
    if not PLANTAS_DIR.exists():
        print(f"ADVERTENCIA: No se encontro el directorio de plantas en {PLANTAS_DIR}")
        print("   Asegúrate de colocar tu carpeta 'plantas' en data/plantas/")
    else:
        especies_count = len([d for d in PLANTAS_DIR.iterdir() if d.is_dir()])
        print(f"Directorio de plantas encontrado: {especies_count} especies")

def validate_config():
    """Valida que la configuración sea correcta"""
    errors = []
    
    if not PLANTAS_DIR.exists():
        errors.append(f"Directorio de plantas no encontrado: {PLANTAS_DIR}")
    
    if MODEL_CONFIG["input_shape"][0] != MODEL_CONFIG["input_shape"][1]:
        errors.append("Las dimensiones de entrada del modelo deben ser cuadradas")
    
    
    firebase_path = Path(FIREBASE_CONFIG["service_account_path"])
    if not firebase_path.exists():
        errors.append(f"Archivo de credenciales Firebase no encontrado: {firebase_path}")
    
    return errors

def get_project_info():
    """Retorna información básica del proyecto"""
    return {
        "project_root": str(PROJECT_ROOT),
        "plantas_dir": str(PLANTAS_DIR),
        "model_dir": str(MODEL_DIR),
        "logs_dir": str(LOGS_DIR),
        "firebase_type": FIREBASE_CONFIG["database_type"],
        "firebase_project": FIREBASE_CONFIG["project_id"],
        "config_valid": len(validate_config()) == 0
    }

create_directories()

config_errors = validate_config()
if config_errors:
    print("Errores en la configuracion:")
    for error in config_errors:
        print(f"   - {error}")
else:
    print("Configuracion validada correctamente")

info = get_project_info()
print(f"Proyecto BucaraFlora inicializado en: {info['project_root']}")
print(f"Directorio de plantas: {info['plantas_dir']}")
print(f"Firebase Firestore: {info['firebase_project']}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("CONFIGURACIÓN DEL PROYECTO BUCARAFLORA")
    print("="*50)
    
    print(f"\nESTADISTICAS:")
    if PLANTAS_DIR.exists():
        especies = [d for d in PLANTAS_DIR.iterdir() if d.is_dir()]
        total_imagenes = sum(len([f for f in especie.iterdir() 
                                if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]) 
                           for especie in especies)
        print(f"   - Especies locales: {len(especies)}")
        print(f"   - Total imágenes locales: {total_imagenes}")
        print(f"   - Promedio por especie: {total_imagenes/len(especies):.1f}")
    
    print(f"\nCONFIGURACION FIREBASE:")
    print(f"   - Tipo: {FIREBASE_CONFIG['database_type']}")
    print(f"   - Proyecto: {FIREBASE_CONFIG['project_id']}")
    print(f"   - Colección plantas: {FIREBASE_CONFIG['collections']['plantas']}")
    print(f"   - Campo ID: {FIREBASE_CONFIG['plantas_schema']['id_field']}")
    
    print(f"\nCONFIGURACION DEL MODELO:")
    print(f"   - Tamaño entrada: {MODEL_CONFIG['input_shape']}")
    print(f"   - Épocas: {MODEL_CONFIG['epochs']}")
    print(f"   - Batch size: {MODEL_CONFIG['batch_size']}")
    
