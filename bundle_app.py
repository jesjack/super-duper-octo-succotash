import os
import re

BASE_DIR = r'c:\Users\jesja\PycharmProjects\punto_venta\inventory_setup'
INPUT_FILE = os.path.join(BASE_DIR, 'index.html')
OUTPUT_FILE = os.path.join(BASE_DIR, 'inventory_app_bundled.html')

def bundle_html(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find script tags with src
    # <script src="path/to/file.js"></script>
    script_pattern = re.compile(r'<script\s+src=["\']([^"\']+)["\']\s*></script>')

    def replace_script(match):
        src = match.group(1)
        # Resolve path relative to index.html
        file_path = os.path.join(BASE_DIR, src)
        
        if os.path.exists(file_path):
            print(f"Bundling {src}...")
            with open(file_path, 'r', encoding='utf-8') as js_file:
                js_content = js_file.read()
            return f'<script>\n/* Source: {src} */\n{js_content}\n</script>'
        else:
            print(f"Warning: Could not find {src}")
            return match.group(0)

    bundled_content = script_pattern.sub(replace_script, content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(bundled_content)
    
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    bundle_html(INPUT_FILE, OUTPUT_FILE)
