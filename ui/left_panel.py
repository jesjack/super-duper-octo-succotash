import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from ui.styles import *
from ui.icon_manager import IconManager
from PIL import Image
import os

class LeftPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND) 
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. Search/Input Section ---
        self.input_card = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS_CARD, 
                                       border_width=1, border_color=COLOR_BORDER)
        self.input_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 12))
        
        # Search Icon (Colorized)
        self.icon_search = IconManager.load_icon("static/icons/icons8-search-50.png", (20, 20), color=COLOR_TEXT_LIGHT)
        self.icon_search_active = IconManager.load_icon("static/icons/icons8-search-50.png", (20, 20), color=COLOR_FOCUS)

        self.lbl_scan = ctk.CTkLabel(self.input_card, text="", image=self.icon_search)
        self.lbl_scan.pack(side="left", padx=(16, 5), pady=12)
        
        self.entry_scan = ctk.CTkEntry(self.input_card, width=300, font=FONT_BODY, height=INPUT_HEIGHT, 
                                       border_width=0, fg_color="transparent", text_color=COLOR_TEXT,
                                       placeholder_text="ESCRIBE O ESCANEA AQUÍ...")
        self.entry_scan.pack(side="left", padx=(0, 16), pady=12, fill="x", expand=True)
        self.entry_scan.bind("<Return>", self.on_scan)
        
        # Focus Visuals
        self.entry_scan.bind("<FocusIn>", self.on_focus_in)
        self.entry_scan.bind("<FocusOut>", self.on_focus_out)

        # --- 2. Main Content Area ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Info Bar (Ready state)
        self.info_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=30)
        self.info_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        self.lbl_last_item = ctk.CTkLabel(self.info_bar, text="Listo para nueva venta", font=FONT_BODY, text_color=STATUS_IDLE)
        self.lbl_last_item.pack(side="left")

        # Cart Container
        self.cart_container_border = ctk.CTkFrame(self.content_frame, fg_color=COLOR_SURFACE, 
                                                  corner_radius=CORNER_RADIUS_CARD, border_width=1, border_color=COLOR_BORDER)
        self.cart_container_border.grid(row=1, column=0, sticky="nsew")
        self.cart_container_border.grid_columnconfigure(0, weight=1)
        self.cart_container_border.grid_rowconfigure(2, weight=1) # Canvas expands
        # Header
        self.cart_header_frame = ctk.CTkFrame(self.cart_container_border, fg_color="transparent", height=48, corner_radius=0)
        self.cart_header_frame.grid(row=0, column=0, sticky="ew")
        self.cart_header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.cart_header_frame, text="Producto", font=FONT_SUBHEADER, text_color=COLOR_TEXT_LIGHT).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(self.cart_header_frame, text="Cantidad", font=FONT_SUBHEADER, text_color=COLOR_TEXT_LIGHT).grid(row=0, column=1, sticky="e", padx=(0, 70), pady=10)
        ctk.CTkLabel(self.cart_header_frame, text="Precio", font=FONT_SUBHEADER, text_color=COLOR_TEXT_LIGHT).grid(row=0, column=2, sticky="e", padx=20, pady=10)
        
        # Separator inside (Managed in update)
        self.header_separator = ctk.CTkFrame(self.cart_container_border, height=1, fg_color=COLOR_BORDER)
        self.header_separator.grid(row=1, column=0, sticky="ew")

        # --- Empty State Widget ---
        self.active_cart_view = None 

        self.empty_frame = ctk.CTkFrame(self.cart_container_border, fg_color="transparent")
        self.icon_empty_cart = IconManager.load_icon("static/icons/icons8-shopping-cart-50.png", (64, 64), color=STATUS_IDLE)
        
        ctk.CTkLabel(self.empty_frame, text="", image=self.icon_empty_cart).pack(pady=(40, 10))
        ctk.CTkLabel(self.empty_frame, text="Tu carrito está vacío", font=FONT_HEADER, text_color=STATUS_IDLE).pack()
        ctk.CTkLabel(self.empty_frame, text="Escanea un producto para comenzar", font=FONT_BODY, text_color=COLOR_TEXT_LIGHT).pack(pady=5)

        # --- Cart List Widget ---
        self.cart_canvas_container = tk.Frame(self.cart_container_border, bg=COLOR_SURFACE)
        self.cart_canvas_container.grid_columnconfigure(0, weight=1)
        self.cart_canvas_container.grid_rowconfigure(0, weight=1)

        self.cart_canvas = tk.Canvas(self.cart_canvas_container, bg=COLOR_SURFACE, highlightthickness=0)
        self.cart_scrollbar = ttk.Scrollbar(self.cart_canvas_container, orient="vertical", command=self.cart_canvas.yview)
        self.cart_canvas.configure(yscrollcommand=self.cart_scrollbar.set)

        self.cart_canvas.grid(row=0, column=0, sticky="nsew")
        self.cart_scrollbar.grid(row=0, column=1, sticky="ns")

        self.cart_frame = tk.Frame(self.cart_canvas, bg=COLOR_SURFACE)
        self.cart_window_id = self.cart_canvas.create_window((0, 0), window=self.cart_frame, anchor="nw")

        def _configure_inner_frame(event):
            # Update scrollregion
            self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
            
            # Auto-hide/show scrollbar logic
            content_height = self.cart_frame.winfo_reqheight()
            visible_height = self.cart_canvas.winfo_height()
            
            if content_height > visible_height:
                self.cart_scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                self.cart_scrollbar.grid_remove()

        def _configure_canvas(event):
            self.cart_canvas.itemconfig(self.cart_window_id, width=event.width)
            # Re-check scrollbar on canvas resize (e.g. max/restore window)
            _configure_inner_frame(None)

        self.cart_frame.bind("<Configure>", _configure_inner_frame)
        self.cart_canvas.bind("<Configure>", _configure_canvas)
        
        # --- Image Preview (Small, Bottom Left) ---
        self.image_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_SURFACE, height=0, # Start hidden
                                        corner_radius=CORNER_RADIUS_CARD, border_width=0)
        self.image_frame.grid(row=2, column=0, sticky="ew", pady=(12,0))
        self.image_frame.pack_propagate(False)
        self.lbl_image = ctk.CTkLabel(self.image_frame, text="", text_color=COLOR_TEXT_LIGHT)
        self.lbl_image.pack(expand=True, fill="both")

        # Initial State
        self.show_empty_state()

    def on_focus_in(self, event):
        self.input_card.configure(border_color=COLOR_FOCUS, border_width=2)
        self.lbl_scan.configure(image=self.icon_search_active)

    def on_focus_out(self, event):
        self.input_card.configure(border_color=COLOR_BORDER, border_width=1)
        self.lbl_scan.configure(image=self.icon_search)

    def show_empty_state(self):
        self.cart_canvas_container.grid_forget()
        self.empty_frame.grid(row=2, column=0, sticky="nsew")
        
        # Hide Header in Empty State
        self.cart_header_frame.grid_remove()
        self.header_separator.grid_remove()

    def show_cart_list(self):
        self.empty_frame.grid_forget()
        self.cart_canvas_container.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)
        
        # Show Header
        self.cart_header_frame.grid()
        self.header_separator.grid()

    def on_scan(self, event=None):
        barcode = self.entry_scan.get().strip()
        if not barcode: return
        self.entry_scan.delete(0, "end")
        self.controller.process_barcode(barcode)

    def update_cart_display(self, cart):
        if not cart:
            self.show_empty_state()
            return
        
        self.show_cart_list()
        
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
        
        # We don't need header row inside canvas anymore, it's fixed above
        self.cart_frame.grid_columnconfigure(1, weight=1)

        for i, item in enumerate(cart):
            # Using tk.Label for layout perf
            
            # Row Container
            h = 40
            row_frame = tk.Frame(self.cart_frame, bg=COLOR_SURFACE, height=h)
            row_frame.pack(fill="x", padx=10, pady=2)
            row_frame.pack_propagate(False)
            row_frame.grid_columnconfigure(1, weight=1)
            
            # Name
            tk.Label(row_frame, text=item['name'], font=FONT_BODY, fg=COLOR_TEXT, bg=COLOR_SURFACE, anchor="w").grid(row=0, column=1, sticky="ew", padx=5)
            
            # Qty (Left aligned or pill?)
            # Let's put Qty first? Design says separate columns.
            # Re-aligning with header: Product (0), Qty (1), Price (2)
            # The header above: Product (Left), Cant (Right), Price (Right -- Wait, Total?)
            
            # Let's match: 
            # Col 0: Name (Expanded)
            # Col 1: Qty x Unit Price (Right)
            # Col 2: Total Price (Right, Bold)
            
            # Name (Left, expandable)
            tk.Label(row_frame, text=item['name'], font=FONT_BODY_BOLD, fg=COLOR_TEXT, bg=COLOR_SURFACE, anchor="w").pack(side="left", fill="x", expand=True)
            
            price_frame = tk.Frame(row_frame, bg=COLOR_SURFACE)
            price_frame.pack(side="right", padx=(10, 0))

            # Column widths (CLAVE)
            price_frame.grid_columnconfigure(0, minsize=12)   # $
            price_frame.grid_columnconfigure(1, minsize=84)   # número completo

            tk.Label(
                price_frame, text="$",
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT, bg=COLOR_SURFACE,
                anchor="e"
            ).grid(row=0, column=0, sticky="e")

            tk.Label(
                price_frame, text=f"{item['price']:.2f}",
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT, bg=COLOR_SURFACE,
                anchor="e"
            ).grid(row=0, column=1, sticky="e")


            # Qty box with 2-column price alignment
            qty_frame = tk.Frame(row_frame, bg=COLOR_SURFACE)
            qty_frame.pack(side="right", padx=(80, 40))

            
            qty_frame.grid_columnconfigure(1, minsize=12)  # $
            qty_frame.grid_columnconfigure(2, minsize=64)  # número completo

            tk.Label(
                qty_frame, text="$",
                font=FONT_SMALL,
                fg=COLOR_TEXT_LIGHT, bg=COLOR_SURFACE,
                anchor="e"
            ).grid(row=0, column=1, sticky="e")

            tk.Label(
                qty_frame, text=f"{item['price']:.2f}",
                font=FONT_SMALL,
                fg=COLOR_TEXT_LIGHT, bg=COLOR_SURFACE,
                anchor="e"
            ).grid(row=0, column=2, sticky="e")

            # Separator
            tk.Frame(self.cart_frame, height=1, bg=COLOR_BACKGROUND).pack(fill="x", padx=10)

    def set_last_item(self, text, color):
        if color == "gray": color = STATUS_IDLE
        self.lbl_last_item.configure(text=text, text_color=color)

    def update_product_image(self, image_path):
        if image_path:
            try:
                full_path = os.path.join("static", "uploads", image_path)
                if os.path.exists(full_path):
                    self.image_frame.configure(height=120, border_width=1, border_color=COLOR_BORDER)
                    pil_img = Image.open(full_path)
                    pil_img.thumbnail((110, 110))
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                    self.lbl_image.configure(image=ctk_img, text="")
                else:
                    self.hide_image()
            except Exception:
                self.hide_image()
        else:
            self.hide_image()

    def hide_image(self):
        self.image_frame.configure(height=0, border_width=0)
        self.lbl_image.configure(image=None, text="")

    def focus_entry(self):
        self.entry_scan.focus_set()
