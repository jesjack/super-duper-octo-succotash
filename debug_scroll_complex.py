import customtkinter as ctk
from ui.styles import *

# Mock Styles if import fails or to ensure consistency
# FONT_SUBHEADER = ("Segoe UI", 16, "bold") 
# COLOR_SURFACE = "#FFFFFF"
# COLOR_BORDER = "#E5E7EB"
# COLOR_TEXT = "#1F2937"

print("DEBUG: Starting Complex Scroll Test")

app = ctk.CTk()
app.geometry("800x600")

try:
    print("DEBUG: Creating Parent Frame (LeftPanel mock)...")
    left_panel = ctk.CTkFrame(app, fg_color="red") # Using red to see it
    left_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)
    
    # EXACT PARAMETERS FROM pos_app.py / LeftPanel
    # self.cart_frame = ctk.CTkScrollableFrame(self, label_text="🛒 Carrito de Compras", label_font=FONT_SUBHEADER, 
    #                                          fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER,
    #                                          label_text_color=COLOR_TEXT)
    
    print("DEBUG: Creating Scrollable Frame with Font 'Segoe UI'...")
    cart_frame = ctk.CTkScrollableFrame(
        left_panel, 
        label_text="🛒 Carrito de Compras", 
        label_font=("Segoe UI", 16, "bold"), # Directly using the font tuple
        fg_color=COLOR_SURFACE, 
        border_width=1, 
        border_color=COLOR_BORDER,
        label_text_color=COLOR_TEXT
    )
    print("DEBUG: Scrollable Frame Created successfully.")
    
    cart_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    print("DEBUG: Adding Items...")
    for i in range(5):
        ctk.CTkLabel(cart_frame, text=f"Item {i}", font=("Segoe UI", 14)).pack()

    print("DEBUG: Success! Entering Mainloop.")
    app.mainloop()

except Exception as e:
    print(f"ERROR: {e}")
except KeyboardInterrupt:
    print("Interrupted")
