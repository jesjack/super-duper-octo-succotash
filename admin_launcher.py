import webview
import sys
import threading
import time
import requests

def wait_for_server():
    """Wait until the backend server is reachable."""
    max_retries = 10
    for _ in range(max_retries):
        try:
            requests.get("http://127.0.0.1:5000/api/server_status", timeout=1)
            return True
        except:
            time.sleep(0.5)
    return False

if __name__ == '__main__':
    # Ensure backend is ready
    if not wait_for_server():
        print("Error: Backend server not reachable.")
        sys.exit(1)

    # Create a standard window pointing to the dashboard
    # width/height match the previous native window size roughly
    window = webview.create_window('Administración - Ventas del Día', 'http://127.0.0.1:5000/', width=1024, height=768)
    
    def on_closing():
        try:
            # Hide window immediately for instant visual feedback
            window.hide()
            
            # Force kill process immediately using os.kill (SIGTERM/SIGKILL equivalent on Windows)
            import os, signal
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception as e:
            print(f"Error closing: {e}")
            import os
            os._exit(1)
        return False
        
    window.events.closing += on_closing
    
    webview.start()
