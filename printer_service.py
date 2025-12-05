import win32print
from escpos.printer import Dummy
import datetime

class PrinterService:
    def __init__(self):
        self.printer_name = self._find_printer()
        
    def _find_printer(self):
        """
        Attempts to automatically find the thermal printer.
        """
        try:
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            
            # 1. Look for "ThermalPrinter" (User defined)
            for p in printers:
                if "ThermalPrinter" in p:
                    return p
            
            # 2. Look for USB/Generic ports
            printers_2 = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS, None, 2)
            for p in printers_2:
                if "USB" in p[3] or "Generic" in p[4] or "Text Only" in p[4]:
                    return p[1]
        except Exception as e:
            print(f"Printer detection error: {e}")
        
        return None

    def print_receipt(self, items, total, payment_method, cash_given=0, change=0):
        """
        items: list of dicts {'name', 'quantity', 'price', 'total'}
        """
        if not self.printer_name:
            print("No printer found. Skipping print.")
            return False

        try:
            dummy = Dummy()
            
            # Header
            dummy.hw("INIT")
            dummy.set(align='center')
            dummy.text("PUNTO DE VENTA\n")
            dummy.text("--------------------------------\n")
            dummy.text(f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            dummy.text("--------------------------------\n")
            dummy.set(align='left')
            
            # Items
            for item in items:
                # Format: Qty x Name ... Total
                # Truncate name if too long
                name = item['name'][:20]
                line = f"{item['quantity']} x {name:<20} ${item['total']:.2f}\n"
                dummy.text(line)
                
            dummy.text("--------------------------------\n")
            
            # Totals
            dummy.set(align='right')
            dummy.text(f"TOTAL: ${total:.2f}\n")
            dummy.text(f"PAGO: {payment_method}\n")
            if payment_method == "EFECTIVO":
                dummy.text(f"RECIBIDO: ${cash_given:.2f}\n")
                dummy.text(f"CAMBIO: ${change:.2f}\n")
            
            dummy.set(align='center')
            dummy.text("\nGracias por su compra!\n")
            dummy.text("\n") # Reduced spacing
            dummy.cut()
            
            # Send to Printer
            raw_data = dummy.output
            
            hPrinter = win32print.OpenPrinter(self.printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, raw_data)
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
                
            return True
            
        except Exception as e:
            print(f"Printing error: {e}")
            return False

if __name__ == "__main__":
    # Test
    ps = PrinterService()
    print(f"Found printer: {ps.printer_name}")
    if ps.printer_name:
        items = [
            {'name': 'Test Product A', 'quantity': 2, 'price': 10.50, 'total': 21.00},
            {'name': 'Coca Cola', 'quantity': 1, 'price': 18.00, 'total': 18.00}
        ]
        ps.print_receipt(items, 39.00, "CASH", 50.00, 11.00)
