import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, List, Optional, Any

sys.path.append(str(Path(__file__).parent.parent))
from config import FIREBASE_CONFIG, API_CONFIG

class FirestoreManager:
    """Gestiona la conexión y operaciones con Firestore Database - VERSION CORREGIDA"""
    
    def __init__(self):
        self.db = None
        self.initialized = False
        self._api_base_url = None
        self.collections = FIREBASE_CONFIG["collections"]
        self.plantas_schema = FIREBASE_CONFIG["plantas_schema"]
        
        self._nombre_cache = {}
        
    def initialize_firestore(self, service_account_path=None):
        """Inicializa la conexión con Firestore usando credenciales de servicio."""
        try:
            if service_account_path is None:
                service_account_path = FIREBASE_CONFIG["service_account_path"]
            
            cred_path = Path(service_account_path)
            if not cred_path.exists():
                print(f"❌ Archivo de credenciales no encontrado: {cred_path}")
                return False
            
            if firebase_admin._apps:
                print("✅ Firebase ya está inicializado")
                self.initialized = True
                self.db = firestore.client()
                return True
            
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred, {
                'projectId': FIREBASE_CONFIG["project_id"]
            })
            
            self.db = firestore.client()
            self.initialized = True
            
            print("🔥 Firestore inicializado exitosamente")
            print(f"📊 Proyecto: {FIREBASE_CONFIG['project_id']}")
            print(f"📋 Colección plantas: {self.collections['plantas']}")
            
            if self._test_connection():
                self._cargar_cache_nombres()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error inicializando Firestore: {e}")
            return False
    
    def _test_connection(self, reintentos=3):
        """Prueba la conexión con Firestore realizando un test de escritura y lectura."""
        import time
        
        for intento in range(reintentos):
            try:
                print(f"🔍 Test de conexión Firestore (intento {intento + 1}/{reintentos})")
                
                sistema_ref = self.db.collection('sistema_test')
                doc_ref = sistema_ref.document('conexion_test')
                
                doc_ref.set({
                    'timestamp': datetime.now(),
                    'mensaje': 'Conexión exitosa a Firestore',
                    'version': '1.0_corregida',
                    'intento': intento + 1
                })
                
                doc = doc_ref.get()
                if doc.exists:
                    print("✅ Test de conexión Firestore exitoso")
                    doc_ref.delete()
                    return True
                else:
                    print("⚠️ Conexión establecida pero no se pudo leer datos")
                    
            except Exception as e:
                print(f"❌ Error en test de conexión Firestore (intento {intento + 1}): {e}")
                
                if intento < reintentos - 1:
                    tiempo_espera = (intento + 1) * 2
                    print(f"⏳ Esperando {tiempo_espera}s antes del siguiente intento...")
                    time.sleep(tiempo_espera)
                else:
                    print(f"❌ Falló después de {reintentos} intentos")
                    
        return False
    
    def verificar_salud_conexion(self):
        """Verifica si la conexión con Firestore está activa y responde correctamente."""
        if not self.initialized or not self.db:
            return False
            
        try:
            self.db.collection('sistema_test').limit(1).get()
            return True
        except Exception as e:
            print(f"⚠️ Conexión Firebase perdida: {e}")
            return False
    
    def reconectar_firestore(self):
        """Intenta reconectar a Firestore usando configuración de Streamlit secrets."""
        try:
            print("🔄 Intentando reconectar a Firestore...")
            
            import streamlit as st
            
            if "firebase" in st.secrets:
                import firebase_admin
                from firebase_admin import credentials, firestore
                
                if firebase_admin._apps:
                    firebase_admin._apps.clear()
                
                firebase_creds = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_creds)
                firebase_admin.initialize_app(cred)
                
                self.db = firestore.client()
                self.initialized = True
                
                if self._test_connection(reintentos=1):
                    print("✅ Reconexión exitosa usando secrets")
                    return True
                else:
                    print("❌ Test de reconexión falló")
                    return False
            else:
                print("❌ No se encontraron secrets de Firebase para reconexión")
                return False
                
        except Exception as e:
            print(f"❌ Error durante reconexión: {e}")
            return False
    
    def _normalizar_nombre_a_firestore(self, nombre_modelo: str) -> List[str]:
        """Convierte nombre del modelo al formato de nombres en Firestore."""
        """
        Convierte nombre del modelo al formato de Firestore
        
        Args:
            nombre_modelo: "Agave_americana_L" (formato del modelo)
        
        Returns:
            List[str]: Lista de posibles nombres en Firestore ["Agave americana L.", "Agave americana L", etc.]
        """
        variaciones = []
        
        nombre_espacios = nombre_modelo.replace('_', ' ')
        variaciones.append(nombre_espacios)
        
        if not nombre_espacios.endswith('.'):
            variaciones.append(nombre_espacios + '.')
        
        if nombre_espacios.endswith('.'):
            variaciones.append(nombre_espacios[:-1])
        
        if '(' in nombre_modelo:
            nombre_parentesis = re.sub(r'_\(', ' (', nombre_modelo)
            nombre_parentesis = re.sub(r'\)_', ') ', nombre_parentesis)
            nombre_parentesis = nombre_parentesis.replace('_', ' ')
            variaciones.append(nombre_parentesis)
            if not nombre_parentesis.endswith('.'):
                variaciones.append(nombre_parentesis + '.')
        
        variaciones_unicas = []
        for var in variaciones:
            if var not in variaciones_unicas:
                variaciones_unicas.append(var)
        
        return variaciones_unicas
    
    def _normalizar_nombre_a_modelo(self, nombre_firestore: str) -> str:
        """Convierte nombre de Firestore al formato esperado por el modelo."""
        """
        Convierte nombre de Firestore al formato del modelo
        
        Args:
            nombre_firestore: "Agave americana L." (formato Firestore)
        
        Returns:
            str: "Agave_americana_L" (formato del modelo)
        """
        nombre = nombre_firestore.rstrip('.')
        
        nombre = nombre.replace(' ', '_')
        
        nombre = re.sub(r' \(', '_(', nombre)
        nombre = re.sub(r'\) ', ')_', nombre)
        
        return nombre
    
    def _cargar_cache_nombres(self):
        """Carga un cache de nombres científicos para acelerar búsquedas futuras."""
        try:
            print("📋 Cargando cache de nombres científicos...")
            
            plantas_ref = self.db.collection(self.collections["plantas"])
            docs = plantas_ref.limit(50).stream()
            
            for doc in docs:
                data = doc.to_dict()
                nombre_firestore = data.get('nombre_cientifico', '')
                if nombre_firestore:
                    nombre_modelo = self._normalizar_nombre_a_modelo(nombre_firestore)
                    self._nombre_cache[nombre_modelo] = nombre_firestore
            
            print(f"✅ Cache cargado con {len(self._nombre_cache)} nombres")
            
        except Exception as e:
            print(f"⚠️ Error cargando cache de nombres: {e}")
    
    def obtener_info_especie_basica(self, nombre_cientifico: str) -> Dict[str, Any]:
        """Obtiene información básica de una especie con normalización de nombres y reconexiones automáticas."""
        """
        Búsqueda básica con normalización de nombres y reconexión automática
        
        Args:
            nombre_cientifico: Nombre científico de la especie (formato del modelo)
        
        Returns:
            dict: Información básica de la especie
        """
        try:
            if not self.initialized or not self.verificar_salud_conexion():
                print("⚠️ Firestore no disponible, intentando reconectar...")
                if not self.reconectar_firestore():
                    print("❌ No se pudo reconectar a Firestore")
                    return self._generar_info_error(nombre_cientifico, "Conexión a Firebase perdida")
            
            print(f"🔍 Búsqueda con normalización para: {nombre_cientifico}")
            
            for intento in range(2):
                try:
                    return self._ejecutar_busqueda(nombre_cientifico)
                except Exception as e:
                    print(f"❌ Error en búsqueda (intento {intento + 1}): {e}")
                    
                    if intento == 0:
                        print("🔄 Intentando reconectar...")
                        if self.reconectar_firestore():
                            continue
                    
                    return self._generar_info_error(nombre_cientifico, str(e))
                    
        except Exception as e:
            print(f"❌ Error general en búsqueda: {e}")
            return self._generar_info_error(nombre_cientifico, str(e))
    
    def _ejecutar_busqueda(self, nombre_cientifico: str) -> Dict[str, Any]:
        """Ejecuta la búsqueda principal de especies en Firestore con normalización de nombres."""
        if nombre_cientifico in self._nombre_cache:
            nombre_firestore = self._nombre_cache[nombre_cientifico]
            print(f"💨 Encontrado en cache: {nombre_firestore}")
            return self._buscar_por_nombre_exacto(nombre_firestore, nombre_cientifico)
        
        variaciones = self._normalizar_nombre_a_firestore(nombre_cientifico)
        print(f"🔄 Probando variaciones: {variaciones}")
        
        plantas_ref = self.db.collection(self.collections["plantas"])
        
        for variacion in variaciones:
            query = plantas_ref.where('nombre_cientifico', '==', variacion).limit(1)
            docs = list(query.stream())
            
            if docs:
                print(f"✅ Encontrado con variación: '{variacion}'")
                
                self._nombre_cache[nombre_cientifico] = variacion
                
                data = docs[0].to_dict()
                return self._procesar_datos_firestore(data, nombre_cientifico)
        
        print(f"🔍 Búsqueda parcial para: {nombre_cientifico}")
        resultado_parcial = self._busqueda_parcial_inteligente(nombre_cientifico)
        
        if resultado_parcial:
            return resultado_parcial
        
        print(f"❌ No encontrado en Firestore: {nombre_cientifico}")
        return self._generar_info_no_encontrada(nombre_cientifico)
    
    def _buscar_por_nombre_exacto(self, nombre_firestore: str, nombre_original: str) -> Dict[str, Any]:
        """Realiza búsqueda exacta por nombre científico en Firestore."""
        try:
            plantas_ref = self.db.collection(self.collections["plantas"])
            query = plantas_ref.where('nombre_cientifico', '==', nombre_firestore).limit(1)
            docs = list(query.stream())
            
            if docs:
                data = docs[0].to_dict()
                return self._procesar_datos_firestore(data, nombre_original)
            else:
                return self._generar_info_no_encontrada(nombre_original)
                
        except Exception as e:
            return self._generar_info_error(nombre_original, str(e))
    
    def _busqueda_parcial_inteligente(self, nombre_cientifico: str) -> Optional[Dict[str, Any]]:
        """Realiza búsqueda parcial por género y especie cuando no se encuentra coincidencia exacta."""
        try:
            partes = nombre_cientifico.replace('_', ' ').split()
            
            if len(partes) >= 2:
                genero = partes[0]
                especie = partes[1]
                
                print(f"🔍 Buscando género '{genero}' y especie '{especie}'")
                
                plantas_ref = self.db.collection(self.collections["plantas"])
                
                docs = plantas_ref.limit(50).stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    nombre_doc = data.get('nombre_cientifico', '').lower()
                    
                    if genero.lower() in nombre_doc and especie.lower() in nombre_doc:
                        print(f"🎯 Coincidencia parcial encontrada: {data.get('nombre_cientifico')}")
                        
                        self._nombre_cache[nombre_cientifico] = data.get('nombre_cientifico')
                        
                        return self._procesar_datos_firestore(data, nombre_cientifico)
            
            return None
            
        except Exception as e:
            print(f"❌ Error en búsqueda parcial: {e}")
            return None
    
    def _procesar_datos_firestore(self, data: Dict[str, Any], nombre_original: str) -> Dict[str, Any]:
        """Procesa y formatea los datos obtenidos de Firestore para presentación."""
        
        imagen_url = ""
        if 'imagenes' in data and data['imagenes']:
            if isinstance(data['imagenes'], list) and len(data['imagenes']) > 0:
                imagen_url = data['imagenes'][0]
            elif isinstance(data['imagenes'], str):
                imagen_url = data['imagenes']
        
        if not imagen_url:
            imagen_url = self._generar_url_imagen_referencia(nombre_original)
        
        taxonomia = data.get('taxonomia', {})
        if isinstance(taxonomia, list):
            taxonomia = {}
        
        info_procesada = {
            "nombre_cientifico": data.get('nombre_cientifico', nombre_original),
            "nombre_comun": data.get('nombre_comun', 'Nombre no disponible'),
            "descripcion": data.get('descripcion', ''),
            "cuidados": data.get('cuidados', ''),
            "fecha_observacion": str(data.get('fecha_observacion', '')),
            "fuente": data.get('fuente', ''),
            "imagen_referencia": imagen_url,
            
            "taxonomia": taxonomia,
            
            "fuente_datos": "firestore",
            "timestamp_consulta": datetime.now().isoformat(),
            "nombre_original_buscado": nombre_original
        }
        
        return info_procesada
    
    def _generar_info_no_encontrada(self, nombre_cientifico: str) -> Dict[str, Any]:
        """Genera información de respuesta cuando no se encuentra la especie en la base de datos."""
        return {
            "nombre_cientifico": nombre_cientifico,
            "nombre_comun": "Especie no encontrada en la base de datos",
            "descripcion": f"La especie '{nombre_cientifico}' no está registrada en la base de datos. Esto puede deberse a diferencias en el formato del nombre científico.",
            "fecha_observacion": "",
            "fuente": "",
            "imagen_referencia": self._generar_url_imagen_referencia(nombre_cientifico),
            "taxonomia": {},
            "fuente_datos": "no_encontrado",
            "timestamp_consulta": datetime.now().isoformat()
        }
    
    def _generar_info_error(self, nombre_cientifico: str, error_msg: str) -> Dict[str, Any]:
        """Genera información de respuesta cuando ocurre un error de conexión."""
        return {
            "nombre_cientifico": nombre_cientifico,
            "nombre_comun": "Error de conexión",
            "descripcion": f"Error conectando con la base de datos: {error_msg}",
            "fecha_observacion": "",
            "fuente": "",
            "imagen_referencia": "",
            "taxonomia": {},
            "fuente_datos": "error",
            "timestamp_consulta": datetime.now().isoformat()
        }
    
    def _generar_url_imagen_referencia(self, nombre_especie: str) -> str:
        """Genera URL para obtener imagen de referencia desde la API local."""
        try:
            if self._api_base_url:
                base_url = self._api_base_url
            else:
                base_url = f"http://localhost:{API_CONFIG['port']}"
            
            return f"{base_url}/api/reference_image/{nombre_especie}"
            
        except Exception as e:
            print(f"⚠️ Error generando URL de imagen para {nombre_especie}: {e}")
            return ""
    
    def establecer_url_api(self, url_api: str):
        """Establece la URL base de la API para generar URLs de imágenes de referencia."""
        self._api_base_url = url_api
        print(f"🔗 URL de API establecida para Firestore: {url_api}")
    
    def obtener_info_especie(self, nombre_cientifico: str) -> Dict[str, Any]:
        """Función original mantenida para compatibilidad con código existente."""
        return self.obtener_info_especie_basica(nombre_cientifico)
    
    def guardar_analisis_usuario(self, datos_analisis: Dict[str, Any]) -> Dict[str, str]:
        """Guarda los datos de análisis de un usuario en la colección de Firestore."""
        if not self.initialized:
            print("⚠️ Firestore no inicializado")
            return {"status": "error", "mensaje": "Firestore no inicializado"}
        
        try:
            analisis_completo = {
                **datos_analisis,
                "timestamp": datetime.now(),
                "timestamp_iso": datetime.now().isoformat(),
                "fuente": "streamlit_app",
                "version_sistema": "1.0_corregida"
            }
            
            analisis_ref = self.db.collection(self.collections["analisis_usuarios"])
            doc_ref = analisis_ref.add(analisis_completo)
            
            print(f"✅ Análisis guardado en Firestore: {doc_ref[1].id}")
            return {"status": "guardado", "id": doc_ref[1].id}
            
        except Exception as e:
            print(f"❌ Error guardando análisis: {e}")
            return {"status": "error", "mensaje": str(e)}
    
    def listar_todas_especies(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene una lista de todas las especies disponibles en la base de datos."""
        try:
            if not self.initialized:
                return []
            
            plantas_ref = self.db.collection(self.collections["plantas"])
            docs = plantas_ref.limit(limite).stream()
            
            especies = []
            for doc in docs:
                data = doc.to_dict()
                especies.append({
                    "nombre_cientifico": data.get('nombre_cientifico', ''),
                    "nombre_comun": data.get('nombre_comun', ''),
                    "familia": data.get('taxonomia', {}).get('familia', ''),
                    "documento_id": doc.id
                })
            
            print(f"📋 {len(especies)} especies listadas desde Firestore")
            return especies
            
        except Exception as e:
            print(f"❌ Error listando especies: {e}")
            return []

firestore_manager = FirestoreManager()

def inicializar_firestore():
    """Función de conveniencia para inicializar la conexión con Firestore."""
    return firestore_manager.initialize_firestore()

def obtener_info_planta_basica(nombre_especie):
    """Función de conveniencia para obtener información básica de una planta."""
    return firestore_manager.obtener_info_especie_basica(nombre_especie)

def obtener_info_planta(nombre_especie):
    """Función de conveniencia para obtener información completa de una planta."""
    return firestore_manager.obtener_info_especie_basica(nombre_especie)

def guardar_analisis(datos):
    """Función de conveniencia para guardar datos de análisis en Firestore."""
    return firestore_manager.guardar_analisis_usuario(datos)

def establecer_url_api_global(url_api):
    """Función de conveniencia para establecer la URL de la API globalmente."""
    firestore_manager.establecer_url_api(url_api)

def listar_especies_disponibles(limite=100):
    """Función de conveniencia para listar especies disponibles en la base de datos."""
    return firestore_manager.listar_todas_especies(limite)

firebase_manager = firestore_manager

if __name__ == "__main__":
    print("🔥 TESTING FIREBASE CONFIG CORREGIDO")
    print("=" * 50)
    
    # Test de inicialización
    if inicializar_firestore():
        print("\n✅ Firestore inicializado correctamente")
        
        # Test de búsquedas específicas que antes fallaban
        nombres_test = [
            "Agave_americana_L",
            "Adiantum_macrophyllum_Sw",
            "Acrocomia_aculeata_(Jacq.)_Lodd._ex_R.Keith"
        ]
        
        print("\n🧪 TESTING BÚSQUEDAS CORREGIDAS:")
        for nombre in nombres_test:
            print(f"\n🔍 Buscando: {nombre}")
            info = obtener_info_planta_basica(nombre)
            
            if info.get('fuente_datos') == 'firestore':
                print(f"   ✅ ENCONTRADO: {info['nombre_comun']}")
                print(f"   📝 Nombre en Firestore: {info['nombre_cientifico']}")
            else:
                print(f"   ❌ No encontrado: {info['fuente_datos']}")
        
    else:
        print("\n❌ Error en inicialización")