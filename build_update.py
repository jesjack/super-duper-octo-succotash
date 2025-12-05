"""
Script para construir paquetes de actualización en USB
Uso: python build_update.py <letra_unidad_usb> [nueva_version]
Ejemplo: python build_update.py E: 1.0.1
         python build_update.py E:  (auto-incrementa versión)
"""

import os
import sys
import shutil
import subprocess
import json
import hashlib
from pathlib import Path
from datetime import datetime
import version

def parse_version(v):
    """Parse version string to tuple"""
    return tuple(int(x) for x in v.split('.'))

def increment_patch(v):
    """Incrementa el número patch de la versión"""
    major, minor, patch = parse_version(v)
    return f"{major}.{minor}.{patch + 1}"

def validate_version_format(v):
    """Valida que la versión tenga formato X.Y.Z"""
    try:
        parts = v.split('.')
        if len(parts) != 3:
            return False
        for p in parts:
            int(p)
        return True
    except:
        return False

def calculate_directory_checksum(directory):
    """Calcula checksum SHA256 de todos los archivos en un directorio"""
    sha256 = hashlib.sha256()
    
    for root, dirs, files in os.walk(directory):
        # Ordenar para consistencia
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as f:
                    while chunk := f.read(8192):
                        sha256.update(chunk)
            except Exception as e:
                print(f"Advertencia: No se pudo leer {filepath}: {e}")
    
    return sha256.hexdigest()

def build_update_package(usb_drive, new_version=None):
    """
    Construye un paquete de actualización en la USB
    
    Args:
        usb_drive: Letra de unidad USB (ej: 'E:')
        new_version: Nueva versión o None para auto-incrementar
    """
    # 1. Determinar versión
    current_version = version.VERSION
    
    if new_version is None:
        # Auto-incrementar patch
        new_version = increment_patch(current_version)
        print(f"📦 Auto-incrementando versión: {current_version} → {new_version}")
    else:
        # Validar formato
        if not validate_version_format(new_version):
            print(f"❌ Error: Formato de versión inválido: {new_version}")
            print("   Debe ser X.Y.Z (ej: 1.0.1)")
            sys.exit(1)
        
        # Verificar que es más nueva
        if not version.is_newer_version(new_version, current_version):
            print(f"❌ Error: La nueva versión {new_version} no es mayor que {current_version}")
            sys.exit(1)
        
        print(f"📦 Actualizando versión: {current_version} → {new_version}")
    
    # 2. Verificar que existe la unidad USB
    if not usb_drive.endswith(':'):
        usb_drive += ':'
    
    if not usb_drive.endswith('\\'):
        usb_drive += '\\'
    
    if not os.path.exists(usb_drive):
        print(f"❌ Error: Unidad USB '{usb_drive}' no encontrada")
        sys.exit(1)
    
    # 3. Preparar directorios
    script_dir = Path(__file__).parent
    update_dir = Path(usb_drive) / 'pos_update'
    files_dir = update_dir / 'files'
    deps_dir = update_dir / 'dependencies'
    
    print(f"\n📂 Creando estructura en {update_dir}")
    
    # Limpiar carpeta existente si la hay
    if update_dir.exists():
        print(f"   Limpiando carpeta existente...")
        shutil.rmtree(update_dir)
    
    # Crear directorios
    update_dir.mkdir(parents=True)
    files_dir.mkdir()
    deps_dir.mkdir()
    
    # 4. Copiar archivos del proyecto
    print(f"\n📄 Copiando archivos del proyecto...")
    
    exclude_patterns = {
        '.git', '.venv', '__pycache__', '*.pyc', '*.pyo', '*.db', '*.db-journal',
        'backups', 'update_temp', 'temp_barcode_*.png', 'test_*.png', 'test_*.py',
        '.gemini', '.gitignore', 'build_update.py'
    }
    
    def should_exclude(path):
        """Verifica si un path debe ser excluido"""
        name = path.name
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or name.startswith(pattern):
                return True
        return False
    
    copied_count = 0
    for item in script_dir.iterdir():
        if should_exclude(item):
            continue
        
        dest = files_dir / item.name
        
        try:
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
                copied_count += sum(1 for _ in dest.rglob('*') if _.is_file())
            else:
                shutil.copy2(item, dest)
                copied_count += 1
            print(f"   ✓ {item.name}")
        except Exception as e:
            print(f"   ✗ Error copiando {item.name}: {e}")
    
    print(f"   Total: {copied_count} archivos copiados")
    
    # 5. Actualizar version.py en el paquete
    print(f"\n🔢 Actualizando version.py a {new_version}")
    version_file = files_dir / 'version.py'
    
    if version_file.exists():
        # Leer contenido actual
        content = version_file.read_text(encoding='utf-8')
        # Reemplazar la línea VERSION
        new_content = []
        for line in content.split('\n'):
            if line.strip().startswith('VERSION ='):
                new_content.append(f'VERSION = "{new_version}"')
            else:
                new_content.append(line)
        version_file.write_text('\n'.join(new_content), encoding='utf-8')
        print(f"   ✓ version.py actualizado")
    else:
        print(f"   ⚠ Advertencia: No se encontró version.py en archivos copiados")
    
    # 6. Descargar dependencias (wheels)
    print(f"\n📦 Descargando dependencias...")
    print(f"   (Esto puede tomar varios minutos)")
    
    requirements_file = script_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print(f"   ⚠ Advertencia: No se encontró requirements.txt")
    else:
        try:
            # Copiar requirements.txt al paquete
            shutil.copy2(requirements_file, deps_dir / 'requirements.txt')
            
            # Descargar wheels usando pip download (sin restricciones de plataforma)
            cmd = [
                sys.executable, '-m', 'pip', 'download',
                '-r', str(requirements_file),
                '-d', str(deps_dir)
            ]
            
            print(f"   Ejecutando pip download...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                print(f"   ⚠ Advertencia: Hubo problemas descargando algunas dependencias")
                print(f"   {result.stderr}")
            else:
                wheels = list(deps_dir.glob('*.whl'))
                print(f"   ✓ {len(wheels)} wheels descargados")
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Error: Timeout descargando dependencias")
        except Exception as e:
            print(f"   ✗ Error descargando dependencias: {e}")
    
    # 7. Generar update_info.json
    print(f"\n📋 Generando update_info.json...")
    
    # Calcular checksum de archivos
    files_checksum = calculate_directory_checksum(files_dir)
    
    # Leer dependencias de requirements.txt
    dependencies = {}
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        pkg, ver = line.split('==')
                        dependencies[pkg.strip()] = ver.strip()
    
    update_info = {
        'version': new_version,
        'release_date': datetime.now().strftime('%Y-%m-%d'),
        'description': f'Actualización a versión {new_version}',
        'requires_python': f'>={sys.version_info.major}.{sys.version_info.minor}',
        'platform': 'win_amd64',
        'files_checksum': files_checksum,
        'dependencies': dependencies
    }
    
    info_file = update_dir / 'update_info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(update_info, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ update_info.json creado")
    
    # 8. Actualizar version.py local (opcional)
    print(f"\n🔄 ¿Actualizar version.py local a {new_version}? (s/n): ", end='')
    response = input().strip().lower()
    
    if response == 's':
        local_version_file = script_dir / 'version.py'
        if local_version_file.exists():
            content = local_version_file.read_text(encoding='utf-8')
            new_content = []
            for line in content.split('\n'):
                if line.strip().startswith('VERSION ='):
                    new_content.append(f'VERSION = "{new_version}"')
                else:
                    new_content.append(line)
            local_version_file.write_text('\n'.join(new_content), encoding='utf-8')
            print(f"   ✓ version.py local actualizado a {new_version}")
    
    # 9. Resumen
    print(f"\n" + "="*60)
    print(f"✅ PAQUETE DE ACTUALIZACIÓN CREADO EXITOSAMENTE")
    print(f"="*60)
    print(f"📍 Ubicación: {update_dir}")
    print(f"📦 Versión: {new_version}")
    print(f"📄 Archivos: {copied_count}")
    print(f"🔧 Dependencias: {len(dependencies)}")
    print(f"🔒 Checksum: {files_checksum[:16]}...")
    print(f"\n💡 Para usar: Conecta la USB en la máquina de producción")
    print(f"             La actualización se iniciará automáticamente")
    print(f"="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python build_update.py <letra_unidad_usb> [nueva_version]")
        print("\nEjemplos:")
        print("  python build_update.py E: 1.0.1    # Versión específica")
        print("  python build_update.py E:          # Auto-incrementa versión patch")
        sys.exit(1)
    
    usb_drive = sys.argv[1]
    new_version = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("\n🚀 CONSTRUCTOR DE PAQUETES DE ACTUALIZACIÓN")
    print("="*60)
    print(f"Versión actual: {version.VERSION}")
    print("="*60 + "\n")
    
    build_update_package(usb_drive, new_version)
