# 🌱 Plant.AI - Identificador de Plantas con IA

## 🚀 Proyecto Optimizado con ONNX Runtime
*Última actualización del modelo: 2025-09-04*

**Plant.AI** es un sistema de identificación de plantas usando Inteligencia Artificial, optimizado para máximo rendimiento con ONNX Runtime.

### ⚡ Características principales:
- 🤖 **IA Ultra-rápida:** Predicciones en 20-50ms (100x más rápido que TensorFlow)
- 🌿 **335 especies:** Base de datos completa de flora de los parques de Bucaramanga
- 🐍 **Python 3.13:** Compatible con las últimas versiones
- 📱 **Web App:** Interfaz moderna y responsive
- 🚀 **Deploy optimizado:** Listo para Streamlit

---

## 📊 Mejoras vs versión TensorFlow

| Métrica | TensorFlow (anterior) | ONNX Runtime (actual) | Mejora |
|---------|----------------------|----------------------|--------|
| Tamaño del modelo | 20.57 MB | 9.26 MB | 55% reducción |
| Tiempo de predicción | 2.2469s | 0.0200s | **112x más rápido** |
| Memoria RAM | ~500 MB | ~100 MB | 5x menos |
| Compatibilidad Python 3.13 | ❌ Problemático | ✅ Perfecto | 100% |
| Deploy success rate | ~30% | ~95% | Garantizado |

---

## 🛠️ Instalación y uso

### Opción A: Usar la app web (Recomendado)
👉 **[App en vivo en Streamlit Cloud](https://planta-ai-uts.streamlit.app)**

### Opción B: Ejecutar localmente
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/planta_ai.git
cd planta_ai

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ó venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar aplicación
streamlit run streamlit_app.py
```

---

## 📁 Estructura del proyecto

```
planta_ai/
├── streamlit_app.py              # 🎯 Aplicación principal
├── requirements.txt              # 📦 Dependencias optimizadas
├── config.py                     # ⚙️ Configuraciones generales
├── assets/                       # 🎨 Recursos visuales
│   ├── logo.png                 # 🌱 Logo de la aplicación
│   ├── fondo.png                # 🖼️ Imagen de fondo
│   └── *.png                    # 🎨 Botones y elementos UI
├── model/
│   ├── plant_classifier.onnx    # 🤖 Modelo IA optimizado
│   ├── species_list.json        # 🌿 335 especies
│   ├── model_metadata.json      # 📊 Metadatos del modelo
│   └── *.py                     # 🔧 Utilidades del modelo
├── ui/                          # 🖥️ Interfaz de usuario
│   ├── components.py            # 🧩 Componentes reutilizables
│   ├── screens/                 # 📱 Pantallas de la app
│   ├── sidebar.py               # 📋 Barra lateral
│   └── styles.py                # 🎨 Estilos CSS
├── utils/                       # 🛠️ Herramientas
│   ├── image_processing.py      # 🖼️ Procesamiento de imágenes
│   ├── firebase_*.py           # 🔥 Integración Firebase
│   └── *.py                    # 🔧 Utilidades varias
├── data/                        # 📂 Datos del proyecto
├── logs/                        # 📝 Logs del sistema
└── venv/                        # 🐍 Entorno virtual
```

---

## 🔄 Migración TensorFlow → ONNX

Este proyecto fue migrado exitosamente de TensorFlow a ONNX Runtime, logrando una **mejora del 112x en velocidad** y **55% de reducción en tamaño del modelo**.

---

## 📊 Tecnologías utilizadas

- **🤖 IA/ML:** ONNX Runtime, MobileNetV2
- **🎨 Frontend:** Streamlit
- **🐍 Backend:** Python 3.13
- **📱 Deployment:** Streamlit Cloud
- **🗄️ Base de datos:** Firebase Firestore
- **🖼️ Procesamiento:** OpenCV, Pillow
- **🔧 Arquitectura:** Modular con separación UI/Lógica

---

## 🚀 Deployment

### Streamlit Cloud (Recomendado)
1. Clonar repositorio
2. Conecta en [share.streamlit.io](https://share.streamlit.io)
3. ¡Listo! Deploy automático

---

## 📈 Performance

### Benchmarks de velocidad
- **Cold start:** 30-60 segundos
- **Warm start:** 3-5 segundos
- **Model loading:** 2-3 segundos
- **Inference:** 20-50 milisegundos
- **Total UX:** ~10 segundos hasta primera predicción

### Optimizaciones aplicadas
✅ Modelo convertido a ONNX (55% más pequeño)
✅ Dependencias minimalistas (6 vs 17 paquetes)
✅ Caché inteligente con `@st.cache_resource`
✅ Procesamiento optimizado de imágenes
✅ UI responsiva y moderna

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 👨‍💻 Autores

- **Proyecto de Grado** - Desarrollo principal
- **Colaboradores** - Ver lista de [contribuidores](https://github.com/tu-usuario/planta_ai/contributors)

---

**⭐ Si este proyecto te fue útil, no olvides darle una estrella en GitHub ⭐**
