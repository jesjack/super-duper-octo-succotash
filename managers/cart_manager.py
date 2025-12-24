from tkinter import messagebox
from typing import List, Dict, Any, Optional
from ui.styles import COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER
from ui.checkout_dialog import CheckoutDialog
import database

class CartManager:
    def __init__(self, app: Any):
        self.app = app
        self.cart: List[Dict[str, Any]] = []

    def add_to_cart(self, product: Dict[str, Any]) -> None:
        for item in self.cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                item['total'] = item['quantity'] * item['price']
                self.update_ui()
                self.app.left_panel.set_last_item(f"Agregado: {product['name']} (x{item['quantity']})", COLOR_SUCCESS)
                return

        self.cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': 1,
            'total': product['price']
        })
        self.update_ui()
        self.app.left_panel.set_last_item(f"Agregado: {product['name']}", COLOR_SUCCESS)

    def remove_from_cart(self, product: Dict[str, Any]) -> None:
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
                self.app.left_panel.set_last_item(msg, COLOR_WARNING)
                break
        
        if not found:
            messagebox.showwarning("No en Carrito", "Este producto no está en el carrito.")
            self.app.after(100, lambda: self.app.left_panel.focus_entry())

    def clear_cart(self) -> None:
        self.cart = []
        self.update_ui()
        self.app.left_panel.set_last_item("Venta Cancelada", COLOR_DANGER)
        self.app.left_panel.update_product_image(None) 
        self.app.left_panel.focus_entry()

    def update_ui(self) -> None:
        self.app.left_panel.update_cart_display(self.cart)
        
        total_sum = sum(item['total'] for item in self.cart)
        total_items = sum(item['quantity'] for item in self.cart)
        self.app.right_panel.update_totals(total_sum, total_items)

    def checkout(self) -> None:
        if not self.cart: return
        
        # Check printer logic via app
        if not self.app.printer:
             messagebox.showwarning("Aviso", "Servicio de impresión no disponible (Modo Seguro)")
        
        total_sum = sum(item['total'] for item in self.cart)
        
        def on_payment_confirmed(cash: float, change: float) -> None:
            # We need session ID. It's in session_manager now.
            # Assuming app has session_manager
            session_id = self.app.session_manager.current_session
            
            database.record_sale(session_id, self.cart, total_sum, "EFECTIVO")
            
            if self.app.printer:
                success = self.app.printer.print_receipt(self.cart, total_sum, "EFECTIVO", cash, change)
                if not success:
                    messagebox.showwarning("Error de Impresora", "No se pudo imprimir el ticket, pero la venta se guardó.")
            else:
                 print("Impresión omitida (PrinterService es None)")
            
            self.clear_cart()
            self.app.left_panel.set_last_item(f"Venta Completada! Cambio: ${change:.2f}", COLOR_SUCCESS)
            self.app.left_panel.focus_entry()

        CheckoutDialog(self.app, total_sum, on_payment_confirmed)
