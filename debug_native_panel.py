import customtkinter as ctk
import tkinter as tk
from ui.styles import *

# Mock Controller
class MockController:
    def process_barcode(self, code):
        print(f"Controller: MOCK process {code}")

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# REDEFINING THE CLASS AS NATIVE TK FRAME
class NativeLeftPanel(tk.Frame):
    def __init__(self, parent, controller):
        # Use 'bg' instead of 'fg_color' for tk.Frame
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        # Grid config works the same
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 1. Input Area
        print("DEBUG: Creating Input Frame...")
        self.input_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_BORDER)
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self.input_frame, text="🔍 Escanear:", font=FONT_SUBHEADER, text_color=COLOR_TEXT).pack(side="left", padx=10, pady=10)
        ctk.CTkEntry(self.input_frame, width=200).pack(side="left", padx=10, pady=10)
        
        # 2. Info Frame
        print("DEBUG: Creating Info Frame...")
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        ctk.CTkLabel(self.info_frame, text="Info Mock").pack()

        # 3. Image Frame
        print("DEBUG: Creating Image Frame...")
        self.image_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=220)
        self.image_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self.image_frame, text="Image Mock").pack()

        # 4. Cart List - THE PROBLEMATIC PART
        print("DEBUG: Creating Cart Structure...")
        self.cart_container = tk.Frame(self, bg=COLOR_SURFACE, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.cart_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(5, 20))
        self.cart_container.grid_columnconfigure(0, weight=1)
        self.cart_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.cart_container, text="🛒 Carrito", font=FONT_SUBHEADER, text_color=COLOR_TEXT, bg_color=COLOR_SURFACE).grid(row=0, column=0, sticky="w")

        # Canvas
        self.cart_canvas = tk.Canvas(self.cart_container, bg=COLOR_SURFACE, highlightthickness=0)
        self.cart_scrollbar = ctk.CTkScrollbar(self.cart_container, command=self.cart_canvas.yview)
        self.cart_canvas.configure(yscrollcommand=self.cart_scrollbar.set)

        self.cart_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0,5), pady=5)
        self.cart_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.cart_frame = tk.Frame(self.cart_canvas, bg=COLOR_SURFACE)
        self.cart_window_id = self.cart_canvas.create_window((0, 0), window=self.cart_frame, anchor="nw")

        def _configure_inner_frame(event):
            self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
        def _configure_canvas(event):
            self.cart_canvas.itemconfig(self.cart_window_id, width=event.width)

        self.cart_frame.bind("<Configure>", _configure_inner_frame)
        self.cart_canvas.bind("<Configure>", _configure_canvas)
        print("DEBUG: Cart Structure Created.")

print("DEBUG: Starting Native Panel Test")
app = ctk.CTk()
app.geometry("800x600")
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

try:
    panel = NativeLeftPanel(app, MockController())
    panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    print("DEBUG: Mainloop...")
    app.mainloop()
except Exception as e:
    print(f"ERROR: {e}")
