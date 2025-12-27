import customtkinter as ctk
import requests
import socket
import datetime
from ui.styles import *
from ui.icon_manager import IconManager

class RightPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=320, fg_color="transparent", border_width=0)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 

        # --- Card Container ---
        self.card = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS_CARD, 
                                 border_width=1, border_color=COLOR_BORDER)
        self.card.pack(fill="both", expand=True, padx=0, pady=0)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(3, weight=1) # Spacer

        # 1. Totals Section (Top)
        self.totals_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.totals_frame.pack(fill="x", padx=24, pady=(32, 16))
        
        # Status Dot
        self.status_canvas = ctk.CTkCanvas(self.card, width=10, height=10, bg=COLOR_SURFACE, highlightthickness=0)
        self.status_canvas.place(relx=0.92, rely=0.015, anchor="ne")
        self.status_circle = self.status_canvas.create_oval(1, 1, 9, 9, fill=STATUS_OFFLINE, outline="")
        self.status_canvas.bind("<ButtonPress-1>", self.on_status_press)
        self.status_canvas.bind("<ButtonRelease-1>", self.on_status_release)
        self.press_timer = None

        self.lbl_total_title = ctk.CTkLabel(self.totals_frame, text="Total a Pagar", font=FONT_HEADER, text_color=COLOR_TEXT_LIGHT)
        self.lbl_total_title.pack(anchor="w")
        
        self.lbl_total_amount = ctk.CTkLabel(self.totals_frame, text="$0.00", font=FONT_BIG_TOTAL, text_color=COLOR_PRIMARY)
        self.lbl_total_amount.pack(anchor="w", pady=(0, 5))
        
        self.lbl_items_count = ctk.CTkLabel(self.totals_frame, text="0 artículos", font=FONT_BODY, text_color=COLOR_TEXT_LIGHT)
        self.lbl_items_count.pack(anchor="w")

        # 2. SEPARATE TOGGLE UI (Middle)
        self.toggle_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.toggle_container.pack(fill="x", padx=24, pady=(0, 24))

        self.var_void_mode = ctk.BooleanVar(value=False)
        
        # Row for switch + label
        self.switch_row = ctk.CTkFrame(self.toggle_container, fg_color="transparent")
        self.switch_row.pack(fill="x", anchor="w")
        
        self.switch_void = ctk.CTkSwitch(self.switch_row, text="Eliminar al escanear", 
                                         font=FONT_BODY_BOLD, text_color=COLOR_TEXT,
                                         variable=self.var_void_mode, 
                                         command=self.on_toggle_void,
                                         progress_color=COLOR_WARNING, fg_color=COLOR_BORDER,
                                         button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER)
        self.switch_void.pack(side="left")
        
        # Helper text below
        self.lbl_mode_desc = ctk.CTkLabel(self.toggle_container, text="Escanear agrega productos", 
                                          font=FONT_SMALL, text_color=COLOR_TEXT_LIGHT)
        self.lbl_mode_desc.pack(anchor="w", pady=(4,0))

        # 3. Primary Pay Button
        self.icon_pay = IconManager.load_icon("static/icons/icons8-cash-100.png", (32, 32), color="white")
        
        self.btn_pay = ctk.CTkButton(self.card, text=" Cobrar (F5)", image=self.icon_pay, compound="left",
                                     font=FONT_HEADER, height=60, 
                                     fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, 
                                     corner_radius=CORNER_RADIUS,
                                     state="disabled",
                                     command=self.controller.checkout)
        self.btn_pay._fg_color = STATUS_IDLE 
        self.btn_pay.pack(pady=(0, 16), padx=24, fill="x")

        # 4. Destructive Action (Clear) - HIDDEN BY DEFAULT
        self.icon_clear = IconManager.load_icon("static/icons/icons8-broom-50.png", (18, 18), color=COLOR_DESTRUCTIVE)
        
        self.btn_cancel = ctk.CTkButton(self.card, text=" Limpiar", image=self.icon_clear, compound="left",
                                        font=FONT_BODY, height=BUTTON_HEIGHT, 
                                        fg_color="transparent", hover_color="#FEE2E2",
                                        text_color=COLOR_DESTRUCTIVE,
                                        border_width=1, border_color=COLOR_DESTRUCTIVE,
                                        corner_radius=CORNER_RADIUS,
                                        command=self.controller.clear_cart)
        # self.btn_cancel.pack(...) # Don't pack initially

        # Spacer
        ctk.CTkFrame(self.card, fg_color="transparent").pack(expand=True)

        # 5. App Navigation - List Tile Style
        self.bottom_tools = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_tools.pack(side="bottom", fill="x", padx=16, pady=16)
        
        self.icon_import = IconManager.load_icon("static/icons/icons8-big-parcel-50.png", (20, 20), color=COLOR_TEXT)
        self.icon_admin = IconManager.load_icon("static/icons/icons8-admin-settings-male-50.png", (20, 20), color=COLOR_TEXT)
        
        def create_nav_tile(parent, text, icon, command, top_border=False):
            btn = ctk.CTkButton(parent, text=f" {text}", image=icon, compound="left",
                                font=FONT_BODY, height=48,
                                fg_color=COLOR_SURFACE_ALT, hover_color=COLOR_SECONDARY_HOVER,
                                text_color=COLOR_TEXT,
                                corner_radius=CORNER_RADIUS,
                                anchor="w",
                                command=command)
            return btn

        self.btn_import = create_nav_tile(self.bottom_tools, "Importar Inventario", self.icon_import, self.controller.import_inventory)
        self.btn_import.pack(fill="x", pady=(0, 8))

        self.btn_admin = create_nav_tile(self.bottom_tools, "Administración", self.icon_admin, self.controller.open_admin_view)
        self.btn_admin.pack(fill="x", pady=(0, 4))
        
        ctk.CTkLabel(self.bottom_tools, text=f"{datetime.date.today()}", font=FONT_SMALL, text_color=COLOR_TEXT_LIGHT).pack(pady=(4,0))
        
        self.after(2000, self.poll_server_status)


    def update_totals(self, total_sum, total_items):
        self.lbl_total_amount.configure(text=f"${total_sum:.2f}")
        
        if total_items > 0:
             self.lbl_items_count.configure(text=f"{total_items} artículos")
             
             # Enable Pay
             self.btn_pay.configure(state="normal", fg_color=COLOR_PRIMARY, text_color="white")
             
             # Show Clear Button if not packed
             if not self.btn_cancel.winfo_ismapped():
                 self.btn_cancel.configure(text=" Limpiar") # Update text just in case
                 self.btn_cancel.pack(pady=(0, 24), padx=24, fill="x", after=self.btn_pay)
        else:
             self.lbl_items_count.configure(text="Sin artículos")
             
             # Disable Pay - Keep text static
             self.btn_pay.configure(state="disabled", fg_color=STATUS_IDLE, text_color="white")
             
             # Hide Clear Button
             if self.btn_cancel.winfo_ismapped():
                 self.btn_cancel.pack_forget()
            
             # Auto-reset Void Mode if empty
             if self.var_void_mode.get():
                 self.var_void_mode.set(False)
                 self.on_toggle_void() # Trigger logic update

    def on_toggle_void(self):
        active = self.var_void_mode.get()
        self.controller.toggle_void_mode() # Tell controller
        self.update_toggle_visuals(active)

    def set_void_mode(self, active):
        # Called by controller to force state
        if self.var_void_mode.get() != active:
            self.var_void_mode.set(active)
            self.update_toggle_visuals(active)

    def update_toggle_visuals(self, active):
        if active:
            # ON State
            self.lbl_mode_desc.configure(text="Escanear quita productos del carrito", text_color=COLOR_WARNING)
            # Switch color is handled by progress_color, but we can update button color too?
            self.switch_void.configure(button_color=COLOR_WARNING, button_hover_color=COLOR_WARNING)
        else:
            # OFF State
            self.lbl_mode_desc.configure(text="Escanear agrega productos", text_color=COLOR_TEXT_LIGHT)
            self.switch_void.configure(button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER)

    # --- Status & QR Logic ---
    def poll_server_status(self):
        try:
            response = requests.get("http://127.0.0.1:5000/api/server_status", timeout=3)
            if response.status_code == 200:
                data = response.json()
                color = data.get('color', STATUS_OFFLINE)
            else:
                color = STATUS_OFFLINE 
        except Exception:
            color = STATUS_OFFLINE 
            
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
            qr_win.geometry("340x480")
            qr_win.attributes('-topmost', True)
            qr_win.lift()
            
            qr_win.configure(fg_color=COLOR_BACKGROUND)
            
            # Simple QR logic (simplified for brevity)
            ctk.CTkLabel(qr_win, text="Escanea para admin").pack()
            
        except Exception as e:
            print(f"Error showing QR: {e}")
