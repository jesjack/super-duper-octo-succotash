import database
import win32print
from escpos.printer import Dummy
from PIL import Image
import barcode
from barcode.writer import ImageWriter
import os

def get_automatic_printer_name():
    try:
        printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        for p in printers:
            if "ThermalPrinter" in p: return p
        
        printers_2 = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS, None, 2)
        for p in printers_2:
            if "USB" in p[3] or "Generic" in p[4] or "Text Only" in p[4]:
                return p[1]
    except:
        pass
    return None

def print_product_label(printer_name, product):
    """
    Prints a single product label with Name, Price, and Barcode.
    """
    print(f"Printing label for: {product['name']}")
    
    # Generate Barcode Image
    code_text = product['barcode']
    
    # Use Code128 for flexibility
    BARCODE_CLASS = barcode.get_barcode_class('code128')
    my_barcode = BARCODE_CLASS(code_text, writer=ImageWriter())
    
    # Save to temp file
    filename = f"temp_barcode_{code_text}"
    fullname = my_barcode.save(filename)
    
    try:
        dummy = Dummy()
        dummy.hw("INIT")
        dummy.set(align='center')
        
        # Product Info
        dummy.text(f"{product['name'][:30]}\n")
        dummy.text(f"${product['price']:.2f}\n")
        
        # Resize image to fit printer (max ~380px)
        img = Image.open(fullname)
        max_width = 300
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            img.save("temp_resized_label.png")
            fullname = "temp_resized_label.png"
            
        dummy.image(fullname, impl="bitImageRaster")
        dummy.text("\n\n") # Space between labels
        dummy.cut()
        
        raw_data = dummy.output
        
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Label", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, raw_data)
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
            
    except Exception as e:
        print(f"Error printing label: {e}")
    finally:
        # Cleanup temp files
        try:
            if os.path.exists(filename + ".png"): os.remove(filename + ".png")
            if os.path.exists("temp_resized_label.png"): os.remove("temp_resized_label.png")
        except:
            pass

def main():
    print("Printing Product Catalog Barcodes...")
    
    printer_name = get_automatic_printer_name()
    if not printer_name:
        print("Printer not found.")
        return
    
    print(f"Using Printer: {printer_name}")
    
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        print("No products found in database. Run seed_data.py first.")
        return

    for p in products:
        print_product_label(printer_name, p)
        
    print("Done! All labels sent to printer.")

if __name__ == "__main__":
    main()
