# utils/firebase_config.py - VERSION CORREGIDA CON NORMALIZACIÓN DE NOMBRES

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, List, Optional, Any

# Agregar directorio padre al path
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
        
        # Cache para mapeo de nombres (mejora rendimiento)
        self._nombre_cache = {}
        
    def initialize_firestore(self, service_account_path=None):
        """Inicializa Firestore con las credenciales reales"""
        try:
            if service_account_path is None:
                service_account_path = FIREBASE_CONFIG["service_account_path"]
            
            # Verificar que existe el archivo de credenciales
            cred_path = Path(service_account_path)
            if not cred_path.exists():
                print(f"❌ Archivo de credenciales no encontrado: {cred_path}")
                return False
            
            # Verificar que no esté ya inicializado
            if firebase_admin._apps:
                print("✅ Firebase ya está inicializado")
                self.initialized = True
                self.db = firestore.client()
                return True
            
            # Inicializar Firebase para Firestore
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred, {
                'projectId': FIREBASE_CONFIG["project_id"]
            })
            
            self.db = firestore.client()
            self.initialized = True
            
            print("🔥 Firestore inicializado exitosamente")
            print(f"📊 Proyecto: {FIREBASE_CONFIG['project_id']}")
            print(f"📋 Colección plantas: {self.collections['plantas']}")
            
            # Verificar conexión y cargar cache de nombres
            if self._test_connection():
                self._cargar_cache_nombres()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error inicializando Firestore: {e}")
            return False
    
    def _test_connection(self):
        """Prueba la conexión con Firestore"""
        try:
            # Test básico con documento temporal
            sistema_ref = self.db.collection('sistema_test')
            doc_ref = sistema_ref.document('conexion_test')
            
            doc_ref.set({
                'timestamp': datetime.now(),
                'mensaje': 'Conexión exitosa a Firestore',
                'version': '1.0_corregida'
            })
            
            # Leer el documento
            doc = doc_ref.get()
            if doc.exists:
                print("✅ Test de conexión Firestore exitoso")
                doc_ref.delete()  # Limpiar
                return True
            else:
                print("⚠️ Conexión establecida pero no se pudo leer datos")
                return False
                
        except Exception as e:
            print(f"❌ Error en test de conexión Firestore: {e}")
            return False
    
    # ==================== NUEVAS FUNCIONES DE NORMALIZACIÓN ====================
    
    def _normalizar_nombre_a_firestore(self, nombre_modelo: str) -> List[str]:
        """
        Convierte nombre del modelo al formato de Firestore
        
        Args:
            nombre_modelo: "Agave_americana_L" (formato del modelo)
        
        Returns:
            List[str]: Lista de posibles nombres en Firestore ["Agave americana L.", "Agave americana L", etc.]
        """
        variaciones = []
        
        # Conversión básica: guiones bajos a espacios
        nombre_espacios = nombre_modelo.replace('_', ' ')
        variaciones.append(nombre_espacios)
        
        # Con punto al final
        if not nombre_espacios.endswith('.'):
            variaciones.append(nombre_espacios + '.')
        
        # Sin punto al final
        if nombre_espacios.endswith('.'):
            variaciones.append(nombre_espacios[:-1])
        
        # Variaciones con paréntesis (común en nombres científicos)
        # Ejemplo: "Agave_americana_(L.)_Oerst" -> "Agave americana (L.) Oerst."
        if '(' in nombre_modelo:
            nombre_parentesis = re.sub(r'_\(', ' (', nombre_modelo)
            nombre_parentesis = re.sub(r'\)_', ') ', nombre_parentesis)
            nombre_parentesis = nombre_parentesis.replace('_', ' ')
            variaciones.append(nombre_parentesis)
            if not nombre_parentesis.endswith('.'):
                variaciones.append(nombre_parentesis + '.')
        
        # Remover duplicados manteniendo orden
        variaciones_unicas = []
        for var in variaciones:
            if var not in variaciones_unicas:
                variaciones_unicas.append(var)
        
        return variaciones_unicas
    
    def _normalizar_nombre_a_modelo(self, nombre_firestore: str) -> str:
        """
        Convierte nombre de Firestore al formato del modelo
        
        Args:
            nombre_firestore: "Agave americana L." (formato Firestore)
        
        Returns:
            str: "Agave_americana_L" (formato del modelo)
        """
        # Remover punto final si existe
        nombre = nombre_firestore.rstrip('.')
        
        # Reemplazar espacios con guiones bajos
        nombre = nombre.replace(' ', '_')
        
        # Manejar paréntesis
        nombre = re.sub(r' \(', '_(', nombre)
        nombre = re.sub(r'\) ', ')_', nombre)
        
        return nombre
    
    def _cargar_cache_nombres(self):
        """Carga un cache de nombres para búsquedas más rápidas"""
        try:
            print("📋 Cargando cache de nombres científicos...")
            
            plantas_ref = self.db.collection(self.collections["plantas"])
            docs = plantas_ref.limit(50).stream()  # Cargar primeros 50 para cache inicial
            
            for doc in docs:
                data = doc.to_dict()
                nombre_firestore = data.get('nombre_cientifico', '')
                if nombre_firestore:
                    nombre_modelo = self._normalizar_nombre_a_modelo(nombre_firestore)
                    self._nombre_cache[nombre_modelo] = nombre_firestore
            
            print(f"✅ Cache cargado con {len(self._nombre_cache)} nombres")
            
        except Exception as e:
            print(f"⚠️ Error cargando cache de nombres: {e}")
    
    # ==================== FUNCIÓN PRINCIPAL CORREGIDA ====================
    
    def obtener_info_especie_basica(self, nombre_cientifico: str) -> Dict[str, Any]:
        """
        Búsqueda básica con normalización de nombres - VERSION CORREGIDA
        
        Args:
            nombre_cientifico: Nombre científico de la especie (formato del modelo)
        
        Returns:
            dict: Información básica de la especie
        """
        try:
            if not self.initialized:
                print("⚠️ Firestore no inicializado")
                return self._generar_info_no_encontrada(nombre_cientifico)
            
            print(f"🔍 Búsqueda con normalización para: {nombre_cientifico}")
            
            # 1. Buscar en cache primero
            if nombre_cientifico in self._nombre_cache:
                nombre_firestore = self._nombre_cache[nombre_cientifico]
                print(f"💨 Encontrado en cache: {nombre_firestore}")
                return self._buscar_por_nombre_exacto(nombre_firestore, nombre_cientifico)
            
            # 2. Generar variaciones de nombres para Firestore
            variaciones = self._normalizar_nombre_a_firestore(nombre_cientifico)
            print(f"🔄 Probando variaciones: {variaciones}")
            
            plantas_ref = self.db.collection(self.collections["plantas"])
            
            # 3. Buscar cada variación
            for variacion in variaciones:
                query = plantas_ref.where('nombre_cientifico', '==', variacion).limit(1)
                docs = list(query.stream())
                
                if docs:
                    print(f"✅ Encontrado con variación: '{variacion}'")
                    
                    # Agregar al cache
                    self._nombre_cache[nombre_cientifico] = variacion
                    
                    # Procesar y retornar datos
                    data = docs[0].to_dict()
                    return self._procesar_datos_firestore(data, nombre_cientifico)
            
            # 4. Búsqueda parcial como último recurso
            print(f"🔍 Búsqueda parcial para: {nombre_cientifico}")
            resultado_parcial = self._busqueda_parcial_inteligente(nombre_cientifico)
            
            if resultado_parcial:
                return resultado_parcial
            
            # 5. No encontrado
            print(f"❌ No encontrado en Firestore: {nombre_cientifico}")
            return self._generar_info_no_encontrada(nombre_cientifico)
                
        except Exception as e:
            print(f"❌ Error en búsqueda básica: {e}")
            return self._generar_info_error(nombre_cientifico, str(e))
    
    def _buscar_por_nombre_exacto(self, nombre_firestore: str, nombre_original: str) -> Dict[str, Any]:
        """Busca por nombre exacto en Firestore"""
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
        """Búsqueda parcial más inteligente"""
        try:
            # Extraer género y especie
            partes = nombre_cientifico.replace('_', ' ').split()
            
            if len(partes) >= 2:
                genero = partes[0]
                especie = partes[1]
                
                print(f"🔍 Buscando género '{genero}' y especie '{especie}'")
                
                plantas_ref = self.db.collection(self.collections["plantas"])
                
                # Buscar documentos que contengan el género en el nombre científico
                docs = plantas_ref.limit(50).stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    nombre_doc = data.get('nombre_cientifico', '').lower()
                    
                    # Verificar si contiene género y especie
                    if genero.lower() in nombre_doc and especie.lower() in nombre_doc:
                        print(f"🎯 Coincidencia parcial encontrada: {data.get('nombre_cientifico')}")
                        
                        # Agregar al cache
                        self._nombre_cache[nombre_cientifico] = data.get('nombre_cientifico')
                        
                        return self._procesar_datos_firestore(data, nombre_cientifico)
            
            return None
            
        except Exception as e:
            print(f"❌ Error en búsqueda parcial: {e}")
            return None
    
    def _procesar_datos_firestore(self, data: Dict[str, Any], nombre_original: str) -> Dict[str, Any]:
        """Procesa datos obtenidos de Firestore"""
        
        # Procesar imagen URL - ahora usando el campo 'imagenes' que encontramos
        imagen_url = ""
        if 'imagenes' in data and data['imagenes']:
            if isinstance(data['imagenes'], list) and len(data['imagenes']) > 0:
                imagen_url = data['imagenes'][0]  # Tomar primera imagen
            elif isinstance(data['imagenes'], str):
                imagen_url = data['imagenes']
        
        # Si no hay imagen en Firestore, usar API local
        if not imagen_url:
            imagen_url = self._generar_url_imagen_referencia(nombre_original)
        
        # Procesar taxonomía
        taxonomia = data.get('taxonomia', {})
        if isinstance(taxonomia, list):
            # Convertir lista a dict si es necesario
            taxonomia = {}
        
        # Información procesada
        info_procesada = {
            "nombre_cientifico": data.get('nombre_cientifico', nombre_original),
            "nombre_comun": data.get('nombre_comun', 'Nombre no disponible'),
            "descripcion": data.get('descripcion', ''),
            "cuidados": data.get('cuidados', ''),  # ← AGREGADO: Campo cuidados
            "fecha_observacion": str(data.get('fecha_observacion', '')),
            "fuente": data.get('fuente', ''),
            "imagen_referencia": imagen_url,
            
            # Taxonomía
            "taxonomia": taxonomia,
            
            # Metadatos
            "fuente_datos": "firestore",
            "timestamp_consulta": datetime.now().isoformat(),
            "nombre_original_buscado": nombre_original
        }
        
        return info_procesada
    
    # ==================== FUNCIONES DE INFORMACIÓN NO ENCONTRADA/ERROR ====================
    
    def _generar_info_no_encontrada(self, nombre_cientifico: str) -> Dict[str, Any]:
        """Genera información cuando no se encuentra la especie"""
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
        """Genera información cuando hay error de conexión"""
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
    
    # ==================== FUNCIONES AUXILIARES EXISTENTES ====================
    
    def _generar_url_imagen_referencia(self, nombre_especie: str) -> str:
        """Genera URL para imagen de referencia usando la API"""
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
        """Establece la URL base de la API para generar URLs de imágenes"""
        self._api_base_url = url_api
        print(f"🔗 URL de API establecida para Firestore: {url_api}")
    
    # ==================== FUNCIONES EXISTENTES (MANTENIDAS) ====================
    
    def obtener_info_especie(self, nombre_cientifico: str) -> Dict[str, Any]:
        """Función original mantenida para compatibilidad"""
        return self.obtener_info_especie_basica(nombre_cientifico)
    
    def guardar_analisis_usuario(self, datos_analisis: Dict[str, Any]) -> Dict[str, str]:
        """Guarda un análisis de usuario en Firestore"""
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
        """Lista todas las especies disponibles en Firestore"""
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

# ==================== INSTANCIA GLOBAL Y FUNCIONES DE CONVENIENCIA ====================

# Instancia global con la nueva versión corregida
firestore_manager = FirestoreManager()

def inicializar_firestore():
    """Función de conveniencia para inicializar Firestore"""
    return firestore_manager.initialize_firestore()

def obtener_info_planta_basica(nombre_especie):
    """Función de conveniencia para obtener info básica de planta - CORREGIDA"""
    return firestore_manager.obtener_info_especie_basica(nombre_especie)

def obtener_info_planta(nombre_especie):
    """Función de conveniencia para obtener info de planta"""
    return firestore_manager.obtener_info_especie_basica(nombre_especie)

def guardar_analisis(datos):
    """Función de conveniencia para guardar análisis"""
    return firestore_manager.guardar_analisis_usuario(datos)

def establecer_url_api_global(url_api):
    """Establece la URL de la API globalmente"""
    firestore_manager.establecer_url_api(url_api)

def listar_especies_disponibles(limite=100):
    """Función de conveniencia para listar especies"""
    return firestore_manager.listar_todas_especies(limite)

# Compatibilidad con código anterior
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