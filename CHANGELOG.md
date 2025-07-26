# Changelog

## [2.0.0] - 2025-07-25 - MIGRACIÓN A ONNX RUNTIME

### 🚀 Added
- ONNX Runtime para predicciones ultra-rápidas
- Compatibilidad completa con Python 3.13
- Interface de usuario mejorada con métricas de rendimiento
- Sistema de badges de performance en tiempo real
- Configuración optimizada para Streamlit Cloud

### ⚡ Changed
- **BREAKING:** Reemplazado TensorFlow con ONNX Runtime
- Reducido requirements.txt de 17 a 6 dependencias
- Mejorado tiempo de inferencia de 2.2s a 0.02s (112x más rápido)
- Reducido tamaño de modelo de 20.57MB a 9.26MB (55% menos)
- Optimizado uso de memoria de ~500MB a ~100MB

### 🔧 Fixed
- Problemas de compatibilidad con Python 3.13
- Timeouts en Streamlit Cloud
- Errores de memoria durante deployment
- Carga lenta del modelo

### 📦 Dependencies
- Added: onnxruntime==1.17.1
- Added: opencv-python-headless==4.9.0.80
- Removed: tensorflow==2.15.0
- Removed: tf2onnx==1.16.1 (solo para conversión)
- Updated: streamlit==1.32.0

## [1.0.0] - 2025-07-14 - VERSIÓN TENSORFLOW ORIGINAL

### 🌱 Added
- Sistema de identificación de 335 especies de plantas
- Modelo basado en MobileNetV2 con Transfer Learning
- Interface web con Streamlit
- Integración con Firebase Firestore
- API REST con Flask
- Sistema de reentrenamiento automático
