import customtkinter as ctk
from tkinter import messagebox
from ui.styles import *

class CheckoutDialog(ctk.CTkToplevel):
    def __init__(self, parent, total_sum, on_confirm):
        super().__init__(parent, fg_color=COLOR_BACKGROUND)
        self.total_sum = total_sum
        self.on_confirm = on_confirm
        
        self.title("Cobrar")
        self.geometry("400x400")
        # Fix for Linux: wait for window to be viewable before grabbing focus
        self.after(200, lambda: self.grab_set())
        
        # Center relative to parent if possible, else screen center
        try:
            self.geometry(f"+{parent.winfo_x()+300}+{parent.winfo_y()+200}")
        except: pass
        
        ctk.CTkLabel(self, text=f"Total: ${total_sum:.2f}", font=FONT_HEADER, text_color=COLOR_TEXT).pack(pady=(30, 20))
        
        self.entry_cash = ctk.CTkEntry(self, placeholder_text="Efectivo Recibido", font=FONT_SUBHEADER, 
                                       height=INPUT_HEIGHT, border_color=COLOR_BORDER, fg_color=COLOR_SURFACE, text_color=COLOR_TEXT)
        self.entry_cash.pack(pady=10, padx=40, fill="x")
        self.entry_cash.focus_set()
        
        self.lbl_change = ctk.CTkLabel(self, text="Cambio: $0.00", font=FONT_SUBHEADER, text_color=COLOR_TEXT_LIGHT)
        self.lbl_change.pack(pady=10)
        
        self.entry_cash.bind("<KeyRelease>", self.calc_change)
        self.entry_cash.bind("<Return>", lambda e: self.confirm())

        ctk.CTkButton(self, text="✅ Confirmar (Enter)", command=self.confirm, 
                      fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
                      corner_radius=CORNER_RADIUS,
                      font=FONT_SUBHEADER, height=BUTTON_HEIGHT).pack(pady=30, padx=40, fill="x")

    def calc_change(self, event=None):
        try:
            txt = self.entry_cash.get()
            if not txt: return
            cash = float(txt)
            change = cash - self.total_sum
            self.lbl_change.configure(text=f"Cambio: ${change:.2f}", text_color=COLOR_SUCCESS if change >= 0 else COLOR_DANGER)
        except ValueError: pass

    def confirm(self):
        try:
            cash = float(self.entry_cash.get())
            if cash < self.total_sum:
                messagebox.showerror("Error", "Efectivo insuficiente.")
                self.after(100, lambda: self.entry_cash.focus_set())
                return
            
            change = cash - self.total_sum
            self.on_confirm(cash, change)
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.")
            self.after(100, lambda: self.entry_cash.focus_set())
