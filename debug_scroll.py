import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x300")
app.title("Test Scrollable")

print("DEBUG: Creating Standard Frame...")
frame = ctk.CTkFrame(app, height=50, fg_color="green")
frame.pack(pady=10)
print("DEBUG: Standard Frame Created.")

try:
    print("DEBUG: Creating Scrollable Frame...")
    scroll = ctk.CTkScrollableFrame(app, width=300, height=100, label_text="Test Scroll")
    scroll.pack(pady=10)
    print("DEBUG: Scrollable Frame Created!")
    
    for i in range(10):
        ctk.CTkLabel(scroll, text=f"Item {i}").pack()
        
except Exception as e:
    print(f"ERROR: {e}")

print("DEBUG: Starting Mainloop...")
app.mainloop()
