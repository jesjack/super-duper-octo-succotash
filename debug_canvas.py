import customtkinter as ctk
import tkinter as tk

# Match POSApp settings
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Styles
COLOR_BACKGROUND = "#F3F4F6"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT = "#1F2937"
COLOR_BORDER = "#E5E7EB"
FONT_SUBHEADER = ("Segoe UI", 16, "bold")

app = ctk.CTk(fg_color=COLOR_BACKGROUND)
app.geometry("800x600")
app.title("Debug Canvas Fix")

app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

print("DEBUG: Creating LeftPanel Frame...")
left_panel = ctk.CTkFrame(app, fg_color=COLOR_BACKGROUND)
left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

left_panel.grid_columnconfigure(0, weight=1)
left_panel.grid_rowconfigure(1, weight=1)

try:
    print("DEBUG: Creating Header...")
    ctk.CTkLabel(left_panel, text="Header").grid(row=0, column=0)

    # REPLICATING THE FIX EXACTLY
    print("DEBUG: Creating Cart Container (CTkFrame)...")
    cart_container = ctk.CTkFrame(left_panel, fg_color=COLOR_SURFACE, border_width=1, border_color=COLOR_BORDER)
    cart_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
    cart_container.grid_columnconfigure(0, weight=1)
    cart_container.grid_rowconfigure(1, weight=1)
    print("DEBUG: Cart Container Created.")

    print("DEBUG: Creating Header Label...")
    cart_header = ctk.CTkLabel(cart_container, text="🛒 Carrito de Compras", font=FONT_SUBHEADER, text_color=COLOR_TEXT)
    cart_header.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    print("DEBUG: Creating Canvas & Scrollbar...")
    cart_canvas = tk.Canvas(cart_container, bg=COLOR_SURFACE, highlightthickness=0)
    cart_scrollbar = ctk.CTkScrollbar(cart_container, command=cart_canvas.yview)
    cart_canvas.configure(yscrollcommand=cart_scrollbar.set)

    cart_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0,5), pady=5)
    cart_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    print("DEBUG: Canvas Created.")

    print("DEBUG: Creating Inner Frame...")
    cart_frame = ctk.CTkFrame(cart_canvas, fg_color=COLOR_SURFACE)
    cart_window_id = cart_canvas.create_window((0, 0), window=cart_frame, anchor="nw")
    print("DEBUG: Inner Frame Created.")

    def _configure_cart_frame(event):
        cart_canvas.configure(scrollregion=cart_canvas.bbox("all"))
        cart_canvas.itemconfig(cart_window_id, width=event.width)

    cart_frame.bind("<Configure>", _configure_cart_frame)
    cart_canvas.bind("<Configure>", lambda e: cart_canvas.itemconfig(cart_window_id, width=e.width))

    # Add items
    print("DEBUG: Adding items...")
    for i in range(20):
        ctk.CTkLabel(cart_frame, text=f"Item de prueba {i}", text_color="black").pack(pady=2)

    print("DEBUG: Success! Entering Mainloop.")
    app.mainloop()

except Exception as e:
    print(f"ERROR: {e}")
