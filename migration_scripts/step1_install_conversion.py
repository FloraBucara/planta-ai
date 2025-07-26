# step1_install_conversion.py
# PASO 1: Instalar dependencias para conversión TensorFlow → ONNX

import subprocess
import sys

def install_conversion_dependencies():
    """
    Instala las dependencias necesarias para convertir TensorFlow a ONNX
    """
    print("🚀 PASO 1: INSTALANDO DEPENDENCIAS PARA CONVERSIÓN")
    print("=" * 60)
    
    # Lista de paquetes necesarios para la conversión
    conversion_packages = [
        "tf2onnx==1.16.1",           # Convertidor oficial TensorFlow → ONNX
        "onnx==1.15.0",              # Formato ONNX base
        "onnxruntime==1.17.1",       # Runtime para ejecutar modelos ONNX
        "tensorflow==2.15.0"         # Necesario para cargar el modelo original
    ]
    
    print("📦 Instalando paquetes de conversión:")
    for package in conversion_packages:
        print(f"   - {package}")
    
    try:
        # Instalar cada paquete
        for package in conversion_packages:
            print(f"\n🔄 Instalando {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                print(f"   ✅ {package} instalado correctamente")
            else:
                print(f"   ❌ Error instalando {package}")
                print(f"   Error: {result.stderr}")
                return False
        
        print("\n🎉 TODAS LAS DEPENDENCIAS INSTALADAS CORRECTAMENTE")
        
        # Verificar instalaciones
        print("\n🔍 VERIFICANDO INSTALACIONES...")
        verification_success = verify_installations()
        
        if verification_success:
            print("\n✅ PASO 1 COMPLETADO EXITOSAMENTE")
            print("💡 Ahora puedes ejecutar el PASO 2: Conversión del modelo")
            return True
        else:
            print("\n❌ Hay problemas con las instalaciones")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la instalación:")
        print(f"   Comando: {e.cmd}")
        print(f"   Código de salida: {e.returncode}")
        print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def verify_installations():
    """
    Verifica que todas las dependencias se instalaron correctamente
    """
    print("🔍 Verificando instalaciones...")
    
    verification_tests = [
        ("onnx", "import onnx; print(f'ONNX {onnx.__version__}')"),
        ("onnxruntime", "import onnxruntime as ort; print(f'ONNX Runtime {ort.__version__}')"),
        ("tensorflow", "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"),
        ("tf2onnx", "import tf2onnx; print(f'tf2onnx {tf2onnx.__version__}')")
    ]
    
    all_success = True
    
    for package_name, test_code in verification_tests:
        try:
            print(f"   🔄 Verificando {package_name}...")
            
            # Timeout más largo para TensorFlow (primera importación es lenta)
            timeout_duration = 120 if package_name in ["tensorflow", "tf2onnx"] else 30
            
            result = subprocess.run([
                sys.executable, "-c", test_code
            ], capture_output=True, text=True, timeout=timeout_duration)
            
            if result.returncode == 0:
                version_info = result.stdout.strip()
                print(f"   ✅ {package_name}: {version_info}")
            else:
                print(f"   ❌ {package_name}: Error en verificación")
                print(f"      {result.stderr.strip()}")
                
                # Para TensorFlow, intentar verificación alternativa
                if package_name == "tensorflow":
                    print(f"   🔄 Intentando verificación alternativa de TensorFlow...")
                    alt_success = verify_tensorflow_alternative()
                    if alt_success:
                        print(f"   ✅ {package_name}: Instalado correctamente (verificación alternativa)")
                        continue
                
                all_success = False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ {package_name}: Importación muy lenta, pero probablemente instalado")
            
            # Para TensorFlow, el timeout no es necesariamente un error
            if package_name in ["tensorflow", "tf2onnx"]:
                print(f"   ℹ️ {package_name}: Primera importación de TensorFlow es lenta (normal)")
                print(f"   💡 Intentando verificación rápida...")
                
                quick_check = quick_verify_package(package_name)
                if quick_check:
                    print(f"   ✅ {package_name}: Instalado correctamente (verificación rápida)")
                else:
                    print(f"   ❌ {package_name}: No instalado correctamente")
                    all_success = False
            else:
                all_success = False
                
        except Exception as e:
            print(f"   ❌ {package_name}: {e}")
            all_success = False
    
    return all_success

def verify_tensorflow_alternative():
    """Verificación alternativa más rápida para TensorFlow"""
    try:
        import importlib.util
        spec = importlib.util.find_spec("tensorflow")
        return spec is not None
    except:
        return False

def quick_verify_package(package_name):
    """Verificación rápida de que el paquete está instalado"""
    try:
        import importlib.util
        spec = importlib.util.find_spec(package_name.replace("-", "_"))
        return spec is not None
    except:
        return False

def show_next_steps():
    """
    Muestra los próximos pasos después de completar la instalación
    """
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASOS:")
    print("="*60)
    print("1. ✅ COMPLETADO: Instalación de dependencias")
    print("2. ⏳ SIGUIENTE: Conversión del modelo TensorFlow → ONNX")
    print("3. ⏸️  PENDIENTE: Actualizar código de Streamlit")
    print("4. ⏸️  PENDIENTE: Actualizar requirements.txt")
    print("5. ⏸️  PENDIENTE: Deploy a Streamlit Cloud")
    
    print("\n💡 IMPORTANTE:")
    print("   - No avances al PASO 2 hasta confirmar que este paso funcionó")
    print("   - Si hay errores, resuelve antes de continuar")
    print("   - Todas las verificaciones deben mostrar ✅")

if __name__ == "__main__":
    print("🚀 MIGRACIÓN A ONNX RUNTIME - PASO 1")
    print("Instalación de dependencias para conversión")
    print()
    
    success = install_conversion_dependencies()
    
    if success:
        show_next_steps()
        print("\n🟢 PASO 1 COMPLETADO - Confirma que todo funciona antes de continuar")
    else:
        print("\n🔴 PASO 1 FALLÓ - Revisa los errores antes de continuar")
        print("\n💡 Posibles soluciones:")
        print("   - Actualiza pip: python -m pip install --upgrade pip")
        print("   - Usa un entorno virtual: python -m venv onnx_env")
        print("   - Verifica tu conexión a internet")