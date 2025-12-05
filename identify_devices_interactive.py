import subprocess
import time
import sys

def get_usb_devices():
    """Executes the PowerShell command to get USB devices and returns a set of (InstanceId, FriendlyName)."""
    cmd = "Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' } | Select-Object InstanceId, FriendlyName | Format-Table -HideTableHeaders"
    try:
        # Run PowerShell command
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
        devices = set()
        for line in result.stdout.splitlines():
            if line.strip():
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    devices.add((parts[0].strip(), parts[1].strip()))
                elif len(parts) == 1:
                     devices.add((parts[0].strip(), "Unknown"))
        return devices
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell: {e}")
        return set()

def main():
    print("Interactive Hardware Identification")
    print("===================================")
    print("This script will help identify your Printer and Scanner by detecting changes.")
    
    while True:
        target = input("\nWhat device do you want to identify? (printer/scanner/exit): ").strip().lower()
        if target == 'exit':
            break
        if target not in ['printer', 'scanner']:
            print("Please type 'printer' or 'scanner'.")
            continue

        print(f"\nStep 1: Ensure the {target} is CONNECTED.")
        input("Press Enter when ready...")
        print("Scanning...")
        connected_devices = get_usb_devices()
        print(f"Found {len(connected_devices)} USB devices.")

        print(f"\nStep 2: UNPLUG the {target}.")
        input("Press Enter when ready...")
        print("Scanning...")
        disconnected_devices = get_usb_devices()
        
        # Find the difference
        diff = connected_devices - disconnected_devices
        
        if not diff:
            print(f"No device disappearance detected. Did you unplug it?")
            # Try the reverse (plugging in)
            print("Let's try the reverse. Leave it UNPLUGGED.")
            input("Press Enter to rescan baseline...")
            disconnected_devices = get_usb_devices()
            print(f"\nStep 3: PLUG IN the {target}.")
            input("Press Enter when ready...")
            connected_devices = get_usb_devices()
            diff = connected_devices - disconnected_devices

        if diff:
            print(f"\nSUCCESS! Identified {target}:")
            for dev_id, name in diff:
                print(f"  Name: {name}")
                print(f"  ID:   {dev_id}")
                
                # Extract VID/PID if possible
                if "VID_" in dev_id and "PID_" in dev_id:
                    try:
                        vid = dev_id.split("VID_")[1][:4]
                        pid = dev_id.split("PID_")[1][:4]
                        print(f"  VID:  0x{vid}")
                        print(f"  PID:  0x{pid}")
                    except:
                        pass
        else:
            print("Could not detect any changes. Make sure the device is actually communicating with Windows.")

if __name__ == "__main__":
    main()
