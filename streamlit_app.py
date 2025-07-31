# streamlit_app.py - VERSIÓN CON INFORMACIÓN DE FIREBASE
# Actualizado para mostrar información rica desde Firestore

import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from datetime import datetime
import json
import time

# ==================== CONFIGURACIÓN DE LA PÁGINA ====================
st.set_page_config(
    page_title="🌱 BucaraFlora - ONNX Runtime",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== CONFIGURACIÓN SIMPLIFICADA ====================
CONFIG = {
    "onnx_model_path": "model/plant_classifier.onnx",
    "species_path": "model/species_list.json",
    "target_size": (224, 224),
    "max_file_size_mb": 10,
    "top_predictions": 5
}

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        color: #2E8B57;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .info-section {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
    }
    
    .confidence-bar {
        background: #e9ecef;
        border-radius: 10px;
        height: 20px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .confidence-fill {
        background: linear-gradient(90deg, #28a745, #20c997);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    .performance-badge {
        background: #17a2b8;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .firebase-info {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES DE CARGA DEL MODELO ====================

@st.cache_resource
def load_onnx_model():
    """Carga el modelo ONNX - Ultra rápido y eficiente"""
    try:
        import onnxruntime as ort
        
        model_path = CONFIG["onnx_model_path"]
        
        if not Path(model_path).exists():
            st.error(f"❌ Modelo ONNX no encontrado: {model_path}")
            st.info("💡 Asegúrate de ejecutar step2_convert_model.py primero")
            return None
        
        # Configurar sesión ONNX con optimizaciones
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        session = ort.InferenceSession(model_path, session_options)
        
        return session
        
    except ImportError:
        st.error("❌ ONNX Runtime no está instalado")
        st.info("💡 Instala con: pip install onnxruntime")
        return None
    except Exception as e:
        st.error(f"❌ Error cargando modelo ONNX: {e}")
        return None

@st.cache_data
def load_species_list():
    """Carga la lista de especies"""
    try:
        species_path = CONFIG["species_path"]
        
        if not Path(species_path).exists():
            st.error(f"❌ Lista de especies no encontrada: {species_path}")
            return []
        
        with open(species_path, 'r', encoding='utf-8') as f:
            species_list = json.load(f)
        
        return species_list
        
    except Exception as e:
        st.error(f"❌ Error cargando especies: {e}")
        return []

# ==================== NUEVA FUNCIÓN: INFORMACIÓN DE FIREBASE ====================

@st.cache_data(ttl=300)  # Cache por 5 minutos
# ==================== FIREBASE ARREGLADO PARA STREAMLIT ====================

def get_plant_info_from_firebase(species_name):
    """Obtiene información rica de la planta desde Firebase - VERSIÓN ARREGLADA"""
    try:
        # Importar la nueva función optimizada para Streamlit
        from utils.firebase_streamlit import get_plant_info_complete
        
        # Obtener información usando la función optimizada
        plant_info = get_plant_info_complete(species_name)
        
        return plant_info
        
    except ImportError:
        st.warning("⚠️ Firebase Streamlit no está configurado")
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
            "fuente_datos": "Sin conexión Firebase"
        }
    except Exception as e:
        st.error(f"❌ Error obteniendo info de Firebase: {e}")
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

# ==================== FUNCIONES DE PROCESAMIENTO ====================

def preprocess_image(image):
    """Procesa la imagen para el modelo ONNX"""
    try:
        # Redimensionar manteniendo aspecto
        img = image.resize(CONFIG["target_size"], Image.Resampling.LANCZOS)
        
        # Convertir a array numpy y normalizar
        img_array = np.array(img, dtype=np.float32) / 255.0
        
        # Agregar dimensión batch
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
        
    except Exception as e:
        st.error(f"❌ Error procesando imagen: {e}")
        return None

def predict_with_onnx(session, image_array, species_list, top_k=5):
    """Realiza predicción ultra-rápida con ONNX Runtime"""
    try:
        # Obtener nombres de entrada y salida
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        
        # Hacer predicción
        start_time = time.time()
        predictions = session.run([output_name], {input_name: image_array})[0][0]
        inference_time = time.time() - start_time
        
        # Obtener top-k índices
        top_indices = np.argsort(predictions)[::-1][:top_k]
        
        # Crear lista de resultados
        results = []
        for idx in top_indices:
            if idx < len(species_list):  # Verificar índice válido
                results.append({
                    "species": species_list[idx],
                    "confidence": float(predictions[idx]),
                    "percentage": int(predictions[idx] * 100),
                    "index": int(idx)
                })
        
        return results, inference_time
        
    except Exception as e:
        st.error(f"❌ Error en predicción ONNX: {e}")
        return [], 0

def format_species_name(species_name):
    """Formatea nombre científico para mostrar"""
    try:
        # Reemplazar guiones bajos con espacios
        formatted = species_name.replace('_', ' ')
        
        # Extraer género y especie
        parts = formatted.split(' ')
        if len(parts) >= 2:
            genus = parts[0]
            species_epithet = parts[1]
            
            # Si hay más partes (autoridad, etc.), incluirlas
            if len(parts) > 2:
                authority = ' '.join(parts[2:])
                return f"*{genus} {species_epithet}* {authority}"
            else:
                # Solo género y especie
                return f"*{genus} {species_epithet}*"
        
        return formatted
    except:
        return species_name

def display_plant_information(plant_info):
    """Muestra información rica de la planta"""
    
    # Título principal con nombre común
    st.markdown(f"### 🌿 {plant_info['nombre_comun']}")
    
    # Nombre científico
    scientific_name = format_species_name(plant_info['nombre_cientifico'])
    st.markdown(f"**Nombre científico:** {scientific_name}")
    
    # Información taxonómica
    if plant_info['familia']:
        st.markdown(f"**Familia:** {plant_info['familia']}")
    
    # Descripción
    if plant_info['descripcion']:
        st.markdown(f"**Descripción:** {plant_info['descripcion']}")
    
    # Información adicional en secciones expandibles
    if plant_info['found']:
        # Taxonomía completa
        taxonomia = plant_info.get('taxonomia', {})
        if taxonomia and any(taxonomia.values()):
            with st.expander("🔬 Clasificación taxonómica"):
                cols = st.columns(2)
                
                with cols[0]:
                    if taxonomia.get('reino'):
                        st.write(f"**Reino:** {taxonomia['reino']}")
                    if taxonomia.get('filo'):
                        st.write(f"**Filo:** {taxonomia['filo']}")
                    if taxonomia.get('clase'):
                        st.write(f"**Clase:** {taxonomia['clase']}")
                    if taxonomia.get('orden'):
                        st.write(f"**Orden:** {taxonomia['orden']}")
                
                with cols[1]:
                    if taxonomia.get('familia'):
                        st.write(f"**Familia:** {taxonomia['familia']}")
                    if taxonomia.get('genero'):
                        st.write(f"**Género:** {taxonomia['genero']}")
                    if taxonomia.get('especie'):
                        st.write(f"**Especie:** {taxonomia['especie']}")
        
        # Información adicional
        if plant_info.get('origen') or plant_info.get('fuente'):
            with st.expander("📋 Información adicional"):
                if plant_info.get('origen'):
                    st.write(f"**Fecha de observación:** {plant_info['origen']}")
                if plant_info.get('fuente'):
                    st.write(f"**Fuente:** {plant_info['fuente']}")
    
    # Badge de fuente de datos
    fuente_color = "#28a745" if plant_info['found'] else "#6c757d"
    st.markdown(f"""
    <div style="text-align: right; margin-top: 1rem;">
        <span style="background: {fuente_color}; color: white; padding: 0.25rem 0.5rem; 
                     border-radius: 12px; font-size: 0.75rem;">
            📊 {plant_info['fuente_datos']}
        </span>
    </div>
    """, unsafe_allow_html=True)

# ==================== INTERFAZ PRINCIPAL ====================

def show_performance_info(inference_time):
    """Muestra información de rendimiento"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="performance-badge">
            ⚡ {inference_time*1000:.1f}ms
        </div>
        """, unsafe_allow_html=True)
        st.caption("Tiempo de inferencia")
    
    with col2:
        st.markdown(f"""
        <div class="performance-badge">
            🚀 ONNX Runtime
        </div>
        """, unsafe_allow_html=True)
        st.caption("Motor de IA")
    
    with col3:
        st.markdown(f"""
        <div class="performance-badge">
            🌿 335 especies
        </div>
        """, unsafe_allow_html=True)
        st.caption("Base de datos")

def main():
    """Función principal de la aplicación"""
    
    # Header principal
    st.markdown('<h1 class="main-header">🌱 BucaraFlora - IA con Firebase</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 1rem;">
            <strong>Identificador de plantas con información rica desde Firebase</strong>
        </p>
        <span class="performance-badge">🔥 Powered by ONNX Runtime + Firebase Firestore</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar modelo y especies
    with st.spinner("🔄 Cargando modelo optimizado..."):
        session = load_onnx_model()
        species_list = load_species_list()
    
    # Verificar que todo esté cargado
    if session is None:
        st.error("❌ No se pudo cargar el modelo ONNX")
        st.info("💡 Ejecuta step2_convert_model.py para generar el modelo ONNX")
        return
    
    if not species_list:
        st.error("❌ No se pudo cargar la lista de especies")
        return
    
    # Mostrar estado del sistema
    st.success(f"✅ Sistema listo: Modelo ONNX cargado con {len(species_list)} especies")
    
    # Test de Firebase en sidebar
    with st.sidebar:
        st.markdown("### 🔥 Estado Firebase")
        try:
            from utils.firebase_streamlit import initialize_firebase
        
        # Verificar conexión usando nuestra función optimizada
            db = initialize_firebase()
        
            if db:
                st.markdown("🟢 **Conectado**")
                st.markdown("Proyecto: `bucaraflora-f0161`")
                st.markdown("Colección: `planta`")
            else:
                st.markdown("🔴 **Error de conexión**")
            
        except Exception as e:
            st.markdown("🟡 **Error en verificación**")
            st.caption(f"Error: {str(e)[:50]}...")
        
        st.markdown("### 🤖 Información del Modelo")
        st.markdown("- **Motor:** ONNX Runtime")
        st.markdown("- **Especies:** 335")
        st.markdown("- **Precisión:** Idéntica a TensorFlow")
        st.markdown("- **Velocidad:** 100x+ más rápido")
        st.markdown("- **Tamaño:** 55% más pequeño")
        st.markdown("- **Python:** 3.13 compatible ✅")
    
    # Área principal de upload
    st.markdown("### 📸 Sube una foto de tu planta")
    
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=['jpg', 'jpeg', 'png'],
        help=f"Formatos: JPG, JPEG, PNG. Máximo {CONFIG['max_file_size_mb']}MB."
    )
    
    if uploaded_file is not None:
        # Validar tamaño
        if uploaded_file.size > CONFIG['max_file_size_mb'] * 1024 * 1024:
            st.error(f"❌ Archivo muy grande. Máximo {CONFIG['max_file_size_mb']}MB.")
            return
        
        try:
            # Cargar y mostrar imagen
            image = Image.open(uploaded_file).convert('RGB')
            
            # Mostrar imagen centrada
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(image, caption="Tu planta", use_container_width=True)
            
            # Botón de análisis
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔍 Identificar con IA", type="primary", use_container_width=True):
                    
                    with st.spinner("🧠 Analizando con IA ultra-rápida..."):
                        # Procesar imagen
                        processed_image = preprocess_image(image)
                        
                        if processed_image is not None:
                            # Hacer predicción
                            predictions, inference_time = predict_with_onnx(
                                session, processed_image, species_list, 
                                top_k=CONFIG['top_predictions']
                            )
                            
                            if predictions:
                                # Mostrar información de rendimiento
                                show_performance_info(inference_time)
                                
                                # Resultado principal
                                best_prediction = predictions[0]
                                
                                st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
                                
                                # ===== NUEVA FUNCIONALIDAD: INFORMACIÓN DE FIREBASE =====
                                with st.spinner("🔥 Obteniendo información desde Firebase..."):
                                    plant_info = get_plant_info_from_firebase(best_prediction['species'])
                                
                                # Mostrar información rica de la planta
                                display_plant_information(plant_info)
                                
                                # Barra de confianza visual
                                confidence_pct = best_prediction['percentage']
                                st.markdown(f"""
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: {confidence_pct}%;"></div>
                                </div>
                                <p style="text-align: center; font-weight: bold; margin: 0.5rem 0;">
                                    Confianza: {confidence_pct}%
                                </p>
                                """, unsafe_allow_html=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Mostrar alternativas si hay más predicciones
                                if len(predictions) > 1:
                                    st.markdown("### 🤔 Otras posibilidades:")
                                    
                                    for i, pred in enumerate(predictions[1:], 2):
                                        # Obtener información de Firebase para alternativas
                                        alt_info = get_plant_info_from_firebase(pred['species'])
                                        
                                        with st.expander(f"{i}. {alt_info['nombre_comun']} - {pred['percentage']}%"):
                                            st.markdown(f"**Nombre científico:** {format_species_name(alt_info['nombre_cientifico'])}")
                                            st.markdown(f"**Confianza:** {pred['percentage']}%")
                                            if alt_info['familia']:
                                                st.markdown(f"**Familia:** {alt_info['familia']}")
                                            st.markdown(f"**Descripción:** {alt_info['descripcion'][:200]}...")
                                
                                # Mensaje de éxito
                                st.success("🎉 ¡Identificación completada con información de Firebase!")
                                st.balloons()
                                
                                # Información técnica
                                with st.expander("📊 Información técnica"):
                                    st.markdown(f"- **Tiempo de inferencia:** {inference_time*1000:.2f}ms")
                                    st.markdown(f"- **Motor de IA:** ONNX Runtime")
                                    st.markdown(f"- **Base de datos:** Firebase Firestore")
                                    st.markdown(f"- **Modelo:** 335 especies colombianas")
                                    st.markdown(f"- **Arquitectura:** MobileNetV2 optimizada")
                                    st.markdown(f"- **Index de clase:** {best_prediction['index']}")
                                    st.markdown(f"- **Información encontrada:** {'✅ Sí' if plant_info['found'] else '❌ No'}")
                                
                                # Botón para nueva consulta
                                if st.button("🔄 Identificar otra planta", use_container_width=True):
                                    st.rerun()
                                
                            else:
                                st.error("❌ No se pudo realizar la predicción")
                        else:
                            st.error("❌ Error procesando la imagen")
                            
        except Exception as e:
            st.error(f"❌ Error cargando imagen: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🌱 BucaraFlora - Identificador de Plantas con IA<br>
        🔥 Optimizado con ONNX Runtime + Firebase Firestore
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()