import subprocess
import sys
import os
import atexit
import threading
from tkinter import messagebox
from typing import Optional, Any, Callable

class ProcessManager:
    def __init__(self, app: Any):
        self.app = app
        self.backend_process: Optional[subprocess.Popen] = None

    def start_backend(self) -> None:
        try:
            python_exe = sys.executable
            # Assuming backend.py is in the parent directory of this file's package, 
            # or we rely on the implementation where we know the path.
            # Best to use app's root dir.
            # self.app should be the POSApp instance which is in the root.
            # But let's be robust.
            root_dir = os.getcwd() # Or os.path.dirname(sys.modules['__main__'].__file__) if main is run.
            # Actually, using os.getcwd() might be risky if cwd changed. 
            # Ideally we pass base_path.
            
            script_path = os.path.join(root_dir, "backend.py")
            if not os.path.exists(script_path):
                 # Fallback if we are in managers dir? No, we shouldn't be running from there.
                 pass

            self.backend_process = subprocess.Popen([python_exe, script_path], cwd=root_dir)
            print(f"Backend started with PID: {self.backend_process.pid}")
            atexit.register(self.stop_backend)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Admin Backend: {e}")

    def stop_backend(self) -> None:
        if self.backend_process:
            print("Stopping backend...")
            try:
                # Force kill process tree on Windows
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.backend_process.pid)], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Error killing backend: {e}")
                self.backend_process.terminate()
            self.backend_process = None

    def open_admin_view(self) -> None:
        try:
            python_exe = sys.executable
            # Assuming admin_launcher.py is in the root
            root_dir = os.getcwd()
            script_path = os.path.join(root_dir, "admin_launcher.py")
            
            self.app.attributes('-disabled', True)
            
            def run_admin():
                process = subprocess.Popen([python_exe, script_path], cwd=root_dir)
                process.wait()
                
                def restore_window():
                    self.app.attributes('-disabled', False)
                    self._force_focus()
                    
                self.app.after(0, restore_window)

            threading.Thread(target=run_admin, daemon=True).start()

        except Exception as e:
            self.app.attributes('-disabled', False)
            messagebox.showerror("Error", f"No se pudo abrir la vista de administración: {e}")

    def _force_focus(self) -> None:
        try:
            import ctypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            SW_RESTORE = 9
            
            hwnd = self.app.winfo_id()
            hwnd = user32.GetParent(hwnd)
            if hwnd == 0:
                hwnd = self.app.winfo_id()

            current_thread_id = kernel32.GetCurrentThreadId()
            foreground_hwnd = user32.GetForegroundWindow()
            foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)

            if current_thread_id != foreground_thread_id:
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
                user32.ShowWindow(hwnd, SW_RESTORE)
                user32.SetForegroundWindow(hwnd)
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)
            else:
                user32.ShowWindow(hwnd, SW_RESTORE)
                user32.SetForegroundWindow(hwnd)

        except Exception as e:
            print(f"Focus Error: {e}")
        
        self.app.attributes('-topmost', True)
        self.app.lift()
        self.app.focus_force()
        self.app.attributes('-topmost', False)
        # Assuming app has left_panel exposed or a method to focus
        if hasattr(self.app, 'left_panel'):
             self.app.left_panel.focus_entry()
