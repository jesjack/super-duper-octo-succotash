from flask import Blueprint, request, jsonify, send_file, send_from_directory, current_app
import database
import io
import os
import barcode
from barcode.writer import ImageWriter
from routes.auth import login_required
from PIL import Image
from werkzeug.utils import secure_filename

products_bp = Blueprint('products', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique filename to prevent overwrite issues
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Ensure directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        return unique_filename
    return None

@products_bp.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename)

@products_bp.route('/api/preview_barcode')
def preview_barcode():
    code = request.args.get('code')
    if not code:
        return "Missing code", 400
    
    try:
        # Generate Barcode Image
        # Code128 is flexible. 
        # options: write_text=False to hide text.
        # module_height: default is 15mm. User wants ~3cm (30mm).
        # module_width: default is 0.2mm.
        
        EAN = barcode.get_barcode_class('code128')
        ean = EAN(code, writer=ImageWriter())
        
        # Render to BytesIO first
        fp = io.BytesIO()
        # write_text=False disables the number
        # quiet_zone=1 ensures we don't have massive whitespace
        ean.write(fp, options={'write_text': False, 'quiet_zone': 1, 'module_height': 15.0})
        fp.seek(0)
        
        # Post-process for Transparency using Pillow
        img = Image.open(fp).convert("RGBA")
        
        # Make white background transparent
        datas = img.getdata()
        new_data = []
        for item in datas:
            # If pixel is white (or very close), make it transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        
        # Save final transparent image
        final_fp = io.BytesIO()
        img.save(final_fp, format="PNG")
        final_fp.seek(0)
        
        return send_file(final_fp, mimetype='image/png')
    except Exception as e:
        return str(e), 500

@products_bp.route('/api/products', methods=['GET'])
@login_required
def get_products():
    products = database.get_all_products()
    return jsonify(products)

@products_bp.route('/api/products', methods=['POST'])
@login_required
def add_product():
    # Handle multipart/form-data
    name = request.form.get('name')
    barcode = request.form.get('barcode')
    price = request.form.get('price')
    
    if not name or not barcode or not price:
        return jsonify({'error': 'Missing fields'}), 400
        
    image_path = None
    if 'image' in request.files:
        image_path = save_image(request.files['image'])

    success = database.add_product(barcode, name, float(price), image_path)
    if success:
        return jsonify({'message': 'Product added'}), 201
    else:
        return jsonify({'error': 'Barcode already exists'}), 400

@products_bp.route('/api/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    # Handle multipart/form-data
    name = request.form.get('name')
    barcode = request.form.get('barcode')
    price = request.form.get('price')
    
    image_path = None
    if 'image' in request.files:
        image_path = save_image(request.files['image'])
        
    # If no new image, keep existing (logic handled in database.py if None passed? 
    # No, database.py replaces if passed. We need to handle "keep existing" logic.
    # Actually database.py logic I wrote: if image_path: update it. else: don't update it.
    # So passing None is safe to keep existing.
    
    success = database.update_product(id, barcode, name, float(price), image_path)
    if success:
        return jsonify({'message': 'Product updated'})
    else:
        return jsonify({'error': 'Update failed'}), 400

@products_bp.route('/api/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    database.delete_product(id)
    return jsonify({'message': 'Product deleted'})
