import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from ui.styles import *

# Mock Controller
class MockController:
    def process_barcode(self, code):
        pass

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Hybrid Panel: Native Frame, but holds CTK widgets for input/image, 
# and runs a PURE TK loop for the cart.
class HybridLeftPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 1. Input Area (CTK - Verified working in isolation)
        print("DEBUG: Creating CTK Input Frame...")
        self.input_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_BORDER)
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self.input_frame, text="🔍 Escanear:", font=FONT_SUBHEADER).pack(side="left", padx=10, pady=10)
        ctk.CTkEntry(self.input_frame, width=200).pack(side="left", padx=10, pady=10)
        
        # 2. Info (CTK)
        ctk.CTkLabel(self, text="Info Mock").grid(row=1, column=0, pady=5)

        # 3. Image (CTK - Verified working)
        print("DEBUG: Creating CTK Image Frame...")
        self.image_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=220)
        self.image_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self.image_frame, text="Image Mock").pack()

        # 4. Cart List - PURE TKINTER (No CTK widgets inside)
        print("DEBUG: Creating PURE TK Cart...")
        
        # Container
        self.cart_container = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#E5E7EB")
        self.cart_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(5, 20))
        self.cart_container.grid_columnconfigure(0, weight=1)
        self.cart_container.grid_rowconfigure(1, weight=1)

        # Header (Standard Label)
        # Using a standard tk.Label with similar styling
        tk.Label(self.cart_container, text="🛒 Carrito de Compras", font=("Segoe UI", 12, "bold"), bg="white", fg="#1F2937").grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Canvas
        self.cart_canvas = tk.Canvas(self.cart_container, bg="white", highlightthickness=0)
        
        # Standard TTK Scrollbar (Platform native look)
        self.cart_scrollbar = ttk.Scrollbar(self.cart_container, orient="vertical", command=self.cart_canvas.yview)
        self.cart_canvas.configure(yscrollcommand=self.cart_scrollbar.set)

        self.cart_scrollbar.grid(row=1, column=1, sticky="ns")
        self.cart_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Inner Frame
        self.cart_frame = tk.Frame(self.cart_canvas, bg="white")
        self.cart_window_id = self.cart_canvas.create_window((0, 0), window=self.cart_frame, anchor="nw")

        def _configure_inner_frame(event):
            self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
        def _configure_canvas(event):
            self.cart_canvas.itemconfig(self.cart_window_id, width=event.width)

        self.cart_frame.bind("<Configure>", _configure_inner_frame)
        self.cart_canvas.bind("<Configure>", _configure_canvas)
        
        # Add pure TK Items
        print("DEBUG: Adding TK items...")
        for i in range(10):
            row = tk.Frame(self.cart_frame, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"Item {i}", bg="white").pack(side="left")

        print("DEBUG: Cart Structure Created.")

print("DEBUG: Starting Pure TK Cart Test")
app = ctk.CTk()
app.geometry("800x600")
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

try:
    panel = HybridLeftPanel(app, MockController())
    panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    print("DEBUG: Mainloop...")
    app.mainloop()
except Exception as e:
    print(f"ERROR: {e}")
