import customtkinter as ctk
import requests
import socket
import qrcode
import datetime
from ui.styles import *

class RightPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=350, fg_color=COLOR_BACKGROUND, border_width=0)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)

        # Main Container with Card look
        self.card = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_BORDER)
        self.card.pack(fill="both", expand=True, padx=10, pady=10)
        self.card.grid_columnconfigure(0, weight=1)

        # --- Status Indicator ---
        self.status_canvas = ctk.CTkCanvas(self.card, width=16, height=16, bg=COLOR_SURFACE, highlightthickness=0)
        self.status_canvas.place(relx=0.92, rely=0.03, anchor="ne")
        self.status_circle = self.status_canvas.create_oval(2, 2, 14, 14, fill=STATUS_OFFLINE, outline="")
        
        self.status_canvas.bind("<ButtonPress-1>", self.on_status_press)
        self.status_canvas.bind("<ButtonRelease-1>", self.on_status_release)
        self.press_timer = None

        # Totals
        self.lbl_total_title = ctk.CTkLabel(self.card, text="TOTAL A PAGAR", font=FONT_HEADER, text_color=COLOR_TEXT_LIGHT)
        self.lbl_total_title.pack(pady=(40, 5))
        
        self.lbl_total_amount = ctk.CTkLabel(self.card, text="$0.00", font=FONT_BIG_TOTAL, text_color=COLOR_PRIMARY)
        self.lbl_total_amount.pack(pady=5)
        
        self.lbl_items_count = ctk.CTkLabel(self.card, text="0 artículos", font=FONT_SUBHEADER, text_color=COLOR_TEXT_LIGHT)
        self.lbl_items_count.pack(pady=(0, 30))

        # Actions
        self.btn_pay = ctk.CTkButton(self.card, text="🛒 COBRAR (F5)", font=FONT_HEADER, height=70, 
                                     fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, 
                                     corner_radius=CORNER_RADIUS,
                                     command=self.controller.checkout)
        self.btn_pay.pack(pady=20, padx=20, fill="x")
        
        self.btn_void = ctk.CTkButton(self.card, text="🗑️ MODO CANCELAR: OFF", font=FONT_BODY_BOLD, height=BUTTON_HEIGHT,
                                      fg_color=COLOR_SECONDARY, hover_color=COLOR_TEXT_LIGHT,
                                      corner_radius=CORNER_RADIUS,
                                      command=self.controller.toggle_void_mode)
        self.btn_void.pack(pady=10, padx=20, fill="x")
        
        self.btn_cancel = ctk.CTkButton(self.card, text="❌ Limpiar Carrito (Esc)", font=FONT_BODY, height=BUTTON_HEIGHT, 
                                        fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER, 
                                        corner_radius=CORNER_RADIUS,
                                        command=self.controller.clear_cart)
        self.btn_cancel.pack(pady=10, padx=20, fill="x")

        # Admin Button
        self.btn_admin = ctk.CTkButton(self.card, text="⚙️ Ver Ventas (Admin)", font=FONT_SMALL, height=30,
                                       fg_color="transparent", text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BACKGROUND,
                                       command=self.controller.open_admin_view)
        self.btn_admin.pack(side="bottom", pady=(5, 20), padx=20, fill="x")

        # Import Button
        self.btn_import = ctk.CTkButton(self.card, text="📥 Importar Inventario", font=FONT_SMALL, height=30,
                                       fg_color="transparent", text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BACKGROUND,
                                       command=self.controller.import_inventory)
        self.btn_import.pack(side="bottom", pady=(5, 5), padx=20, fill="x")

        # Session Info
        self.lbl_session = ctk.CTkLabel(self.card, text=f"📅 Sesión: {datetime.date.today()}", font=FONT_SMALL, text_color=COLOR_TEXT_LIGHT)
        self.lbl_session.pack(side="bottom", pady=5)
        
        # Start Polling
        self.after(2000, self.poll_server_status)

    def update_totals(self, total_sum, total_items):
        self.lbl_total_amount.configure(text=f"${total_sum:.2f}")
        self.lbl_items_count.configure(text=f"{total_items} artículos")

    def set_void_mode(self, active):
        if active:
            self.btn_void.configure(text="🗑️ MODO CANCELAR: ON", fg_color=COLOR_WARNING, text_color="white")
        else:
            self.btn_void.configure(text="🗑️ MODO CANCELAR: OFF", fg_color=COLOR_SECONDARY, text_color="white")

    # --- Status & QR Logic ---
    def poll_server_status(self):
        try:
            response = requests.get("http://127.0.0.1:5000/api/server_status", timeout=3)
            if response.status_code == 200:
                data = response.json()
                # Backend now calculates the color based on complex logic
                color = data.get('color', STATUS_OFFLINE)
                print(f"DEBUG: Full Data: {data}")
                print(f"DEBUG: Status Color Received: {color}")
            else:
                print(f"Status Error: {response.status_code}")
                color = STATUS_OFFLINE # Red
        except Exception as e:
            print(f"Status Connection Error: {e}")
            color = STATUS_OFFLINE # Red
            
        self.status_canvas.itemconfig(self.status_circle, fill=color)
        self.after(3000, self.poll_server_status)

    def on_status_press(self, event):
        self.press_timer = self.after(2000, self.show_qr_code)

    def on_status_release(self, event):
        if self.press_timer:
            self.after_cancel(self.press_timer)
            self.press_timer = None

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def show_qr_code(self):
        try:
            ip = self.get_local_ip()
            url = f"http://{ip}:5000"
            
            qr_win = ctk.CTkToplevel(self)
            qr_win.title("Acceso Admin")
            qr_win.geometry("300x350")
            
            # Ensure window is on top (fixes Windows issue)
            qr_win.transient(self.winfo_toplevel())
            qr_win.attributes('-topmost', True)
            qr_win.lift()
            
            # Fix Linux grab error: Wait for window to be visible
            qr_win.update()
            qr_win.after(100, lambda: qr_win.grab_set())
            
            ctk.CTkLabel(qr_win, text="Escanear para Acceder", font=FONT_HEADER).pack(pady=10)
            
            # Robust way to get QRCode class
            try:
                import qrcode
                QRClass = qrcode.QRCode
            except AttributeError:
                # Fallback for weird package environments
                import qrcode.main
                QRClass = qrcode.main.QRCode

            qr = QRClass(box_size=10, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img_factory = qr.make_image(fill_color="black", back_color="white")
            
            # Compatibility for different qrcode library versions/wrappers
            if hasattr(img_factory, 'get_image'):
                img = img_factory.get_image()
            elif hasattr(img_factory, '_img'):
                img = img_factory._img
            else:
                img = img_factory
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
            
            ctk.CTkLabel(qr_win, image=ctk_img, text="").pack(pady=10)
            ctk.CTkLabel(qr_win, text=url, font=FONT_BODY, text_color="gray").pack(pady=5)
            
            # Fullscreen Toggle Button
            is_fullscreen = self.controller.attributes("-fullscreen")
            btn_text = "🔳 Salir de Pantalla Completa" if is_fullscreen else "🔲 Pantalla Completa"
            btn_color = COLOR_DANGER if is_fullscreen else COLOR_PRIMARY
            
            def toggle_and_close():
                qr_win.destroy()
                self.controller.toggle_fullscreen()
                
            ctk.CTkButton(qr_win, text=btn_text, command=toggle_and_close, 
                         fg_color=btn_color, hover_color=btn_color).pack(pady=20)
            
        except Exception as e:
            print(f"Error showing QR: {e}")
            if 'qr_win' in locals() and qr_win.winfo_exists():
                ctk.CTkLabel(qr_win, text=f"Error: {e}", text_color="red").pack(pady=20)
