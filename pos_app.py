import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import database
from printer_service import PrinterService
import datetime
import subprocess
import sys
import os
import atexit
from ui.styles import *
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel
from ui.checkout_dialog import CheckoutDialog
from usb_monitor import USBMonitor
from updater import Updater
from updater import Updater
import version
from pdf_importer import import_inventory_from_pdf
import argparse

import json

# UI Configuration
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class POSApp(ctk.CTk):
    def __init__(self, safe_mode=False, no_usb=False):
        super().__init__(fg_color=COLOR_BACKGROUND)
        self.safe_mode = safe_mode
        self.no_usb = no_usb
        
        print("--- INICIANDO POS APP ---")
        print(f"Modo Seguro: {self.safe_mode}")
        print(f"Sin USB: {self.no_usb}")
        
        # Load Settings
        self.settings = self.load_settings()
        
        # Initialize Database
        print("Inicializando base de datos...")
        database.init_db()
        print("Base de datos inicializada.")
        
        # Start Backend Server
        self.backend_process = None
        if not self.safe_mode:
            print("Iniciando backend...")
            self.start_backend()
        else:
            print("SKIPPING: Backend (Safe Mode)")
        
        # Initialize USB Monitor for auto-updates
        self.usb_monitor = None
        self.updater = Updater(os.path.dirname(__file__))
        
        if not self.safe_mode and not self.no_usb:
            print("Iniciando monitor USB...")
            self.start_usb_monitor()
        else:
            print("SKIPPING: USB Monitor")

        self.title("Punto de Venta")
        self.geometry("1024x768")
        
        # Data
        self.cart = [] 
        self.current_session = None
        
        if not self.safe_mode:
            print("Iniciando servicio de impresión...")
            self.printer = PrinterService()
        else:
            print("SKIPPING: Printer Service (Safe Mode)")
            self.printer = None
        self.void_mode = False 
        
        # Layout
        # Layout
        print("Configurando Layout...")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Components
        print("Inicializando LeftPanel...")
        self.left_panel = LeftPanel(self, self)
        print("LeftPanel inicializado.")
        
        print("Agregando LeftPanel al grid...")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        print("Inicializando RightPanel...")
        self.right_panel = RightPanel(self, self)
        print("RightPanel inicializado.")
        
        print("Agregando RightPanel al grid...")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Key bindings
        self.bind("<F5>", lambda e: self.checkout())
        self.bind("<Escape>", lambda e: self.clear_cart())
        self.bind("<Button-1>", lambda e: self.check_focus(e))
        self.bind("<F11>", lambda e: self.toggle_fullscreen(from_key=True))

        # Initialize Session (AFTER UI IS BUILT)
        self.init_daily_session()

        # Apply Fullscreen if saved
        if self.settings.get("fullscreen", False):
            self.attributes("-fullscreen", True)

        # Force focus on startup
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        self.after(200, lambda: self.left_panel.focus_entry())
        self.after(500, lambda: self.left_panel.focus_entry())

        # Intercept Window Close Event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window close attempts"""
        if self.attributes("-fullscreen"):
            messagebox.showwarning("Modo Pantalla Completa", "No se puede cerrar la aplicación en modo pantalla completa.\Primero salga del modo pantalla completa usando el menú de administración.")
            return
        
        self.destroy()

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"fullscreen": False}

    def save_settings(self):
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def toggle_fullscreen(self, from_key=False):
        is_fullscreen = self.attributes("-fullscreen")
        
        if is_fullscreen:
            # Exiting fullscreen requires password
            password = simpledialog.askstring("Admin", "Contraseña de Administrador:", show='*', parent=self)
            if password == "admin123":
                self.attributes("-fullscreen", False)
                self.settings["fullscreen"] = False
                self.save_settings()
            elif password is not None:
                messagebox.showerror("Error", "Contraseña incorrecta")
                # Maintain fullscreen if failed
                self.focus_force()
        else:
            # Entering fullscreen is free
            self.attributes("-fullscreen", True)
            self.settings["fullscreen"] = True
            self.save_settings()
            
        self.left_panel.focus_entry()

    def start_backend(self):
        try:
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(__file__), "backend.py")
            self.backend_process = subprocess.Popen([python_exe, script_path], cwd=os.path.dirname(__file__))
            print(f"Backend started with PID: {self.backend_process.pid}")
            atexit.register(self.stop_backend)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Admin Backend: {e}")

    def stop_backend(self):
        if self.backend_process:
            print("Stopping backend...")
            try:
                # Force kill process tree on Windows to ensure no orphaned flask processes
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.backend_process.pid)], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Error killing backend: {e}")
                # Fallback
                self.backend_process.terminate()
            self.backend_process = None
    
    def start_usb_monitor(self):
        """Inicia el monitor de USB para detectar actualizaciones"""
        try:
            self.usb_monitor = USBMonitor(
                update_callback=self.on_update_detected,
                check_interval=2.0
            )
            self.usb_monitor.start()
            print(f"USB Monitor iniciado (Versión actual: {version.VERSION})")
        except Exception as e:
            print(f"Error iniciando USB monitor: {e}")
    
    def on_update_detected(self, update_info):
        """Callback cuando se detecta un paquete de actualización en USB"""
        try:
            # Verificar si podemos actualizar
            can_update, msg = self.updater.can_update(update_info)
            
            if not can_update:
                print(f"No se puede actualizar: {msg}")
                return
            
            # Mostrar diálogo de actualización
            self.show_update_dialog(update_info)
            
        except Exception as e:
            print(f"Error procesando actualización: {e}")
    
    def show_update_dialog(self, update_info):
        """Muestra diálogo de actualización y ejecuta el proceso"""
        try:
            # Detener monitor para evitar múltiples detecciones
            if self.usb_monitor:
                self.usb_monitor.stop()
            
            # Crear ventana de diálogo bloqueante
            dialog = ctk.CTkToplevel(self)
            dialog.title("Actualización")
            dialog.geometry("400x200")
            dialog.transient(self)
            dialog.grab_set()
            
            # Centrar en pantalla
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"400x200+{x}+{y}")
            
            # Mensaje
            label = ctk.CTkLabel(
                dialog,
                text=f"Actualizando a versión {update_info['version']}...\n\nPor favor espere",
                font=("Arial", 16)
            )
            label.pack(expand=True, pady=20)
            
            # Barra de progreso indeterminada
            progress = ctk.CTkProgressBar(dialog, mode="indeterminate")
            progress.pack(pady=10, padx=20, fill="x")
            progress.start()
            
            dialog.update()
            
            # Ejecutar actualización en el mismo thread (bloqueante)
            success = self.updater.perform_update(update_info)
            
            progress.stop()
            
            if success:
                # Actualización exitosa
                label.configure(
                    text=f"✅ Actualización completada\n\nPuede retirar la USB de forma segura"
                )
                progress.pack_forget()
                
                # Botón para reiniciar
                def restart():
                    dialog.destroy()
                    self.updater.restart_application()
                
                btn = ctk.CTkButton(
                    dialog,
                    text="Reiniciar Aplicación",
                    command=restart,
                    fg_color=COLOR_SUCCESS,
                    hover_color="#27AE60"
                )
                btn.pack(pady=10)
                
            else:
                # Error en actualización
                label.configure(
                    text=f"❌ Error durante la actualización\n\nConsulte los logs para más detalles"
                )
                progress.pack_forget()
                
                btn = ctk.CTkButton(
                    dialog,
                    text="Cerrar",
                    command=dialog.destroy,
                    fg_color=COLOR_DANGER
                )
                btn.pack(pady=10)
            
        except Exception as e:
            print(f"Error mostrando diálogo de actualización: {e}")
            messagebox.showerror("Error", f"Error durante actualización: {e}")

    def destroy(self):
        self.stop_backend()
        super().destroy()

    def check_focus(self, event):
        # Basic heuristic to keep focus on scanner
        if not isinstance(event.widget, (ctk.CTkEntry, str)) and "entry" not in str(event.widget).lower():
             self.left_panel.focus_entry()

    def init_daily_session(self):
        print("Verificando sesión diaria...")
        session = database.get_active_session()
        today_str = datetime.date.today().isoformat()
        
        if session:
            start_time = session['start_time'] 
            if start_time.startswith(today_str):
                self.current_session = session['id']
                return
            else:
                database.close_session(session['id'], 0) 
        
        self.after(100, self.ask_initial_cash)

    def ask_initial_cash(self):
        initial = simpledialog.askfloat("Inicio de Turno", "Ingrese efectivo inicial en caja:", parent=self)
        if initial is None: initial = 0.0
        self.current_session = database.create_session(initial)
        self.left_panel.focus_entry()

    def toggle_void_mode(self):
        self.void_mode = not self.void_mode
        self.right_panel.set_void_mode(self.void_mode)
        
        if self.void_mode:
            self.left_panel.set_last_item("MODO CANCELAR ACTIVADO - Escanee para eliminar", COLOR_WARNING)
        else:
            self.left_panel.set_last_item("Listo para escanear", "gray")
        
        self.left_panel.focus_entry()

    def process_barcode(self, barcode):
        product = database.get_product_by_barcode(barcode)
        if not product:
            messagebox.showwarning("No Encontrado", f"Producto con código '{barcode}' no encontrado.")
            self.after(100, lambda: self.left_panel.focus_entry())
            return

        # Show Image
        self.left_panel.update_product_image(product.get('image_path'))

        if self.void_mode:
            self.remove_from_cart(product)
        else:
            self.add_to_cart(product)

    def add_to_cart(self, product):
        for item in self.cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                item['total'] = item['quantity'] * item['price']
                self.update_ui()
                self.left_panel.set_last_item(f"Agregado: {product['name']} (x{item['quantity']})", COLOR_SUCCESS)
                return

        self.cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': 1,
            'total': product['price']
        })
        self.update_ui()
        self.left_panel.set_last_item(f"Agregado: {product['name']}", COLOR_SUCCESS)

    def remove_from_cart(self, product):
        found = False
        for i, item in enumerate(self.cart):
            if item['id'] == product['id']:
                found = True
                item['quantity'] -= 1
                item['total'] = item['quantity'] * item['price']
                
                msg = f"Removido 1: {product['name']}"
                
                if item['quantity'] <= 0:
                    self.cart.pop(i)
                    msg = f"Eliminado: {product['name']}"
                
                self.update_ui()
                self.left_panel.set_last_item(msg, COLOR_WARNING)
                break
        
        if not found:
            messagebox.showwarning("No en Carrito", "Este producto no está en el carrito.")
            self.after(100, lambda: self.left_panel.focus_entry())

    def update_ui(self):
        self.left_panel.update_cart_display(self.cart)
        
        total_sum = sum(item['total'] for item in self.cart)
        total_items = sum(item['quantity'] for item in self.cart)
        self.right_panel.update_totals(total_sum, total_items)

    def clear_cart(self):
        self.cart = []
        self.update_ui()
        self.left_panel.set_last_item("Venta Cancelada", COLOR_DANGER)
        self.left_panel.update_product_image(None) # Clear image
        self.left_panel.focus_entry()

    def checkout(self):
        if not self.cart: return
        # Check printer
        if not self.printer:
             messagebox.showwarning("Aviso", "Servicio de impresión no disponible (Modo Seguro)")
             # Proceed without printing logic that depends on self.printer being a Service object
             # For now, just return or handle gracefully.
             # Actually, let's allow checkout but skip print.
        
        total_sum = sum(item['total'] for item in self.cart)
        
        def on_payment_confirmed(cash, change):
            database.record_sale(self.current_session, self.cart, total_sum, "EFECTIVO")
            
            if self.printer:
                success = self.printer.print_receipt(self.cart, total_sum, "EFECTIVO", cash, change)
                if not success:
                    messagebox.showwarning("Error de Impresora", "No se pudo imprimir el ticket, pero la venta se guardó.")
            else:
                 print("Impresión omitida (PrinterService es None)")
            
            self.clear_cart()
            self.left_panel.set_last_item(f"Venta Completada! Cambio: ${change:.2f}", COLOR_SUCCESS)
            self.left_panel.focus_entry()

        CheckoutDialog(self, total_sum, on_payment_confirmed)

    def open_admin_view(self):
        try:
            # Launch the separate admin window process
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(__file__), "admin_launcher.py")
            
            # Disable main window
            self.attributes('-disabled', True)
            
            def run_admin():
                process = subprocess.Popen([python_exe, script_path], cwd=os.path.dirname(__file__))
                
                # Wait indefinitely for the admin window to close
                process.wait()
                
                def force_focus():
                    try:
                        import ctypes
                        user32 = ctypes.windll.user32
                        kernel32 = ctypes.windll.kernel32

                        # Constants
                        SW_RESTORE = 9
                        
                        # Get window handles
                        hwnd = self.winfo_id()
                        # Ensure we have the top-level window HWND
                        hwnd = user32.GetParent(hwnd)
                        if hwnd == 0:
                            hwnd = self.winfo_id()

                        # Get thread IDs
                        current_thread_id = kernel32.GetCurrentThreadId()
                        foreground_hwnd = user32.GetForegroundWindow()
                        foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)

                        # Attach thread input if different
                        if current_thread_id != foreground_thread_id:
                            user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
                            
                            # Bring to foreground
                            user32.ShowWindow(hwnd, SW_RESTORE)
                            user32.SetForegroundWindow(hwnd)
                            
                            # Detach
                            user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)
                        else:
                            user32.ShowWindow(hwnd, SW_RESTORE)
                            user32.SetForegroundWindow(hwnd)

                    except Exception as e:
                        print(f"Focus Error: {e}")
                    
                    # Tkinter fallbacks
                    self.attributes('-topmost', True)
                    self.lift()
                    self.focus_force()
                    self.attributes('-topmost', False)
                    self.left_panel.focus_entry()

                # Re-enable main window and force focus immediately
                def restore_window():
                    self.attributes('-disabled', False)
                    force_focus()
                    
                self.after(0, restore_window)

            import threading
            threading.Thread(target=run_admin, daemon=True).start()

        except Exception as e:
            self.attributes('-disabled', False)
            messagebox.showerror("Error", f"No se pudo abrir la vista de administración: {e}")

    def import_inventory(self):
        """Importa inventario desde PDF generado por la app móvil"""
        # 1. Password Protection
        password = simpledialog.askstring("Admin", "Contraseña de Administrador:", show='*', parent=self)
        if password != "admin123":
            if password is not None: # Only show error if not cancelled
                messagebox.showerror("Error", "Contraseña incorrecta")
            return

        # 2. Select File
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF de Inventario",
            filetypes=[("PDF Files", "*.pdf")],
            parent=self
        )
        
        if not file_path:
            return

        # 3. Process Import
        try:
            # Show loading (simple cursor change or message)
            self.configure(cursor="wait")
            self.update()
            
            success, message = import_inventory_from_pdf(file_path)
            
            self.configure(cursor="")
            
            if success:
                messagebox.showinfo("Éxito", message)
                # Refresh UI if needed (e.g. if we were displaying product list, but we aren't really)
            else:
                messagebox.showerror("Error de Importación", message)
                
        except Exception as e:
            self.configure(cursor="")
            messagebox.showerror("Error Crítico", f"Falló la importación: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POS Application")
    parser.add_argument("--safe", action="store_true", help="Start in safe mode (no backend, no printer, no usb)")
    parser.add_argument("--no-usb", action="store_true", help="Start without USB monitor")
    args = parser.parse_args()

    print("Iniciando aplicación principal...")
    app = POSApp(safe_mode=args.safe, no_usb=args.no_usb)
    print("Entrando a mainloop...")
    app.mainloop()
