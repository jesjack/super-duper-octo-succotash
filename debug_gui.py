import customtkinter as ctk
import sys

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

print("DEBUG: Inicio de script debug_gui.py")
print(f"DEBUG: Python {sys.version}")

try:
    print("DEBUG: Creando instancia CTk...")
    app = ctk.CTk()
    app.geometry("400x240")
    app.title("Test GUI")

    print("DEBUG: Creando botón...")
    def hello():
        print("Click!")
    
    button = ctk.CTkButton(app, text="Click Interactivo", command=hello)
    button.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    print("DEBUG: Entrando a mainloop...")
    app.mainloop()
    print("DEBUG: Mainloop finalizado.")

except Exception as e:
    print(f"ERROR CRITICO: {e}")
except KeyboardInterrupt:
    print("Interrumpido por usuario")
