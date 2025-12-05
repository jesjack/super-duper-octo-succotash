"""
Monitor de USB para detectar actualizaciones automáticas
Busca carpeta 'pos_update/' en unidades USB conectadas
"""

import os
import json
import time
import threading
import psutil
from typing import Callable, Optional, Set

class USBMonitor:
    """
    Monitorea conexiones de USB y detecta paquetes de actualización
    """
    
    def __init__(self, update_callback: Callable, check_interval: float = 2.0):
        """
        Inicializa el monitor de USB
        
        Args:
            update_callback: Función a llamar cuando se detecta actualización
            check_interval: Intervalo en segundos entre verificaciones (default: 2.0)
        """
        self.update_callback = update_callback
        self.check_interval = check_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.known_drives: Set[str] = set()
        
    def start(self):
        """Inicia el monitoreo en un thread daemon"""
        if not self.running:
            self.running = True
            self.known_drives = self._get_current_drives()
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print("USB Monitor: Iniciado")
    
    def stop(self):
        """Detiene el monitoreo"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("USB Monitor: Detenido")
    
    def _get_current_drives(self) -> Set[str]:
        """
        Obtiene lista de unidades actualmente montadas
        
        Returns:
            Set de letras de unidad (ej: {'C:\\', 'D:\\'})
        """
        drives = set()
        for partition in psutil.disk_partitions(all=False):
            # Solo unidades removibles (USB) y fijas
            if 'removable' in partition.opts.lower() or 'fixed' in partition.opts.lower():
                drives.add(partition.mountpoint)
        return drives
    
    def _check_for_update_package(self, drive: str) -> Optional[dict]:
        """
        Verifica si una unidad contiene un paquete de actualización válido
        
        Args:
            drive: Letra de unidad (ej: 'E:\\')
        
        Returns:
            Dict con info de actualización si es válida, None si no
        """
        update_path = os.path.join(drive, 'pos_update')
        info_file = os.path.join(update_path, 'update_info.json')
        
        # Verificar que existe la carpeta y el archivo de info
        if not os.path.isdir(update_path):
            return None
        
        if not os.path.isfile(info_file):
            print(f"USB Monitor: Carpeta pos_update encontrada en {drive} pero falta update_info.json")
            return None
        
        # Leer y validar update_info.json
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                update_info = json.load(f)
            
            # Validar campos requeridos
            required_fields = ['version', 'platform', 'files_checksum']
            for field in required_fields:
                if field not in update_info:
                    print(f"USB Monitor: update_info.json inválido, falta campo '{field}'")
                    return None
            
            # Verificar que existe carpeta de archivos
            files_path = os.path.join(update_path, 'files')
            if not os.path.isdir(files_path):
                print(f"USB Monitor: Falta carpeta 'files' en paquete de actualización")
                return None
            
            # Verificar que existe carpeta de dependencias
            deps_path = os.path.join(update_path, 'dependencies')
            if not os.path.isdir(deps_path):
                print(f"USB Monitor: Falta carpeta 'dependencies' en paquete de actualización")
                return None
            
            # Agregar ruta completa del paquete al info
            update_info['package_path'] = update_path
            
            print(f"USB Monitor: Paquete de actualización válido encontrado en {drive}")
            print(f"  Versión: {update_info.get('version')}")
            print(f"  Descripción: {update_info.get('description', 'N/A')}")
            
            return update_info
            
        except json.JSONDecodeError as e:
            print(f"USB Monitor: Error parseando update_info.json: {e}")
            return None
        except Exception as e:
            print(f"USB Monitor: Error verificando paquete: {e}")
            return None
    
    def _monitor_loop(self):
        """Loop principal del monitor (corre en thread separado)"""
        while self.running:
            try:
                # Obtener unidades actuales
                current_drives = self._get_current_drives()
                
                # Detectar nuevas unidades
                new_drives = current_drives - self.known_drives
                
                if new_drives:
                    print(f"USB Monitor: Nueva(s) unidad(es) detectada(s): {new_drives}")
                    
                    # Verificar cada nueva unidad
                    for drive in new_drives:
                        update_info = self._check_for_update_package(drive)
                        if update_info:
                            # Encontramos una actualización válida
                            print(f"USB Monitor: Activando callback de actualización...")
                            try:
                                self.update_callback(update_info)
                            except Exception as e:
                                print(f"USB Monitor: Error en callback: {e}")
                            # Solo procesamos la primera actualización encontrada
                            break
                
                # Actualizar conjunto de unidades conocidas
                self.known_drives = current_drives
                
            except Exception as e:
                print(f"USB Monitor: Error en loop de monitoreo: {e}")
            
            # Esperar antes del siguiente chequeo
            time.sleep(self.check_interval)


# Ejemplo de uso
if __name__ == "__main__":
    def on_update_found(update_info):
        print("\n🔔 ACTUALIZACIÓN DETECTADA!")
        print(f"Versión: {update_info['version']}")
        print(f"Ruta: {update_info['package_path']}")
    
    monitor = USBMonitor(on_update_found, check_interval=2.0)
    monitor.start()
    
    try:
        print("Monitoreando USBs... (Ctrl+C para detener)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo monitor...")
        monitor.stop()
