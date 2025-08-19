# config.py - CONFIGURACIÓN FIREBASE ACTUALIZADA PARA FIRESTORE

import os
from pathlib import Path

# ==================== RUTAS DEL PROYECTO ====================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PLANTAS_DIR = DATA_DIR / "plantas"
MODEL_DIR = PROJECT_ROOT / "model"
UTILS_DIR = PROJECT_ROOT / "utils"
LOGS_DIR = PROJECT_ROOT / "logs"

# ==================== CONFIGURACIÓN DEL MODELO ====================
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

# ==================== CONFIGURACIÓN DE RE-ENTRENAMIENTO ====================
RETRAINING_CONFIG = {
    "min_images_total": 30,
    "min_species_with_new_images": 10,
    "min_images_per_species": 3,
    "weekly_schedule_day": "sunday",
    "weekly_schedule_time": "01:00",
    "max_attempts_per_prediction": 3,
    "top_species_to_show": 6,
    "min_accuracy_to_replace": 0.80,
    "accuracy_improvement_threshold": 0.95
}

# ==================== CONFIGURACIÓN DE FIREBASE FIRESTORE ====================
FIREBASE_CONFIG = {
    # CONFIGURACIÓN ACTUALIZADA PARA FIRESTORE
    "project_id": "bucaraflora-f0161",
    "service_account_path": "bucaraflora-f0161-firebase-adminsdk-fbsvc-be20c93d27.json",
    "database_type": "firestore",  # ← FIRESTORE, no Realtime Database
    
    # COLECCIONES DE FIRESTORE
    "collections": {
        # Colección principal de plantas (tu estructura existente)
        "plantas": "planta",
        
        # Colecciones para el sistema de análisis
        "analisis_usuarios": "analisis_usuarios",
        "estadisticas_sistema": "estadisticas_sistema", 
        "logs_entrenamientos": "logs_entrenamientos",
        "sesiones_usuarios": "sesiones_usuarios",
        "metricas_modelo": "metricas_modelo"
    },
    
    # CAMPOS DE LA COLECCIÓN PLANTAS
    "plantas_schema": {
        "id_field": "nombre_cientifico",  # ← Campo identificador
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

# ==================== CONFIGURACIÓN DE LA API (NGROK) ====================
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

# ==================== CONFIGURACIÓN DE NGROK ====================
NGROK_CONFIG = {
    "auth_token": "tu_ngrok_auth_token_aqui",  # ← ACTUALIZA CON TU TOKEN REAL
    "region": "us",
    "subdomain": None
}

# ==================== CONFIGURACIÓN DE STREAMLIT ====================
STREAMLIT_CONFIG = {
    "page_title": "🌱 BucaraFlora - Identificador de Plantas IA",
    "page_icon": "🌱",
    "layout": "centered",
    "initial_sidebar_state": "collapsed",
    "max_file_size": 10,
    "allowed_extensions": ["jpg", "jpeg", "png"],
    "image_quality": 85
}

# ==================== ESTADOS DEL SISTEMA ====================
SYSTEM_STATES = {
    "training_idle": "idle",
    "training_in_progress": "training",
    "training_completed": "completed",
    "training_failed": "failed",
    "training_validating": "validating"
}

# ==================== RUTAS DE ARCHIVOS IMPORTANTES ====================
PATHS = {
    "model_file": MODEL_DIR / MODEL_CONFIG["model_name"],
    "backup_model_file": MODEL_DIR / MODEL_CONFIG["backup_model_name"],
    "species_list_file": MODEL_DIR / MODEL_CONFIG["species_list_name"],
    "training_log_file": LOGS_DIR / "training_logs.txt",
    "session_data_file": DATA_DIR / "sessions.json",
    "system_log_file": LOGS_DIR / "system.log"
}

# ==================== CONFIGURACIÓN DE LOGGING ====================
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# ==================== MENSAJES DE LA APLICACIÓN ====================
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

# ==================== VALIDACIONES Y FUNCIONES AUXILIARES ====================

def create_directories():
    """Crea los directorios necesarios si no existen"""
    directories = [DATA_DIR, MODEL_DIR, LOGS_DIR]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        
    if not PLANTAS_DIR.exists():
        print(f"⚠️ ADVERTENCIA: No se encontró el directorio de plantas en {PLANTAS_DIR}")
        print("   Asegúrate de colocar tu carpeta 'plantas' en data/plantas/")
    else:
        especies_count = len([d for d in PLANTAS_DIR.iterdir() if d.is_dir()])
        print(f"✅ Directorio de plantas encontrado: {especies_count} especies")

def validate_config():
    """Valida que la configuración sea correcta"""
    errors = []
    
    if not PLANTAS_DIR.exists():
        errors.append(f"Directorio de plantas no encontrado: {PLANTAS_DIR}")
    
    if MODEL_CONFIG["input_shape"][0] != MODEL_CONFIG["input_shape"][1]:
        errors.append("Las dimensiones de entrada del modelo deben ser cuadradas")
    
    if RETRAINING_CONFIG["min_images_total"] < 10:
        errors.append("min_images_total debería ser al menos 10")
    
    # Verificar archivo de Firebase
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

# ==================== INICIALIZACIÓN ====================

create_directories()

config_errors = validate_config()
if config_errors:
    print("❌ Errores en la configuración:")
    for error in config_errors:
        print(f"   - {error}")
else:
    print("✅ Configuración validada correctamente")

info = get_project_info()
print(f"📁 Proyecto BucaraFlora inicializado en: {info['project_root']}")
print(f"🌱 Directorio de plantas: {info['plantas_dir']}")
print(f"🔥 Firebase Firestore: {info['firebase_project']}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("CONFIGURACIÓN DEL PROYECTO BUCARAFLORA")
    print("="*50)
    
    print(f"\n📊 ESTADÍSTICAS:")
    if PLANTAS_DIR.exists():
        especies = [d for d in PLANTAS_DIR.iterdir() if d.is_dir()]
        total_imagenes = sum(len([f for f in especie.iterdir() 
                                if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]) 
                           for especie in especies)
        print(f"   - Especies locales: {len(especies)}")
        print(f"   - Total imágenes locales: {total_imagenes}")
        print(f"   - Promedio por especie: {total_imagenes/len(especies):.1f}")
    
    print(f"\n🔥 CONFIGURACIÓN FIREBASE:")
    print(f"   - Tipo: {FIREBASE_CONFIG['database_type']}")
    print(f"   - Proyecto: {FIREBASE_CONFIG['project_id']}")
    print(f"   - Colección plantas: {FIREBASE_CONFIG['collections']['plantas']}")
    print(f"   - Campo ID: {FIREBASE_CONFIG['plantas_schema']['id_field']}")
    
    print(f"\n🤖 CONFIGURACIÓN DEL MODELO:")
    print(f"   - Tamaño entrada: {MODEL_CONFIG['input_shape']}")
    print(f"   - Épocas: {MODEL_CONFIG['epochs']}")
    print(f"   - Batch size: {MODEL_CONFIG['batch_size']}")
    
    print(f"\n🔄 CONFIGURACIÓN RE-ENTRENAMIENTO:")
    print(f"   - Mínimo imágenes: {RETRAINING_CONFIG['min_images_total']}")
    print(f"   - Día programado: {RETRAINING_CONFIG['weekly_schedule_day']}")
    print(f"   - Hora programada: {RETRAINING_CONFIG['weekly_schedule_time']}")