import wmi

def list_usb_devices():
    c = wmi.WMI()
    print("Scanning for USB devices...")
    print("-" * 60)
    print(f"{'Device Name':<40} | {'Device ID':<40}")
    print("-" * 60)
    
    found_printer = False
    found_scanner = False

    for device in c.Win32_PnPEntity():
        if device.DeviceID and 'USB' in device.DeviceID:
            name = device.Name or "Unknown"
            device_id = device.DeviceID
            
            # Highlight potential target devices
            prefix = "  "
            if "print" in name.lower() or "pos" in name.lower():
                prefix = ">>"
                found_printer = True
            if "scan" in name.lower() or "barcode" in name.lower() or "keyboard" in name.lower(): # Scanners often appear as keyboards
                prefix = ">>"
                found_scanner = True
                
            print(f"{prefix} {name:<38} | {device_id}")

    print("-" * 60)
    if not found_printer:
        print("WARNING: No obvious printer found. Look for 'USB Printing Support' or specific brand names.")
    if not found_scanner:
        print("NOTE: Barcode scanners often appear as 'HID Keyboard Device'. Look for generic input devices if not explicitly named.")

if __name__ == "__main__":
    try:
        list_usb_devices()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure pywin32 and wmi are installed.")
