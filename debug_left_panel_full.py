import customtkinter as ctk
from ui.left_panel import LeftPanel
import sys

# Mock Controller
class MockController:
    def process_barcode(self, code):
        print(f"Controller: MOCK process {code}")

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

print("DEBUG: Starting LeftPanel Full Class Test")

app = ctk.CTk()
app.geometry("800x600")
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

try:
    print("DEBUG: Instantiating LeftPanel...")
    controller = MockController()
    left_panel = LeftPanel(app, controller)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    print("DEBUG: LeftPanel Instantiated and Gridded.")

    print("DEBUG: Starting Mainloop...")
    app.mainloop()

except Exception as e:
    print(f"ERROR: {e}")
