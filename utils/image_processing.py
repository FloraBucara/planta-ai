import cv2
import numpy as np
from PIL import Image
import os
import json
from pathlib import Path
from datetime import datetime
import sys

# Agregar el directorio padre al path para importar config
sys.path.append(str(Path(__file__).parent.parent))
from config import MODEL_CONFIG, PLANTAS_DIR, PATHS

class ImageProcessor:
    """Clase para manejar todo el procesamiento de imágenes"""
    
    def __init__(self):
        self.target_size = MODEL_CONFIG["target_size"]
        self.input_shape = MODEL_CONFIG["input_shape"]
    
    def cargar_y_procesar_imagen(self, ruta_imagen):
        """
        Carga y procesa una imagen para el modelo
        
        Args:
            ruta_imagen: Ruta a la imagen, PIL Image, o numpy array
        
        Returns:
            numpy array procesado o None si hay error
        """
        try:
            # Determinar el tipo de entrada y cargar
            if isinstance(ruta_imagen, (str, Path)):
                # Es una ruta de archivo
                imagen = cv2.imread(str(ruta_imagen))
                if imagen is None:
                    print(f"❌ Error: No se pudo cargar la imagen {ruta_imagen}")
                    return None
                imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
                
            elif isinstance(ruta_imagen, Image.Image):
                # Es una imagen PIL (desde Streamlit)
                imagen = np.array(ruta_imagen.convert('RGB'))
                
            elif isinstance(ruta_imagen, np.ndarray):
                # Ya es un numpy array
                imagen = ruta_imagen.copy()
                
            else:
                print(f"❌ Tipo de imagen no soportado: {type(ruta_imagen)}")
                return None
            
            # Redimensionar manteniendo aspecto
            imagen_redim = self._redimensionar_con_aspecto(imagen)
            
            # Normalizar valores (0-1)
            imagen_norm = imagen_redim.astype(np.float32) / 255.0
            
            return imagen_norm
            
        except Exception as e:
            print(f"❌ Error procesando imagen: {e}")
            return None
    
    def procesar_para_prediccion(self, imagen):
        """
        Procesa una imagen para hacer predicción (agrega dimensión batch)
        
        Args:
            imagen: Imagen en cualquier formato soportado
        
        Returns:
            numpy array con shape (1, 3, 224, 224) para ONNX
        """
        img_procesada = self.cargar_y_procesar_imagen(imagen)
        
        if img_procesada is not None:
            # Agregar dimensión batch: (224, 224, 3) -> (1, 224, 224, 3)
            img_batch = np.expand_dims(img_procesada, axis=0)
            
            # Convertir de NHWC a NCHW para ONNX: (1, 224, 224, 3) -> (1, 3, 224, 224)
            img_onnx = np.transpose(img_batch, (0, 3, 1, 2))
            
            return img_onnx
        
        return None
    
    def _redimensionar_con_aspecto(self, imagen):
        """
        Redimensiona manteniendo la relación de aspecto y rellenando con padding
        """
        h, w = imagen.shape[:2]
        target_h, target_w = self.target_size
        
        # Calcular escala para mantener aspecto
        escala = min(target_w / w, target_h / h)
        
        # Nuevo tamaño
        nuevo_w = int(w * escala)
        nuevo_h = int(h * escala)
        
        # Redimensionar
        imagen_redim = cv2.resize(imagen, (nuevo_w, nuevo_h))
        
        # Crear imagen final con padding negro
        imagen_final = np.zeros((target_h, target_w, 3), dtype=imagen.dtype)
        
        # Centrar la imagen redimensionada
        y_offset = (target_h - nuevo_h) // 2
        x_offset = (target_w - nuevo_w) // 2
        
        imagen_final[y_offset:y_offset+nuevo_h, x_offset:x_offset+nuevo_w] = imagen_redim
        
        return imagen_final

class DatasetManager:
    """Clase para manejar el dataset de plantas"""
    
    def __init__(self):
        self.plantas_dir = PLANTAS_DIR
        self.processor = ImageProcessor()
    
    def cargar_dataset_completo(self, incluir_augmentation=False):
        """
        Carga todo el dataset desde las carpetas
        
        Args:
            incluir_augmentation: Si aplicar data augmentation
        
        Returns:
            tuple: (imagenes, etiquetas, nombres_especies)
        """
        print("🔍 Cargando dataset completo...")
        
        if not self.plantas_dir.exists():
            raise Exception(f"Directorio de plantas no encontrado: {self.plantas_dir}")
        
        imagenes = []
        etiquetas = []
        nombres_especies = []
        
        # Obtener carpetas de especies (ordenadas para consistencia)
        carpetas_especies = sorted([d for d in self.plantas_dir.iterdir() if d.is_dir()])
        
        for idx, carpeta_especie in enumerate(carpetas_especies):
            nombre_especie = carpeta_especie.name
            nombres_especies.append(nombre_especie)
            
            # Obtener imágenes de esta especie
            imagenes_especie = self._obtener_imagenes_carpeta(carpeta_especie)
            
            print(f"📁 {nombre_especie}: {len(imagenes_especie)} imágenes")
            
            for ruta_imagen in imagenes_especie:
                img_procesada = self.processor.cargar_y_procesar_imagen(ruta_imagen)
                
                if img_procesada is not None:
                    imagenes.append(img_procesada)
                    etiquetas.append(idx)
                    
                    # Aplicar data augmentation si se solicita
                    if incluir_augmentation:
                        img_aug = self._aplicar_augmentation(img_procesada)
                        imagenes.append(img_aug)
                        etiquetas.append(idx)
        
        print(f"✅ Dataset cargado: {len(imagenes)} imágenes de {len(nombres_especies)} especies")
        
        # Guardar lista de especies para uso posterior
        self._guardar_lista_especies(nombres_especies)
        
        return np.array(imagenes), np.array(etiquetas), nombres_especies
    
    def _obtener_imagenes_carpeta(self, carpeta):
        """Obtiene todas las imágenes de una carpeta"""
        extensiones = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
        
        imagenes = [archivo for archivo in carpeta.iterdir() 
                   if archivo.suffix in extensiones]
        
        return sorted(imagenes)
    
    def _aplicar_augmentation(self, imagen):
        """Aplica transformaciones de data augmentation"""
        img_aug = imagen.copy()
        
        # Rotación aleatoria (-15 a +15 grados)
        if np.random.random() > 0.5:
            angulo = np.random.uniform(-15, 15)
            h, w = img_aug.shape[:2]
            centro = (w//2, h//2)
            matriz_rot = cv2.getRotationMatrix2D(centro, angulo, 1.0)
            img_aug = cv2.warpAffine(img_aug, matriz_rot, (w, h))
        
        # Flip horizontal
        if np.random.random() > 0.5:
            img_aug = cv2.flip(img_aug, 1)
        
        # Ajuste de brillo
        if np.random.random() > 0.5:
            factor = np.random.uniform(0.8, 1.2)
            img_aug = np.clip(img_aug * factor, 0, 1)
        
        # Ruido gaussiano leve
        if np.random.random() > 0.7:
            ruido = np.random.normal(0, 0.02, img_aug.shape)
            img_aug = np.clip(img_aug + ruido, 0, 1)
        
        return img_aug
    
    def _guardar_lista_especies(self, nombres_especies):
        """Guarda la lista de especies en un archivo JSON"""
        try:
            with open(PATHS["species_list_file"], 'w', encoding='utf-8') as f:
                json.dump(nombres_especies, f, ensure_ascii=False, indent=2)
            print(f"✅ Lista de especies guardada en {PATHS['species_list_file']}")
        except Exception as e:
            print(f"❌ Error guardando lista de especies: {e}")
    
    def cargar_lista_especies(self):
        """Carga la lista de especies desde el archivo JSON"""
        try:
            if PATHS["species_list_file"].exists():
                with open(PATHS["species_list_file"], 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Archivo de especies no encontrado: {PATHS['species_list_file']}")
                return None
        except Exception as e:
            print(f"❌ Error cargando lista de especies: {e}")
            return None
    
    def contar_imagenes_por_especie(self):
        """Cuenta las imágenes por cada especie"""
        conteo = {}
        
        if not self.plantas_dir.exists():
            return conteo
        
        for carpeta in self.plantas_dir.iterdir():
            if carpeta.is_dir():
                imagenes = self._obtener_imagenes_carpeta(carpeta)
                conteo[carpeta.name] = len(imagenes)
        
        return conteo
    
    def contar_imagenes_nuevas(self):
        """
        Cuenta imágenes nuevas (que contienen 'user_' en el nombre)
        
        Returns:
            tuple: (total_nuevas, especies_con_nuevas, detalle_por_especie)
        """
        total_nuevas = 0
        especies_con_nuevas = set()
        detalle = {}
        
        for carpeta in self.plantas_dir.iterdir():
            if carpeta.is_dir():
                imagenes_nuevas = [img for img in self._obtener_imagenes_carpeta(carpeta)
                                 if 'user_' in img.name]
                
                if len(imagenes_nuevas) > 0:
                    total_nuevas += len(imagenes_nuevas)
                    especies_con_nuevas.add(carpeta.name)
                    detalle[carpeta.name] = len(imagenes_nuevas)
        
        return total_nuevas, len(especies_con_nuevas), detalle
    
    def guardar_imagen_validada(self, imagen, nombre_especie, session_id, correcto=True):
        """
        Guarda una imagen validada por el usuario
        
        Args:
            imagen: Imagen a guardar (PIL, numpy, etc.)
            nombre_especie: Nombre de la especie
            session_id: ID de la sesión del usuario
            correcto: Si la predicción fue correcta
        
        Returns:
            dict: Información sobre el guardado
        """
        try:
            # Crear directorio de la especie si no existe
            carpeta_especie = self.plantas_dir / nombre_especie
            carpeta_especie.mkdir(exist_ok=True)
            
            # Generar nombre único para la imagen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status = "correct" if correcto else "corrected"
            nombre_archivo = f"user_{session_id}_{timestamp}_{status}.jpg"
            
            ruta_archivo = carpeta_especie / nombre_archivo
            
            # Convertir imagen a formato guardable
            if isinstance(imagen, Image.Image):
                imagen_pil = imagen
            elif isinstance(imagen, np.ndarray):
                # Convertir de numpy a PIL
                if imagen.dtype == np.float32 or imagen.dtype == np.float64:
                    imagen = (imagen * 255).astype(np.uint8)
                imagen_pil = Image.fromarray(imagen)
            else:
                raise ValueError(f"Tipo de imagen no soportado: {type(imagen)}")
            
            # Guardar imagen
            imagen_pil.save(ruta_archivo, "JPEG", quality=MODEL_CONFIG.get("image_quality", 85))
            
            resultado = {
                "status": "guardada",
                "archivo": nombre_archivo,
                "ruta": str(ruta_archivo),
                "especie": nombre_especie,
                "timestamp": timestamp
            }
            
            print(f"✅ Imagen guardada: {ruta_archivo}")
            return resultado
            
        except Exception as e:
            print(f"❌ Error guardando imagen: {e}")
            return {"status": "error", "mensaje": str(e)}
    
    def validar_estructura_dataset(self):
        """
        Valida que la estructura del dataset sea correcta
        
        Returns:
            dict: Información detallada sobre la validación
        """
        validacion = {
            "es_valido": True,
            "errores": [],
            "advertencias": [],
            "estadisticas": {}
        }
        
        if not self.plantas_dir.exists():
            validacion["es_valido"] = False
            validacion["errores"].append(f"Directorio no existe: {self.plantas_dir}")
            return validacion
        
        carpetas = [d for d in self.plantas_dir.iterdir() if d.is_dir()]
        
        if len(carpetas) == 0:
            validacion["es_valido"] = False
            validacion["errores"].append("No se encontraron carpetas de especies")
            return validacion
        
        total_imagenes = 0
        especies_sin_imagenes = []
        especies_pocas_imagenes = []
        
        for carpeta in carpetas:
            imagenes = self._obtener_imagenes_carpeta(carpeta)
            total_imagenes += len(imagenes)
            
            if len(imagenes) == 0:
                especies_sin_imagenes.append(carpeta.name)
            elif len(imagenes) == 1:
                especies_pocas_imagenes.append(carpeta.name)
        
        # Registrar problemas
        if especies_sin_imagenes:
            validacion["advertencias"].extend([f"Sin imágenes: {esp}" for esp in especies_sin_imagenes])
        
        if especies_pocas_imagenes:
            validacion["advertencias"].extend([f"Solo 1 imagen: {esp}" for esp in especies_pocas_imagenes])
        
        # Estadísticas
        validacion["estadisticas"] = {
            "total_especies": len(carpetas),
            "total_imagenes": total_imagenes,
            "promedio_por_especie": total_imagenes / len(carpetas) if carpetas else 0,
            "especies_sin_imagenes": len(especies_sin_imagenes),
            "especies_con_pocas_imagenes": len(especies_pocas_imagenes)
        }
        
        return validacion

# Funciones de conveniencia para usar desde otros módulos
def procesar_imagen_simple(imagen):
    """Función simple para procesar una imagen"""
    processor = ImageProcessor()
    return processor.procesar_para_prediccion(imagen)

def obtener_estadisticas_dataset():
    """Función simple para obtener estadísticas del dataset"""
    dataset_manager = DatasetManager()
    
    # Validar estructura
    validacion = dataset_manager.validar_estructura_dataset()
    
    # Contar imágenes nuevas
    nuevas_total, especies_nuevas, detalle_nuevas = dataset_manager.contar_imagenes_nuevas()
    
    # Contar por especie
    conteo_especies = dataset_manager.contar_imagenes_por_especie()
    
    return {
        "validacion": validacion,
        "imagenes_nuevas": {
            "total": nuevas_total,
            "especies_afectadas": especies_nuevas,
            "detalle": detalle_nuevas
        },
        "conteo_por_especie": conteo_especies
    }

if __name__ == "__main__":
    # Si ejecutas este archivo directamente, muestra estadísticas
    print("🔍 ANÁLISIS DEL DATASET")
    print("=" * 50)
    
    stats = obtener_estadisticas_dataset()
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    val = stats["validacion"]
    if val["es_valido"]:
        print(f"   ✅ Dataset válido")
        est = val["estadisticas"]
        print(f"   📁 Especies: {est['total_especies']}")
        print(f"   🖼️  Total imágenes: {est['total_imagenes']}")
        print(f"   📈 Promedio por especie: {est['promedio_por_especie']:.1f}")
    else:
        print(f"   ❌ Problemas encontrados:")
        for error in val["errores"]:
            print(f"      - {error}")
    
    print(f"\n🆕 IMÁGENES NUEVAS (validadas por usuarios):")
    nuevas = stats["imagenes_nuevas"]
    print(f"   📊 Total: {nuevas['total']}")
    print(f"   🌿 Especies afectadas: {nuevas['especies_afectadas']}")
    
    if nuevas["detalle"]:
        print(f"   📝 Detalle por especie:")
        for especie, cantidad in list(nuevas["detalle"].items())[:5]:
            print(f"      - {especie}: {cantidad} imágenes")
        if len(nuevas["detalle"]) > 5:
            print(f"      ... y {len(nuevas['detalle']) - 5} especies más")