import customtkinter as ctk
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

print("DEBUG: Starting Component Test")

app = ctk.CTk()
app.geometry("600x400")

try:
    # 1. Test Entry
    print("DEBUG: Creating Frame for Entry...")
    frame1 = ctk.CTkFrame(app)
    frame1.pack(pady=10)
    
    print("DEBUG: Creating CTkEntry (Segoe UI 16 bold)...")
    # Exact settings from LeftPanel
    # font=FONT_SUBHEADER -> ("Segoe UI", 16, "bold")
    entry = ctk.CTkEntry(frame1, width=350, font=("Segoe UI", 16, "bold"))
    entry.pack(padx=10, pady=10)
    print("DEBUG: CTkEntry Created.")
    
    # 2. Test Image (PIL)
    print("DEBUG: Testing PIL Image creation...")
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    
    print("DEBUG: Creating CTkImage...")
    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
    
    print("DEBUG: Creating Label with Image...")
    lbl = ctk.CTkLabel(app, text="", image=ctk_img)
    lbl.pack(pady=10)
    print("DEBUG: Image Label Created.")

    print("DEBUG: Success! Entering Mainloop.")
    app.mainloop()

except Exception as e:
    print(f"ERROR: {e}")
