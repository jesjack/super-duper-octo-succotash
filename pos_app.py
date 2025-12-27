import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import database
from printer_service import PrinterService
import datetime
import subprocess
import sys
import os
import atexit
from typing import List, Dict, Optional, Any, Union, Tuple, Callable
import json

from ui.styles import *
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel
from ui.checkout_dialog import CheckoutDialog

import version
from pdf_importer import import_inventory_from_pdf
import argparse

# Managers
from managers.settings_manager import SettingsManager
from managers.process_manager import ProcessManager
from managers.session_manager import SessionManager
from managers.cart_manager import CartManager

# UI Configuration
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class POSApp(ctk.CTk):
    def __init__(self, safe_mode: bool = False):
        super().__init__(fg_color=COLOR_BACKGROUND) # Fluent Background
        self.safe_mode = safe_mode
        
        if self.safe_mode:
            print("--- MODO SEGURO ACTIVADO ---")
        
        # Managers
        self.settings_manager = SettingsManager()
        self.process_manager = ProcessManager(self)
        self.session_manager = SessionManager(self)
        self.cart_manager = CartManager(self)
        
        # Initialize Database
        database.init_db()
        
        # Start Backend Server
        if not self.safe_mode:
            self.process_manager.start_backend()
        else:
            print("SKIPPING: Backend (Safe Mode)")
        
        # Updater removed


        self.title("Punto de Venta")
        self.geometry("1024x768")
        
        # Services
        if not self.safe_mode:
            self.printer: Optional[PrinterService] = PrinterService()
        else:
            print("SKIPPING: Printer Service (Safe Mode)")
            self.printer = None
            
        self.void_mode: bool = False 
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Components
        self.left_panel = LeftPanel(self, self)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.right_panel = RightPanel(self, self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Key bindings
        self.bind("<F5>", lambda e: self.checkout())
        self.bind("<Escape>", lambda e: self.clear_cart())
        self.bind("<Button-1>", lambda e: self.check_focus(e))
        self.bind("<F11>", lambda e: self.toggle_fullscreen(from_key=True))

        # Initialize Session (AFTER UI IS BUILT)
        self.session_manager.init_daily_session()

        # Apply Fullscreen if saved
        if self.settings_manager.get("fullscreen", False):
            self.attributes("-fullscreen", True)

        # Force focus on startup
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        self.after(200, lambda: self.left_panel.focus_entry())
        self.after(500, lambda: self.left_panel.focus_entry())

        # Intercept Window Close Event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Properties for backward compatibility
    @property
    def cart(self) -> List[Dict[str, Any]]:
        return self.cart_manager.cart
    
    @cart.setter
    def cart(self, value: List[Dict[str, Any]]):
        self.cart_manager.cart = value

    @property
    def settings(self) -> Dict[str, Any]:
        return self.settings_manager.settings

    @property
    def current_session(self) -> Optional[int]:
        return self.session_manager.current_session
    
    @current_session.setter
    def current_session(self, value: Optional[int]):
        self.session_manager.current_session = value

    # Event Handlers
    def on_closing(self):
        """Handle window close attempts"""
        if self.attributes("-fullscreen"):
            messagebox.showwarning("Modo Pantalla Completa", "No se puede cerrar la aplicación en modo pantalla completa.\nPrimero salga del modo pantalla completa usando el menú de administración.")
            return
        
        self.destroy()

    def destroy(self):
        self.process_manager.stop_backend()
        super().destroy()

    def toggle_fullscreen(self, from_key: bool = False) -> None:
        is_fullscreen = self.attributes("-fullscreen")
        
        if is_fullscreen:
            # Exiting fullscreen requires password
            password = simpledialog.askstring("Admin", "Contraseña de Administrador:", show='*', parent=self)
            if password == "admin123":
                self.attributes("-fullscreen", False)
                self.settings_manager.set("fullscreen", False)
            elif password is not None:
                messagebox.showerror("Error", "Contraseña incorrecta")
                # Maintain fullscreen if failed
                self.focus_force()
        else:
            # Entering fullscreen is free
            self.attributes("-fullscreen", True)
            self.settings_manager.set("fullscreen", True)
            
        self.left_panel.focus_entry()

    def check_focus(self, event: Any) -> None:
        # Basic heuristic to keep focus on scanner
        if not isinstance(event.widget, (ctk.CTkEntry, str)) and "entry" not in str(event.widget).lower():
             self.left_panel.focus_entry()

    def toggle_void_mode(self) -> None:
        self.void_mode = not self.void_mode
        self.right_panel.set_void_mode(self.void_mode)
        
        if self.void_mode:
            self.left_panel.set_last_item("MODO CANCELAR ACTIVADO - Escanee para eliminar", COLOR_WARNING)
        else:
            self.left_panel.set_last_item("Listo para escanear", "gray")
        
        self.left_panel.focus_entry()

    def process_barcode(self, barcode: str) -> None:
        product = database.get_product_by_barcode(barcode)
        if not product:
            messagebox.showwarning("No Encontrado", f"Producto con código '{barcode}' no encontrado.")
            self.after(100, lambda: self.left_panel.focus_entry())
            return

        # Show Image
        self.left_panel.update_product_image(product.get('image_path'))

        if self.void_mode:
            self.cart_manager.remove_from_cart(product)
        else:
            self.cart_manager.add_to_cart(product)

    # Delegated Methods
    def add_to_cart(self, product: Dict[str, Any]) -> None:
        self.cart_manager.add_to_cart(product)

    def remove_from_cart(self, product: Dict[str, Any]) -> None:
        self.cart_manager.remove_from_cart(product)

    def clear_cart(self) -> None:
        self.cart_manager.clear_cart()

    def checkout(self) -> None:
        self.cart_manager.checkout()

    def open_admin_view(self) -> None:
        self.process_manager.open_admin_view()
    


    def update_ui(self) -> None:
        self.left_panel.update_cart_display(self.cart)
        
        total_sum = sum(item['total'] for item in self.cart)
        total_items = sum(item['quantity'] for item in self.cart)
        self.right_panel.update_totals(total_sum, total_items)

    def import_inventory(self) -> None:
        # Keeping this here as discussed
        password = simpledialog.askstring("Admin", "Contraseña de Administrador:", show='*', parent=self)
        if password != "admin123":
            if password is not None:
                messagebox.showerror("Error", "Contraseña incorrecta")
            return

        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF de Inventario",
            filetypes=[("PDF Files", "*.pdf")],
            parent=self
        )
        
        if not file_path:
            return

        try:
            self.configure(cursor="wait")
            self.update()
            
            success, message = import_inventory_from_pdf(file_path)
            
            self.configure(cursor="")
            
            if success:
                messagebox.showinfo("Éxito", message)
            else:
                messagebox.showerror("Error de Importación", message)
                
        except Exception as e:
            self.configure(cursor="")
            messagebox.showerror("Error Crítico", f"Falló la importación: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POS Application")
    parser.add_argument("--safe", action="store_true", help="Start in safe mode (no backend, no printer)")
    args = parser.parse_args()

    print("Iniciando aplicación principal...")
    app = POSApp(safe_mode=args.safe)
    app.mainloop()
