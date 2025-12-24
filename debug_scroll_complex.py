import customtkinter as ctk

# Match POSApp settings
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Styles from ui/styles.py
COLOR_BACKGROUND = "#F3F4F6"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT = "#1F2937"
COLOR_BORDER = "#E5E7EB"
FONT_SUBHEADER = ("Segoe UI", 16, "bold")

app = ctk.CTk(fg_color=COLOR_BACKGROUND)
app.geometry("1024x768")
app.title("Debug Complex Grid")

# Layout Configuration (Same as POSApp)
app.grid_columnconfigure(0, weight=1) # Column 0 in app is LeftPanel
app.grid_rowconfigure(0, weight=1)

print("DEBUG: Creating LeftPanel Frame (Mock)...")
# LeftPanel matches POSApp logic
left_panel = ctk.CTkFrame(app, fg_color=COLOR_BACKGROUND)
left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# LeftPanel internal grid config
left_panel.grid_columnconfigure(0, weight=1)
left_panel.grid_rowconfigure(3, weight=1) # Row 3 is Cart Frame

try:
    # 1. Input Frame
    print("DEBUG: Creating Input Frame...")
    input_frame = ctk.CTkFrame(left_panel, fg_color=COLOR_SURFACE)
    input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
    ctk.CTkLabel(input_frame, text="Input Mock").pack()

    # 2. Info Frame
    print("DEBUG: Creating Info Frame...")
    info_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
    info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
    ctk.CTkLabel(info_frame, text="Info Mock").pack()

    # 3. Image Frame
    print("DEBUG: Creating Image Frame...")
    image_frame = ctk.CTkFrame(left_panel, fg_color=COLOR_SURFACE, height=220)
    image_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
    image_frame.pack_propagate(False)
    ctk.CTkLabel(image_frame, text="Image Mock").pack()

    # 4. Cart Frame (THE SUSPECT)
    print("DEBUG: Creating Scrollable Cart Frame...")
    # NOTE: Exact parameters from LeftPanel
    cart_frame = ctk.CTkScrollableFrame(
        left_panel, 
        label_text="🛒 Carrito de Compras", 
        label_font=FONT_SUBHEADER, 
        fg_color=COLOR_SURFACE, 
        border_width=1, 
        border_color=COLOR_BORDER,
        label_text_color=COLOR_TEXT
    )
    print("DEBUG: Scrollable Frame Created.")
    
    print("DEBUG: Gridding Cart Frame...")
    cart_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(5, 20))
    print("DEBUG: Cart Frame Gridded.")

    # Add content
    for i in range(5):
        ctk.CTkLabel(cart_frame, text=f"Item {i}").pack()

    print("DEBUG: Initialized successfully. Entering Mainloop.")
    app.mainloop()

except Exception as e:
    print(f"ERROR: {e}")
