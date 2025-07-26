import tensorflow as tf

# Imports más compatibles para evitar errores de Pylance
try:
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.applications import MobileNetV2, EfficientNetB0
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
except ImportError:
    # Fallback para versiones más antiguas
    import keras
    from keras import layers
    from keras.applications import MobileNetV2, EfficientNetB0
    from keras.optimizers import Adam
    from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))
from config import MODEL_CONFIG, PATHS, RETRAINING_CONFIG, LOGS_DIR
from utils.image_processing import DatasetManager

class PlantModelTrainer:
    """Clase para entrenar y gestionar el modelo de clasificación de plantas"""
    
    def __init__(self):
        self.model = None
        self.history = None
        self.dataset_manager = DatasetManager()
        self.num_classes = None
        self.species_names = None
        
        # Configurar GPU si está disponible
        self._configurar_gpu()
    
    def _configurar_gpu(self):
        """Configura el uso de GPU si está disponible"""
        try:
            # Verificar GPUs disponibles
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                print(f"✅ GPU encontrada: {len(gpus)} dispositivo(s)")
                # Configurar memoria dinámica para evitar errores
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            else:
                print("⚠️ No se encontró GPU, usando CPU")
        except Exception as e:
            print(f"❌ Error configurando GPU: {e}")
    
    def crear_modelo(self, num_classes):
        """
        Crea el modelo usando Transfer Learning
        
        Args:
            num_classes: Número de especies/clases
        
        Returns:
            Modelo compilado
        """
        print(f"🏗️ Creando modelo para {num_classes} especies...")
        
        input_shape = MODEL_CONFIG["input_shape"]
        
        # Modelo base pre-entrenado
        if MODEL_CONFIG["base_model"] == "MobileNetV2":
            base_model = MobileNetV2(
                weights='imagenet',
                include_top=False,
                input_shape=input_shape
            )
        elif MODEL_CONFIG["base_model"] == "EfficientNetB0":
            base_model = EfficientNetB0(
                weights='imagenet',
                include_top=False,
                input_shape=input_shape
            )
        else:
            raise ValueError(f"Modelo base no soportado: {MODEL_CONFIG['base_model']}")
        
        # Congelar capas del modelo base inicialmente
        base_model.trainable = not MODEL_CONFIG["freeze_base"]
        
        # Crear el modelo completo
        model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax', name='predictions')
        ])
        
        # Compilar modelo
        model.compile(
            optimizer=Adam(learning_rate=MODEL_CONFIG["learning_rate"]),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.SparseTopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
        )
        
        print(f"✅ Modelo creado con {model.count_params():,} parámetros")
        return model
    
    def preparar_datos(self, incluir_augmentation=True):
        """
        Prepara los datos para entrenamiento
        
        Args:
            incluir_augmentation: Si aplicar data augmentation
        
        Returns:
            tuple: (X_train, X_val, y_train, y_val, species_names)
        """
        print("📊 Preparando datos de entrenamiento...")
        
        # Cargar dataset completo
        X, y, species_names = self.dataset_manager.cargar_dataset_completo(
            incluir_augmentation=incluir_augmentation
        )
        
        self.num_classes = len(species_names)
        self.species_names = species_names
        
        # Dividir en entrenamiento y validación
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, 
            test_size=MODEL_CONFIG["validation_split"],
            random_state=42,
            stratify=y  # Mantener proporción de clases
        )
        
        print(f"📈 Datos preparados:")
        print(f"   - Entrenamiento: {len(X_train)} imágenes")
        print(f"   - Validación: {len(X_val)} imágenes")
        print(f"   - Clases: {self.num_classes}")
        
        return X_train, X_val, y_train, y_val, species_names
    
    def entrenar_modelo(self, X_train, X_val, y_train, y_val, epochs=None):
        """
        Entrena el modelo
        
        Args:
            X_train, X_val, y_train, y_val: Datos de entrenamiento y validación
            epochs: Número de épocas (usa config si es None)
        
        Returns:
            Historia del entrenamiento
        """
        if epochs is None:
            epochs = MODEL_CONFIG["epochs"]
        
        print(f"🚀 Iniciando entrenamiento por {epochs} épocas...")
        
        # Crear modelo si no existe
        if self.model is None:
            self.model = self.crear_modelo(self.num_classes)
        
        # Callbacks para mejorar el entrenamiento
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=str(PATHS["model_file"]),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Entrenar
        self.history = self.model.fit(
            X_train, y_train,
            batch_size=MODEL_CONFIG["batch_size"],
            epochs=epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        print("✅ Entrenamiento completado")
        return self.history
    
    def evaluar_modelo(self, X_val, y_val):
        """
        Evalúa el rendimiento del modelo
        
        Args:
            X_val, y_val: Datos de validación
        
        Returns:
            dict: Métricas de evaluación
        """
        print("📊 Evaluando modelo...")
        
        if self.model is None:
            print("❌ No hay modelo para evaluar")
            return None
        
        # Predicciones
        y_pred_proba = self.model.predict(X_val)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Métricas básicas
        loss, accuracy, top3_accuracy = self.model.evaluate(X_val, y_val, verbose=0)
        
        # Top-5 accuracy manual
        y_pred_proba = self.model.predict(X_val, verbose=0)
        top5_accuracy = tf.keras.metrics.sparse_top_k_categorical_accuracy(
            tf.constant(y_val), tf.constant(y_pred_proba), k=5
        ).numpy().mean()
        
        metricas = {
            "loss": float(loss),
            "accuracy": float(accuracy),
            "top3_accuracy": float(top3_accuracy),
            "top5_accuracy": float(top5_accuracy),
            "total_params": self.model.count_params(),
            "num_classes": self.num_classes
        }
        
        print(f"📈 Resultados:")
        print(f"   - Precisión: {accuracy:.3f}")
        print(f"   - Top-3 Accuracy: {top3_accuracy:.3f}")
        print(f"   - Top-5 Accuracy: {top5_accuracy:.3f}")
        print(f"   - Loss: {loss:.3f}")
        
        return metricas
    
    def guardar_modelo_completo(self, metricas=None):
        """
        Guarda el modelo y metadatos asociados
        
        Args:
            metricas: Métricas de evaluación
        """
        try:
            # Guardar modelo
            self.model.save(PATHS["model_file"])
            print(f"✅ Modelo guardado en: {PATHS['model_file']}")
            
            # Guardar metadatos
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "num_classes": self.num_classes,
                "species_names": self.species_names,
                "model_config": MODEL_CONFIG,
                "metricas": metricas or {}
            }
            
            metadata_file = PATHS["model_file"].parent / "model_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Metadatos guardados en: {metadata_file}")
            
        except Exception as e:
            print(f"❌ Error guardando modelo: {e}")
    
    def crear_backup_modelo_actual(self):
        """Crea un backup del modelo actual antes de reemplazarlo"""
        try:
            if PATHS["model_file"].exists():
                # Copiar modelo actual a backup
                import shutil
                shutil.copy2(PATHS["model_file"], PATHS["backup_model_file"])
                print(f"✅ Backup creado: {PATHS['backup_model_file']}")
                return True
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
        return False
    
    def cargar_modelo_existente(self):
        """Carga un modelo previamente entrenado"""
        try:
            if PATHS["model_file"].exists():
                self.model = keras.models.load_model(PATHS["model_file"])
                
                # Cargar metadatos si existen
                metadata_file = PATHS["model_file"].parent / "model_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    self.num_classes = metadata.get("num_classes")
                    self.species_names = metadata.get("species_names")
                    
                print(f"✅ Modelo cargado: {PATHS['model_file']}")
                print(f"   - Clases: {self.num_classes}")
                return True
            else:
                print(f"⚠️ No se encontró modelo en: {PATHS['model_file']}")
                return False
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False
    
    def fine_tuning(self, X_train, X_val, y_train, y_val):
        """
        Realiza fine-tuning desbloqueando algunas capas del modelo base
        """
        if self.model is None:
            print("❌ No hay modelo base para fine-tuning")
            return None
        
        print("🔧 Iniciando fine-tuning...")
        
        # Desbloquear las últimas capas del modelo base
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Congelar todas las capas excepto las últimas N
        fine_tune_at = len(base_model.layers) - MODEL_CONFIG["fine_tune_layers"]
        
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False
        
        # Recompilar con learning rate más bajo
        self.model.compile(
            optimizer=Adam(learning_rate=MODEL_CONFIG["learning_rate"] / 10),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.SparseTopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
        )
        
        # Entrenar con pocas épocas
        fine_tune_epochs = 10
        
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=5,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-8
            )
        ]
        
        history_fine = self.model.fit(
            X_train, y_train,
            batch_size=MODEL_CONFIG["batch_size"],
            epochs=fine_tune_epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        print("✅ Fine-tuning completado")
        return history_fine
    
    def generar_reporte_entrenamiento(self, metricas, guardar_graficos=True):
        """
        Genera un reporte completo del entrenamiento
        
        Args:
            metricas: Métricas de evaluación
            guardar_graficos: Si guardar gráficos del entrenamiento
        """
        print("📋 Generando reporte de entrenamiento...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear reporte texto
        reporte = f"""
REPORTE DE ENTRENAMIENTO - {timestamp}
{'='*50}

CONFIGURACIÓN:
- Modelo base: {MODEL_CONFIG['base_model']}
- Épocas: {MODEL_CONFIG['epochs']}
- Batch size: {MODEL_CONFIG['batch_size']}
- Learning rate: {MODEL_CONFIG['learning_rate']}

DATASET:
- Especies: {self.num_classes}
- Total parámetros: {metricas.get('total_params', 'N/A'):,}

RESULTADOS:
- Precisión: {metricas.get('accuracy', 0):.3f}
- Top-3 Accuracy: {metricas.get('top3_accuracy', 0):.3f}
- Top-5 Accuracy: {metricas.get('top5_accuracy', 0):.3f}
- Loss: {metricas.get('loss', 0):.3f}

FECHA: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        # Guardar reporte
        reporte_file = LOGS_DIR / f"training_report_{timestamp}.txt"
        with open(reporte_file, 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print(f"✅ Reporte guardado: {reporte_file}")
        
        # Guardar gráficos si hay historia y se solicita
        if self.history is not None and guardar_graficos:
            self._guardar_graficos_entrenamiento(timestamp)
        
        return reporte_file
    
    def _guardar_graficos_entrenamiento(self, timestamp):
        """Guarda gráficos del progreso de entrenamiento"""
        try:
            # Crear figura con subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Progreso del Entrenamiento', fontsize=16)
            
            # Accuracy
            axes[0, 0].plot(self.history.history['accuracy'], label='Training')
            axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation')
            axes[0, 0].set_title('Accuracy')
            axes[0, 0].set_xlabel('Época')
            axes[0, 0].set_ylabel('Accuracy')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
            
            # Loss
            axes[0, 1].plot(self.history.history['loss'], label='Training')
            axes[0, 1].plot(self.history.history['val_loss'], label='Validation')
            axes[0, 1].set_title('Loss')
            axes[0, 1].set_xlabel('Época')
            axes[0, 1].set_ylabel('Loss')
            axes[0, 1].legend()
            axes[0, 1].grid(True)
            
            # Top-3 Accuracy
            if 'top_3_categorical_accuracy' in self.history.history:
                axes[1, 0].plot(self.history.history['top_3_categorical_accuracy'], label='Training')
                axes[1, 0].plot(self.history.history['val_top_3_categorical_accuracy'], label='Validation')
                axes[1, 0].set_title('Top-3 Accuracy')
                axes[1, 0].set_xlabel('Época')
                axes[1, 0].set_ylabel('Top-3 Accuracy')
                axes[1, 0].legend()
                axes[1, 0].grid(True)
            
            # Learning Rate
            if 'lr' in self.history.history:
                axes[1, 1].plot(self.history.history['lr'])
                axes[1, 1].set_title('Learning Rate')
                axes[1, 1].set_xlabel('Época')
                axes[1, 1].set_ylabel('Learning Rate')
                axes[1, 1].set_yscale('log')
                axes[1, 1].grid(True)
            
            # Guardar gráfico
            grafico_file = LOGS_DIR / f"training_plots_{timestamp}.png"
            plt.tight_layout()
            plt.savefig(grafico_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráficos guardados: {grafico_file}")
            
        except Exception as e:
            print(f"❌ Error guardando gráficos: {e}")

def entrenar_modelo_completo(incluir_fine_tuning=True):
    """
    Función principal para entrenar un modelo completo desde cero
    
    Args:
        incluir_fine_tuning: Si realizar fine-tuning después del entrenamiento inicial
    
    Returns:
        dict: Resultados del entrenamiento
    """
    print("🚀 INICIANDO ENTRENAMIENTO COMPLETO")
    print("="*50)
    
    # Crear entrenador
    trainer = PlantModelTrainer()
    
    try:
        # 1. Preparar datos
        X_train, X_val, y_train, y_val, species_names = trainer.preparar_datos(
            incluir_augmentation=True
        )
        
        # 2. Crear y entrenar modelo
        trainer.entrenar_modelo(X_train, X_val, y_train, y_val)
        
        # 3. Fine-tuning si se solicita
        if incluir_fine_tuning:
            trainer.fine_tuning(X_train, X_val, y_train, y_val)
        
        # 4. Evaluar modelo final
        metricas = trainer.evaluar_modelo(X_val, y_val)
        
        # 5. Guardar modelo
        trainer.guardar_modelo_completo(metricas)
        
        # 6. Generar reporte
        reporte_file = trainer.generar_reporte_entrenamiento(metricas)
        
        resultado = {
            "status": "exitoso",
            "metricas": metricas,
            "reporte_file": str(reporte_file),
            "model_file": str(PATHS["model_file"])
        }
        
        print("🎉 ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        return resultado
        
    except Exception as e:
        print(f"❌ ERROR EN ENTRENAMIENTO: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    # Si ejecutas este archivo directamente, entrena el modelo
    print("🤖 ENTRENAMIENTO DEL MODELO DE PLANTAS")
    print("="*50)
    
    # Verificar que existe el dataset
    from utils.image_processing import obtener_estadisticas_dataset
    
    stats = obtener_estadisticas_dataset()
    
    if not stats["validacion"]["es_valido"]:
        print("❌ Dataset no válido. Corrige los errores antes de entrenar:")
        for error in stats["validacion"]["errores"]:
            print(f"   - {error}")
        sys.exit(1)
    
    print("✅ Dataset validado. Iniciando entrenamiento...")
    
    # Entrenar modelo
    resultado = entrenar_modelo_completo(incluir_fine_tuning=True)
    
    if resultado["status"] == "exitoso":
        print(f"\n🎯 MODELO ENTRENADO:")
        print(f"   📁 Archivo: {resultado['model_file']}")
        print(f"   📊 Precisión: {resultado['metricas']['accuracy']:.3f}")
        print(f"   📋 Reporte: {resultado['reporte_file']}")
    else:
        print(f"\n❌ ERROR: {resultado['error']}")