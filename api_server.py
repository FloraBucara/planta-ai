from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
import io
import threading
from datetime import datetime, timedelta
from PIL import Image
import schedule
import time
import sys
from pathlib import Path
import mimetypes
import json

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent))

from config import API_CONFIG, RETRAINING_CONFIG, SYSTEM_STATES, PLANTAS_DIR, PATHS
from utils.image_processing import DatasetManager, obtener_estadisticas_dataset
from utils.session_manager import session_manager, obtener_estadisticas_sesiones

# Estado global del sistema
sistema_estado = {
    "entrenamiento": SYSTEM_STATES["training_idle"],
    "ultimo_entrenamiento": None,
    "ngrok_url": None,
    "servidor_iniciado": datetime.now().isoformat()
}

app = Flask(__name__)
CORS(app)  # Permitir CORS para Streamlit

# Gestores
dataset_manager = DatasetManager()

@app.route('/', methods=['GET'])
def home():
    """Endpoint básico para verificar que la API funciona"""
    return jsonify({
        "status": "activo",
        "mensaje": "🌱 API de Gestión de Plantas funcionando",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "ngrok_url": sistema_estado.get("ngrok_url"),
        "endpoints": {
            "guardar_imagen": "/api/save_image",
            "estadisticas": "/api/stats",
            "estado_entrenamiento": "/api/training_status", 
            "forzar_entrenamiento": "/api/retrain",
            "estadisticas_sesiones": "/api/session_stats",
            "imagen_referencia": "/api/reference_image/<especie_name>",
            "verificar_imagen": "/api/check_reference_image/<especie_name>"
        }
    })

@app.route('/api/reference_image/<especie_name>')
def get_reference_image(especie_name):
    """
    Sirve imagen de referencia para una especie específica
    - Solo especies válidas del modelo
    - Solo la primera imagen de cada especie
    - Acceso muy controlado y seguro
    """
    try:
        # 1. Validar que la especie existe en nuestro modelo
        if not verificar_especie_valida(especie_name):
            return jsonify({
                "error": "Especie no encontrada",
                "mensaje": f"La especie '{especie_name}' no está en el modelo"
            }), 404
        
        # 2. Verificar que existe la carpeta de la especie
        carpeta_especie = PLANTAS_DIR / especie_name
        if not carpeta_especie.exists() or not carpeta_especie.is_dir():
            return jsonify({
                "error": "Carpeta de especie no encontrada",
                "mensaje": f"No se encontró carpeta para '{especie_name}'"
            }), 404
        
        # 3. Buscar imágenes en la carpeta (solo extensiones permitidas)
        extensiones_permitidas = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
        imagenes = [
            f for f in carpeta_especie.iterdir() 
            if f.is_file() and f.suffix in extensiones_permitidas
        ]
        
        if not imagenes:
            return jsonify({
                "error": "No hay imágenes disponibles",
                "mensaje": f"No se encontraron imágenes para '{especie_name}'"
            }), 404
        
        # 4. Seleccionar la primera imagen (ordenadas alfabéticamente)
        imagenes_ordenadas = sorted(imagenes)
        imagen_referencia = imagenes_ordenadas[0]
        
        # 5. Verificar que el archivo existe y es accesible
        if not imagen_referencia.exists():
            return jsonify({
                "error": "Archivo no accesible",
                "mensaje": "La imagen de referencia no está disponible"
            }), 404
        
        # 6. Determinar tipo MIME
        mimetype, _ = mimetypes.guess_type(str(imagen_referencia))
        if not mimetype or not mimetype.startswith('image/'):
            mimetype = 'image/jpeg'  # Fallback seguro
        
        # 7. Log del acceso (para seguridad)
        print(f"📷 Sirviendo imagen de referencia: {especie_name} -> {imagen_referencia.name}")
        
        # 8. Servir archivo con headers de caché
        response = send_file(
            imagen_referencia, 
            mimetype=mimetype,
            as_attachment=False,
            download_name=f"{especie_name}_referencia{imagen_referencia.suffix}"
        )
        
        # Headers de caché (24 horas)
        response.headers['Cache-Control'] = 'public, max-age=86400'
        response.headers['X-Served-Species'] = especie_name
        
        return response
        
    except Exception as e:
        print(f"❌ Error sirviendo imagen de {especie_name}: {e}")
        return jsonify({
            "error": "Error interno del servidor",
            "mensaje": "No se pudo cargar la imagen de referencia"
        }), 500

@app.route('/api/check_reference_image/<especie_name>')
def check_reference_image(especie_name):
    """
    Verifica si existe imagen de referencia para una especie
    (Sin descargar la imagen)
    """
    try:
        if not verificar_especie_valida(especie_name):
            return jsonify({
                "disponible": False,
                "razon": "Especie no válida"
            })
        
        carpeta_especie = PLANTAS_DIR / especie_name
        if not carpeta_especie.exists():
            return jsonify({
                "disponible": False,
                "razon": "Carpeta no encontrada"
            })
        
        extensiones_permitidas = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
        imagenes = [
            f for f in carpeta_especie.iterdir() 
            if f.is_file() and f.suffix in extensiones_permitidas
        ]
        
        if imagenes:
            imagen_referencia = sorted(imagenes)[0]
            return jsonify({
                "disponible": True,
                "nombre_archivo": imagen_referencia.name,
                "url": f"/api/reference_image/{especie_name}"
            })
        else:
            return jsonify({
                "disponible": False,
                "razon": "No hay imágenes"
            })
            
    except Exception as e:
        return jsonify({
            "disponible": False,
            "razon": f"Error: {str(e)}"
        })

def verificar_especie_valida(especie_name):
    """
    Verifica que la especie esté en nuestro modelo entrenado
    """
    try:
        # Cargar lista de especies del modelo
        species_file = PATHS["species_list_file"]
        if species_file.exists():
            with open(species_file, 'r', encoding='utf-8') as f:
                species_list = json.load(f)
            return especie_name in species_list
        
        # Fallback: verificar con model_utils
        from model.model_utils import ModelUtils
        model_utils = ModelUtils()
        if model_utils.cargar_modelo():
            return especie_name in (model_utils.species_names or [])
        
        return False
        
    except Exception as e:
        print(f"❌ Error verificando especie {especie_name}: {e}")
        return False

@app.route('/api/save_image', methods=['POST'])
def guardar_imagen_validada():
    """
    Guarda una imagen validada por el usuario
    
    Expected JSON:
    {
        "image_data": "base64_encoded_image",
        "especie": "nombre_especie",
        "session_id": "session_id",
        "correcto": true/false,
        "metodo": "prediccion" o "seleccion_manual"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        # Validar datos requeridos
        required_fields = ["image_data", "especie", "session_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400
        
        # Decodificar imagen de base64
        try:
            image_data = data["image_data"]
            # Remover prefijo data:image si existe
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decodificar base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
        except Exception as e:
            return jsonify({"error": f"Error decodificando imagen: {str(e)}"}), 400
        
        # Obtener parámetros
        especie = data["especie"]
        session_id = data["session_id"]
        correcto = data.get("correcto", True)
        metodo = data.get("metodo", "prediccion")
        
        # Guardar imagen
        resultado = dataset_manager.guardar_imagen_validada(
            imagen=image,
            nombre_especie=especie,
            session_id=session_id,
            correcto=correcto
        )
        
        if resultado["status"] == "guardada":
            # Actualizar estadísticas
            nuevas_total, especies_nuevas, _ = dataset_manager.contar_imagenes_nuevas()
            
            # Verificar si es momento de reentrenar
            necesidad_retrain = verificar_necesidad_reentrenamiento()
            
            response = {
                "status": "exitoso",
                "mensaje": "Imagen guardada correctamente",
                "archivo": resultado["archivo"],
                "especie": especie,
                "session_id": session_id,
                "estadisticas": {
                    "total_nuevas": nuevas_total,
                    "especies_afectadas": especies_nuevas
                },
                "reentrenamiento": {
                    "necesario": necesidad_retrain["necesita_reentrenamiento"],
                    "criterios": necesidad_retrain["criterios"]
                }
            }
            
            return jsonify(response), 200
        else:
            return jsonify({
                "status": "error",
                "mensaje": "Error guardando imagen",
                "error": resultado.get("mensaje", "Error desconocido")
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "mensaje": "Error interno del servidor",
            "error": str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas del dataset y sistema"""
    try:
        # Estadísticas del dataset
        stats_dataset = obtener_estadisticas_dataset()
        
        # Estadísticas de sesiones
        stats_sesiones = obtener_estadisticas_sesiones()
        
        # Verificar necesidad de reentrenamiento
        necesidad_retrain = verificar_necesidad_reentrenamiento()
        
        # Estado del sistema
        estado_sistema = {
            "estado_entrenamiento": sistema_estado["entrenamiento"],
            "ultimo_entrenamiento": sistema_estado.get("ultimo_entrenamiento"),
            "servidor_iniciado": sistema_estado["servidor_iniciado"],
            "ngrok_url": sistema_estado.get("ngrok_url")
        }
        
        response = {
            "dataset": stats_dataset,
            "sesiones": stats_sesiones,
            "reentrenamiento": necesidad_retrain,
            "sistema": estado_sistema,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "Error obteniendo estadísticas",
            "mensaje": str(e)
        }), 500

@app.route('/api/training_status', methods=['GET'])
def estado_entrenamiento():
    """Obtiene el estado actual del entrenamiento"""
    try:
        # Verificar necesidad de reentrenamiento
        necesidad = verificar_necesidad_reentrenamiento()
        
        response = {
            "estado_actual": sistema_estado["entrenamiento"],
            "ultimo_entrenamiento": sistema_estado.get("ultimo_entrenamiento"),
            "necesita_reentrenamiento": necesidad["necesita_reentrenamiento"],
            "criterios": necesidad["criterios"],
            "proximo_check_programado": obtener_proximo_check_semanal(),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "Error obteniendo estado de entrenamiento",
            "mensaje": str(e)
        }), 500

@app.route('/api/retrain', methods=['POST'])
def forzar_reentrenamiento():
    """Fuerza el reentrenamiento del modelo (solo para admins)"""
    try:
        # Verificar autenticación básica
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != f"Bearer {API_CONFIG['admin_key']}":
            return jsonify({"error": "No autorizado"}), 401
        
        # Verificar que no hay entrenamiento en progreso
        if sistema_estado["entrenamiento"] == SYSTEM_STATES["training_in_progress"]:
            return jsonify({
                "error": "Ya hay un entrenamiento en progreso",
                "estado_actual": sistema_estado["entrenamiento"]
            }), 409
        
        # Iniciar reentrenamiento en background
        thread = threading.Thread(target=ejecutar_reentrenamiento_background, args=(True,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "iniciado",
            "mensaje": "Reentrenamiento forzado iniciado",
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Error iniciando reentrenamiento",
            "mensaje": str(e)
        }), 500

@app.route('/api/session_stats', methods=['GET'])
def estadisticas_sesiones():
    """Obtiene estadísticas detalladas de las sesiones de usuario"""
    try:
        stats = obtener_estadisticas_sesiones()
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({
            "error": "Error obteniendo estadísticas de sesiones",
            "mensaje": str(e)
        }), 500

# ==================== FUNCIONES DE REENTRENAMIENTO ====================

def verificar_necesidad_reentrenamiento():
    """Verifica si se cumplen los criterios para reentrenamiento"""
    # Obtener estadísticas actuales
    nuevas_total, especies_nuevas, _ = dataset_manager.contar_imagenes_nuevas()
    
    # Criterios de reentrenamiento
    criterios = RETRAINING_CONFIG
    
    cumple_total = nuevas_total >= criterios["min_images_total"]
    cumple_especies = especies_nuevas >= criterios["min_species_with_new_images"]
    
    return {
        "necesita_reentrenamiento": cumple_total and cumple_especies,
        "criterios": {
            "total_imagenes": {
                "actual": nuevas_total,
                "requerido": criterios["min_images_total"],
                "cumple": cumple_total
            },
            "especies_afectadas": {
                "actual": especies_nuevas,
                "requerido": criterios["min_species_with_new_images"],
                "cumple": cumple_especies
            }
        }
    }

def verificar_y_reentrenar_semanal():
    """Función llamada por el scheduler semanal"""
    print(f"🕐 [Scheduler] Verificando necesidad de reentrenamiento semanal...")
    
    necesidad = verificar_necesidad_reentrenamiento()
    
    if necesidad["necesita_reentrenamiento"]:
        print("✅ Criterios cumplidos. Iniciando reentrenamiento automático...")
        ejecutar_reentrenamiento_background(forzado=False)
    else:
        criterios = necesidad["criterios"]
        print(f"❌ Criterios no cumplidos:")
        print(f"   - Imágenes: {criterios['total_imagenes']['actual']}/{criterios['total_imagenes']['requerido']}")
        print(f"   - Especies: {criterios['especies_afectadas']['actual']}/{criterios['especies_afectadas']['requerido']}")

def ejecutar_reentrenamiento_background(forzado=True):
    """Ejecuta el reentrenamiento en background"""
    global sistema_estado
    
    try:
        sistema_estado["entrenamiento"] = SYSTEM_STATES["training_in_progress"]
        print(f"🚀 Iniciando reentrenamiento {'forzado' if forzado else 'programado'}...")
        
        # Importar aquí para evitar imports circulares
        from model.train_model import entrenar_modelo_completo
        
        # Ejecutar entrenamiento
        resultado = entrenar_modelo_completo(incluir_fine_tuning=True)
        
        if resultado["status"] == "exitoso":
            sistema_estado["entrenamiento"] = SYSTEM_STATES["training_completed"]
            sistema_estado["ultimo_entrenamiento"] = datetime.now().isoformat()
            print("✅ Reentrenamiento completado exitosamente")
        else:
            sistema_estado["entrenamiento"] = SYSTEM_STATES["training_failed"]
            print(f"❌ Error en reentrenamiento: {resultado.get('error', 'Error desconocido')}")
            
    except Exception as e:
        sistema_estado["entrenamiento"] = SYSTEM_STATES["training_failed"]
        print(f"❌ Error crítico en reentrenamiento: {e}")
    
    # Resetear a idle después de un tiempo
    threading.Timer(60, lambda: setattr(sistema_estado, "entrenamiento", SYSTEM_STATES["training_idle"])).start()

def obtener_proximo_check_semanal():
    """Calcula cuándo será el próximo check semanal"""
    ahora = datetime.now()
    
    # Encontrar próximo domingo a la 1:00 AM
    dias_hasta_domingo = (6 - ahora.weekday()) % 7
    if dias_hasta_domingo == 0:  # Es domingo
        # Si ya pasó la 1:00 AM, esperar hasta próximo domingo
        if ahora.hour >= 1:
            dias_hasta_domingo = 7
    
    proximo_domingo = ahora.replace(hour=1, minute=0, second=0, microsecond=0)
    proximo_domingo = proximo_domingo + timedelta(days=dias_hasta_domingo)
    
    return proximo_domingo.isoformat()

# ==================== SCHEDULER SEMANAL ====================

def configurar_scheduler_semanal():
    """Configura el scheduler para reentrenamiento semanal"""
    schedule.every().sunday.at("01:00").do(verificar_y_reentrenar_semanal)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Verificar cada hora
    
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    print(f"⏰ Scheduler semanal configurado: domingos a las {RETRAINING_CONFIG['weekly_schedule_time']}")

# ==================== CONFIGURACIÓN DE NGROK ====================

def configurar_ngrok():
    """Configura y lanza Ngrok"""
    try:
        from pyngrok import ngrok
        from config import NGROK_CONFIG
        
        # Configurar token si existe
        if NGROK_CONFIG.get("auth_token"):
            ngrok.set_auth_token(NGROK_CONFIG["auth_token"])
        
        # Crear tunnel
        port = API_CONFIG["port"]
        public_url = ngrok.connect(port)
        sistema_estado["ngrok_url"] = str(public_url)
        
        print(f"🌐 Ngrok tunnel creado: {public_url}")
        print(f"🔗 API accesible en: {public_url}")
        
        # Establecer URL para Firebase (para imágenes)
        try:
            from utils.firebase_config import establecer_url_api_global
            establecer_url_api_global(str(public_url))
        except Exception as e:
            print(f"⚠️ No se pudo establecer URL en Firebase: {e}")
        
        return str(public_url)
        
    except Exception as e:
        print(f"❌ Error configurando Ngrok: {e}")
        print("⚠️ API solo disponible localmente")
        return None

# ==================== FUNCIÓN PRINCIPAL ====================

def iniciar_servidor(usar_ngrok=True, debug=False):
    """
    Inicia el servidor Flask con todas las configuraciones
    
    Args:
        usar_ngrok: Si usar Ngrok para túnel público
        debug: Si ejecutar en modo debug
    """
    print("🚀 INICIANDO API DE GESTIÓN DE PLANTAS")
    print("=" * 50)
    
    # ==================== INICIALIZAR FIRESTORE PRIMERO ====================
    print("\n🔥 Inicializando Firestore para la API...")
    try:
        from utils.firebase_config import firestore_manager
        if firestore_manager.initialize_firestore():
            print("✅ Firestore inicializado correctamente en la API")
        else:
            print("⚠️ Firestore no pudo inicializarse - algunas funciones no estarán disponibles")
    except Exception as e:
        print(f"❌ Error inicializando Firestore: {e}")
    
    # Configurar scheduler semanal
    configurar_scheduler_semanal()
    
    # Configurar Ngrok si se solicita
    if usar_ngrok:
        ngrok_url = configurar_ngrok()
        if ngrok_url:
            print(f"✅ API pública disponible en: {ngrok_url}")
    else:
        # Establecer URL local para Firebase
        try:
            from utils.firebase_config import establecer_url_api_global
            local_url = f"http://localhost:{API_CONFIG['port']}"
            establecer_url_api_global(local_url)
        except Exception as e:
            print(f"⚠️ No se pudo establecer URL local en Firebase: {e}")
    
    # Mostrar información del servidor
    host = API_CONFIG["host"]
    port = API_CONFIG["port"]
    
    print(f"🏠 Servidor local: http://{host}:{port}")
    print(f"📊 Endpoints disponibles:")
    print(f"   - Estado: GET /")
    print(f"   - Guardar imagen: POST /api/save_image")
    print(f"   - Estadísticas: GET /api/stats")
    print(f"   - Estado entrenamiento: GET /api/training_status")
    print(f"   - Forzar reentrenamiento: POST /api/retrain")
    print(f"   - Imagen referencia: GET /api/reference_image/<especie>")
    print(f"   - Verificar imagen: GET /api/check_reference_image/<especie>")
    
    # Iniciar servidor Flask
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    # Si ejecutas este archivo directamente, inicia el servidor
    import argparse
    
    parser = argparse.ArgumentParser(description="API de Gestión de Plantas")
    parser.add_argument("--no-ngrok", action="store_true", help="No usar Ngrok")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    
    args = parser.parse_args()
    
    iniciar_servidor(
        usar_ngrok=not args.no_ngrok,
        debug=args.debug
    )