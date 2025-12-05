import json
import os
from pypdf import PdfReader
import database

def import_inventory_from_pdf(pdf_path):
    """
    Imports products and images from the generated inventory PDF.
    """
    try:
        reader = PdfReader(pdf_path)
        
        # 1. Extract JSON Database
        json_data = None
        
        # pypdf attachments are in reader.attachments (dict: filename -> list of bytes)
        # Note: pypdf structure for attachments can vary by version, but usually it's a dict
        # where keys are filenames and values are the bytes.
        
        if not reader.attachments:
             raise Exception("No attachments found in PDF")

        # Find inventory_db.json
        for filename, data in reader.attachments.items():
            if filename == 'inventory_db.json':
                # data is list of bytes in some versions, or bytes directly
                if isinstance(data, list):
                    data = b"".join(data)
                
                # Try decoding with different encodings
                try:
                    json_str = data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        json_str = data.decode('latin-1')
                    except:
                        # Fallback: try to find the JSON structure in raw bytes if pypdf added garbage
                        # This is a heuristic if direct decoding fails
                        try:
                            json_str = data.decode('utf-8', errors='ignore')
                        except:
                            raise Exception("Could not decode inventory_db.json")

                if not json_str or not json_str.strip():
                    raise Exception("inventory_db.json is empty")

                try:
                    json_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    # Log first 100 chars to help debug
                    snippet = json_str[:100] if json_str else "EMPTY"
                    raise Exception(f"Invalid JSON format: {e}. Content snippet: '{snippet}'")
                    
                break
        
        if not json_data:
            raise Exception("inventory_db.json not found in PDF")

        # 2. Process Products
        imported_count = 0
        updated_count = 0
        
        # Ensure images directory exists
        img_dir = os.path.join("static", "images", "products")
        os.makedirs(img_dir, exist_ok=True)

        for p in json_data:
            barcode = p.get('barcode')
            name = p.get('name')
            price = float(p.get('price', 0))
            image_filename = p.get('image_filename')
            
            # Save Image if exists
            saved_image_path = None
            if image_filename and image_filename in reader.attachments:
                img_data = reader.attachments[image_filename]
                if isinstance(img_data, list):
                    img_data = b"".join(img_data)
                
                # Save to static/images/products/
                # Use barcode as filename to ensure uniqueness/consistency
                ext = os.path.splitext(image_filename)[1]
                target_filename = f"{barcode}{ext}"
                target_path = os.path.join(img_dir, target_filename)
                
                with open(target_path, "wb") as f:
                    f.write(img_data)
                
                # Path relative to static folder for DB (or absolute? DB usually stores relative or full)
                # Looking at database.py, it seems to store just the path. 
                # Let's store relative to static folder: "images/products/..."
                saved_image_path = f"images/products/{target_filename}"

            # Update or Insert into DB
            existing = database.get_product_by_barcode(barcode)
            if existing:
                # Update
                # Only update image if we have a new one, otherwise keep existing?
                # Or overwrite? Let's overwrite if we have one.
                final_img_path = saved_image_path if saved_image_path else existing['image_path']
                database.update_product(existing['id'], barcode, name, price, final_img_path)
                updated_count += 1
            else:
                # Insert
                database.add_product(barcode, name, price, saved_image_path)
                imported_count += 1

        return True, f"Importado: {imported_count} nuevos, {updated_count} actualizados."

    except Exception as e:
        return False, str(e)
