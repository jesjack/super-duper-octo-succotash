"""
Sistema de actualización automática desde USB
Maneja la instalación completa de actualizaciones incluyendo archivos y dependencias
"""

import os
import sys
import shutil
import subprocess
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
import version

class Updater:
    """
    Maneja el proceso de actualización completo
    """
    
    def __init__(self, app_root: str):
        """
        Inicializa el updater
        
        Args:
            app_root: Directorio raíz de la aplicación
        """
        self.app_root = Path(app_root)
        self.backup_dir = self.app_root / 'backups'
        self.temp_dir = self.app_root / 'update_temp'
        
    def can_update(self, update_info: dict) -> tuple[bool, str]:
        """
        Verifica si la actualización puede ser instalada
        
        Args:
            update_info: Información de la actualización
        
        Returns:
            (puede_actualizar, mensaje)
        """
        # Verificar versión
        update_version = update_info.get('version')
        current_version = version.VERSION
        
        try:
            if not version.is_newer_version(update_version, current_version):
                return False, f"La versión {update_version} no es más nueva que {current_version}"
        except ValueError as e:
            return False, f"Error verificando versión: {e}"
        
        # Verificar plataforma
        platform = update_info.get('platform', '')
        if 'win' not in platform.lower():
            return False, f"Plataforma incompatible: {platform}"
        
        # Verificar que existe el paquete
        package_path = Path(update_info.get('package_path', ''))
        if not package_path.exists():
            return False, "Ruta del paquete no existe"
        
        return True, "OK"
    
    def create_backup(self) -> Path:
        """
        Crea un respaldo de la instalación actual
        
        Returns:
            Path del directorio de respaldo
        """
        # Crear directorio de backups si no existe
        self.backup_dir.mkdir(exist_ok=True)
        
        # Nombre de backup con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_v{version.VERSION}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        print(f"Updater: Creando respaldo en {backup_path}")
        
        # Exclusiones
        exclude_patterns = {
            '.git', '.venv', '__pycache__', '*.pyc', '*.pyo',
            'backups', 'update_temp', '*.db', '*.db-journal'
        }
        
        def should_exclude(path: Path) -> bool:
            """Verifica si un path debe ser excluido del backup"""
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    # Pattern de extensión
                    if path.suffix == pattern[1:]:
                        return True
                elif path.name == pattern:
                    return True
            return False
        
        # Copiar archivos
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for item in self.app_root.iterdir():
            if should_exclude(item):
                continue
            
            dest = backup_path / item.name
            
            try:
                if item.is_dir():
                    shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
                else:
                    shutil.copy2(item, dest)
            except Exception as e:
                print(f"Updater: Advertencia - Error copiando {item}: {e}")
        
        print(f"Updater: Respaldo completado")
        return backup_path
    
    def install_dependencies(self, package_path: Path) -> bool:
        """
        Instala dependencias desde wheels en el paquete
        
        Args:
            package_path: Ruta al paquete de actualización
        
        Returns:
            True si exitoso, False si hubo error
        """
        deps_dir = package_path / 'dependencies'
        
        if not deps_dir.exists():
            print("Updater: Advertencia - No hay carpeta de dependencias")
            return True
        
        # Obtener Python executable del virtualenv actual
        python_exe = sys.executable
        
        print(f"Updater: Instalando dependencias desde {deps_dir}")
        
        # Obtener lista de wheels
        wheels = list(deps_dir.glob('*.whl'))
        
        if not wheels:
            print("Updater: No hay wheels para instalar")
            return True
        
        try:
            # Instalar todos los wheels con --force-reinstall para manejar cambios de versión
            wheel_paths = [str(w) for w in wheels]
            
            cmd = [
                python_exe, '-m', 'pip', 'install',
                '--force-reinstall',  # Fuerza reinstalación (permite cambios de versión)
                '--no-index',  # No usar PyPI
                '--find-links', str(deps_dir),  # Buscar en directorio de wheels
            ] + wheel_paths
            
            print(f"Updater: Ejecutando: {' '.join(cmd[:6])}... ({len(wheels)} wheels)")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode != 0:
                print(f"Updater: Error instalando dependencias:")
                print(result.stderr)
                return False
            
            print("Updater: Dependencias instaladas exitosamente")
            return True
            
        except subprocess.TimeoutExpired:
            print("Updater: Timeout instalando dependencias")
            return False
        except Exception as e:
            print(f"Updater: Error instalando dependencias: {e}")
            return False
    
    def install_files(self, package_path: Path) -> bool:
        """
        Instala archivos actualizados desde el paquete
        
        Args:
            package_path: Ruta al paquete de actualización
        
        Returns:
            True si exitoso, False si hubo error
        """
        files_dir = package_path / 'files'
        
        if not files_dir.exists():
            print("Updater: Error - No hay carpeta de archivos")
            return False
        
        print(f"Updater: Instalando archivos desde {files_dir}")
        
        # Exclusiones (archivos que NO deben ser sobrescritos)
        exclude_files = {
            'pos_system.db',  # Base de datos
            '*.db-journal',
            '*.db'
        }
        
        def should_exclude_file(filename: str) -> bool:
            for pattern in exclude_files:
                if pattern.startswith('*'):
                    if filename.endswith(pattern[1:]):
                        return True
                elif filename == pattern:
                    return True
            return False
        
        try:
            # Copiar archivos recursivamente
            for item in files_dir.rglob('*'):
                if item.is_file():
                    # Calcular ruta relativa y destino
                    rel_path = item.relative_to(files_dir)
                    
                    if should_exclude_file(item.name):
                        print(f"Updater: Saltando {rel_path} (excluido)")
                        continue
                    
                    dest = self.app_root / rel_path
                    
                    # Crear directorio padre si no existe
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar archivo
                    shutil.copy2(item, dest)
                    print(f"Updater: Actualizado {rel_path}")
            
            print("Updater: Archivos instalados exitosamente")
            return True
            
        except Exception as e:
            print(f"Updater: Error instalando archivos: {e}")
            return False
    
    def cleanup_temp(self):
        """Limpia archivos temporales"""
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                print("Updater: Archivos temporales limpiados")
            except Exception as e:
                print(f"Updater: Error limpiando temporales: {e}")
    
    def perform_update(self, update_info: dict) -> bool:
        """
        Ejecuta el proceso completo de actualización
        
        Args:
            update_info: Información del paquete de actualización
        
        Returns:
            True si exitoso, False si hubo error
        """
        package_path = Path(update_info['package_path'])
        
        print("\n" + "="*60)
        print(f"INICIANDO ACTUALIZACIÓN A VERSIÓN {update_info['version']}")
        print("="*60 + "\n")
        
        try:
            # 1. Verificar que podemos actualizar
            can_update, msg = self.can_update(update_info)
            if not can_update:
                print(f"Updater: No se puede actualizar - {msg}")
                return False
            
            # 2. Crear respaldo
            print("\n[1/4] Creando respaldo...")
            backup_path = self.create_backup()
            print(f"✓ Respaldo creado en: {backup_path}")
            
            # 3. Instalar dependencias
            print("\n[2/4] Instalando dependencias...")
            if not self.install_dependencies(package_path):
                print("✗ Error instalando dependencias")
                return False
            print("✓ Dependencias instaladas")
            
            # 4. Instalar archivos
            print("\n[3/4] Instalando archivos...")
            if not self.install_files(package_path):
                print("✗ Error instalando archivos")
                return False
            print("✓ Archivos instalados")
            
            # 5. Limpiar archivos temporales
            print("\n[4/4] Limpiando archivos temporales...")
            self.cleanup_temp()
            print("✓ Limpieza completada")
            
            print("\n" + "="*60)
            print(f"ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
            print(f"Versión anterior: {version.VERSION}")
            print(f"Versión nueva: {update_info['version']}")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\nUpdater: ERROR DURANTE ACTUALIZACIÓN: {e}")
            print(f"Puede restaurar desde respaldo en: {self.backup_dir}")
            return False
    
    def restart_application(self):
        """
        Reinicia la aplicación
        """
        print("\nUpdater: Reiniciando aplicación...")
        
        # Obtener el script principal
        main_script = self.app_root / 'pos_app.py'
        python_exe = sys.executable
        
        # Lanzar nueva instancia
        subprocess.Popen(
            [python_exe, str(main_script)],
            cwd=str(self.app_root),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        # Salir de la instancia actual
        print("Updater: Saliendo de instancia actual...")
        sys.exit(0)
