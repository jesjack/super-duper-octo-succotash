import customtkinter as ctk
from ui.styles import *
from PIL import Image
import os

class LeftPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BACKGROUND)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Cart expands

        # 1. Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_BORDER)
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.lbl_scan = ctk.CTkLabel(self.input_frame, text="🔍 Escanear:", font=FONT_SUBHEADER, text_color=COLOR_TEXT)
        self.lbl_scan.pack(side="left", padx=(15, 5), pady=10)
        
        self.entry_scan = ctk.CTkEntry(self.input_frame, width=350, font=FONT_SUBHEADER, height=INPUT_HEIGHT, 
                                       border_color=COLOR_BORDER, fg_color=COLOR_BACKGROUND, text_color=COLOR_TEXT)
        self.entry_scan.pack(side="left", padx=(0, 15), pady=10, fill="x", expand=True)
        self.entry_scan.bind("<Return>", self.on_scan)
        
        # 2. Product Info (Last Scanned)
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        self.lbl_last_item = ctk.CTkLabel(self.info_frame, text="Listo para escanear", font=FONT_SUBHEADER, text_color=COLOR_TEXT_LIGHT)
        self.lbl_last_item.pack(side="left")

        # 3. Product Image
        self.image_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=220, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_BORDER)
        self.image_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.image_frame.pack_propagate(False)
        
        self.lbl_image = ctk.CTkLabel(self.image_frame, text="📷 Sin Imagen", text_color=COLOR_TEXT_LIGHT, font=FONT_BODY)
        self.lbl_image.pack(expand=True, fill="both")

        # 4. Cart List (Custom Scrollable Implementation to fix Linux Segfault)
        self.cart_container = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER)
        self.cart_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(5, 20))
        self.cart_container.grid_columnconfigure(0, weight=1)
        self.cart_container.grid_rowconfigure(1, weight=1)

        # Header
        self.cart_header = ctk.CTkLabel(self.cart_container, text="🛒 Carrito de Compras", font=FONT_SUBHEADER, text_color=COLOR_TEXT)
        self.cart_header.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Canvas & Scrollbar
        import tkinter as tk
        self.cart_canvas = tk.Canvas(self.cart_container, bg=COLOR_SURFACE, highlightthickness=0)
        self.cart_scrollbar = ctk.CTkScrollbar(self.cart_container, command=self.cart_canvas.yview)
        self.cart_canvas.configure(yscrollcommand=self.cart_scrollbar.set)

        self.cart_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0,5), pady=5)
        self.cart_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Inner Frame (The actual cart_frame where items go)
        # Note: We use a standard CTkFrame here, but inside the canvas
        self.cart_frame = ctk.CTkFrame(self.cart_canvas, fg_color=COLOR_SURFACE)
        self.cart_window_id = self.cart_canvas.create_window((0, 0), window=self.cart_frame, anchor="nw")

        def _configure_cart_frame(event):
            self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
            self.cart_canvas.itemconfig(self.cart_window_id, width=event.width)

        self.cart_frame.bind("<Configure>", _configure_cart_frame)
        self.cart_canvas.bind("<Configure>", lambda e: self.cart_canvas.itemconfig(self.cart_window_id, width=e.width))

    def on_scan(self, event=None):
        barcode = self.entry_scan.get().strip()
        if not barcode: return
        self.entry_scan.delete(0, "end")
        self.controller.process_barcode(barcode)

    def update_cart_display(self, cart):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
            
        headers = ["Cant.", "Producto", "Precio", "Total"]
        # Header Row Background
        header_bg = ctk.CTkFrame(self.cart_frame, fg_color=COLOR_BACKGROUND, height=30, corner_radius=5)
        header_bg.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.cart_frame, text=h, font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="w" if i < 2 else "e")

        # Configure columns to stretch properly
        self.cart_frame.grid_columnconfigure(1, weight=1)

        for i, item in enumerate(cart):
            r = i + 1
            # Alternating row colors could be done with frames, but for simplicity keeping labels
            # Using a separator line or just spacing
            
            ctk.CTkLabel(self.cart_frame, text=str(item['quantity']), font=FONT_BODY, text_color=COLOR_TEXT).grid(row=r, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.cart_frame, text=item['name'], font=FONT_BODY, text_color=COLOR_TEXT).grid(row=r, column=1, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.cart_frame, text=f"${item['price']:.2f}", font=FONT_BODY, text_color=COLOR_TEXT).grid(row=r, column=2, padx=10, pady=2, sticky="e")
            ctk.CTkLabel(self.cart_frame, text=f"${item['total']:.2f}", font=FONT_BODY_BOLD, text_color=COLOR_TEXT).grid(row=r, column=3, padx=10, pady=2, sticky="e")

    def set_last_item(self, text, color):
        self.lbl_last_item.configure(text=text, text_color=color)

    def update_product_image(self, image_path):
        if image_path:
            try:
                full_path = os.path.join("static", "uploads", image_path)
                if os.path.exists(full_path):
                    pil_img = Image.open(full_path)
                    # Resize keeping aspect ratio
                    pil_img.thumbnail((200, 200))
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                    self.lbl_image.configure(image=ctk_img, text="")
                else:
                    self.lbl_image.configure(image=None, text="Imagen no encontrada")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.lbl_image.configure(image=None, text="Error al cargar imagen")
        else:
            self.lbl_image.configure(image=None, text="Sin Imagen")

    def focus_entry(self):
        self.entry_scan.focus_set()
