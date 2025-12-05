import { API_URL } from './common.js';

// Picker Data (Sorted)
const TYPES = ["Blusa", "Camisa", "Chamarra", "Falda", "Leggins", "Pantalón", "Short", "Suéter", "Top", "Vestido"].sort();
const FABRICS = ["Algodón", "Encaje", "Licra", "Lino", "Mezclilla", "Poliéster", "Seda", "Vinil", "Lana"].sort();
const DETAILS = ["Acampanado", "Cargo", "Casual", "Corto", "Deportivo", "Estampado", "Formal", "Largo", "Liso", "Maternidad"].sort();

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const ITEM_HEIGHT = 50;

export async function initProductForm() {
    initPickers();
    setupImagePreview();
    setupSaveButton();

    // Check if editing
    const path = window.location.pathname;
    const match = path.match(/\/products\/edit\/(\d+)/);

    if (match) {
        const id = match[1];
        await loadProductData(id);
    } else {
        // New Product
        document.getElementById('form-title').textContent = "Nuevo Producto";

        // Auto-generate 6-digit barcode
        const randomBarcode = Math.floor(100000 + Math.random() * 900000).toString();
        document.getElementById('prod-barcode').value = randomBarcode;
        document.getElementById('barcode-container').innerHTML = `
            <div class="barcode-wrapper">
                <img src="${API_URL}/preview_barcode?code=${randomBarcode}" alt="Barcode">
                <div class="barcode-text">${randomBarcode}</div>
            </div>
        `;

        // Reset pickers to middle (Name) and 0 (Price)
        setTimeout(() => {
            setPickerValue('col-type', TYPES[0], TYPES);
            setPickerValue('col-fabric', FABRICS[0], FABRICS);
            setPickerValue('col-detail', DETAILS[0], DETAILS);

            setPickerValue('col-price-100', 0, DIGITS);
            setPickerValue('col-price-10', 0, DIGITS);
            setPickerValue('col-price-1', 0, DIGITS);
        }, 100);
    }
}

async function loadProductData(id) {
    document.getElementById('form-title').textContent = "Editar Producto";

    const res = await fetch(`${API_URL}/products`);
    const allProducts = await res.json();
    const product = allProducts.find(p => p.id == id);

    if (!product) {
        alert("Producto no encontrado");
        window.location.href = '/products';
        return;
    }

    document.getElementById('prod-id').value = product.id;
    document.getElementById('prod-barcode').value = product.barcode;
    // document.getElementById('prod-price').value = product.price; // No longer used directly

    // Show existing image if available
    if (product.image_path) {
        document.getElementById('image-preview').src = `${API_URL}/uploads/${product.image_path}`;
        document.getElementById('image-preview-container').style.display = 'block';
    }

    // Show barcode image
    document.getElementById('barcode-container').innerHTML = `
        <div class="barcode-wrapper">
            <img src="${API_URL}/preview_barcode?code=${product.barcode}" alt="Barcode">
            <div class="barcode-text">${product.barcode}</div>
        </div>
    `;

    // Parse name to set pickers
    const parts = product.name.split(' ');

    // Parse price to set pickers
    const priceInt = Math.floor(product.price);
    const hundreds = Math.floor(priceInt / 100) % 10;
    const tens = Math.floor(priceInt / 10) % 10;
    const units = priceInt % 10;

    setTimeout(() => {
        setPickerValue('col-type', parts[0] || TYPES[0], TYPES);
        setPickerValue('col-fabric', parts[1] || FABRICS[0], FABRICS);
        setPickerValue('col-detail', parts.slice(2).join(' ') || DETAILS[0], DETAILS);

        setPickerValue('col-price-100', hundreds, DIGITS);
        setPickerValue('col-price-10', tens, DIGITS);
        setPickerValue('col-price-1', units, DIGITS);
    }, 100);
}

function setupImagePreview() {
    const prodImageInput = document.getElementById('prod-image');
    if (prodImageInput) {
        prodImageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    document.getElementById('image-preview').src = e.target.result;
                    document.getElementById('image-preview-container').style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }
}

function setupSaveButton() {
    document.getElementById('btn-save').addEventListener('click', saveProduct);
}

async function saveProduct() {
    const id = document.getElementById('prod-id').value;

    const type = getPickerValue('col-type');
    const fabric = getPickerValue('col-fabric');
    const detail = getPickerValue('col-detail');
    const name = `${type} ${fabric} ${detail}`;

    // Construct Price
    const p100 = getPickerValue('col-price-100');
    const p10 = getPickerValue('col-price-10');
    const p1 = getPickerValue('col-price-1');
    const price = parseInt(p100) * 100 + parseInt(p10) * 10 + parseInt(p1);

    const formData = new FormData();
    formData.append('barcode', document.getElementById('prod-barcode').value);
    formData.append('name', name);
    formData.append('price', price);

    const imageFile = document.getElementById('prod-image').files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }

    if (!formData.get('barcode') || !formData.get('name') || !formData.get('price')) {
        alert("Todos los campos son obligatorios");
        return;
    }

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/products/${id}` : `${API_URL}/products`;

    const res = await fetch(url, {
        method: method,
        body: formData
    });

    if (res.status === 401) { window.location.href = '/login'; return; }

    if (res.ok) {
        window.location.href = '/products';
    } else {
        const err = await res.json();
        alert("Error: " + (err.error || "No se pudo guardar"));
    }
}

// --- Wheel Picker Logic (Copied & Adapted) ---
function initPickers() {
    setupColumn('col-type', TYPES);
    setupColumn('col-fabric', FABRICS);
    setupColumn('col-detail', DETAILS);

    setupColumn('col-price-100', DIGITS);
    setupColumn('col-price-10', DIGITS);
    setupColumn('col-price-1', DIGITS);
}

function setupColumn(id, items) {
    const col = document.getElementById(id);
    if (!col) return;
    const allItems = [...items, ...items, ...items];

    col.innerHTML = allItems.map(item => `<div class="picker-item" data-val="${item}">${item}</div>`).join('');

    const middleIndex = items.length;
    col.scrollTop = middleIndex * ITEM_HEIGHT;

    col.addEventListener('scroll', () => {
        const scrollTop = col.scrollTop;
        const totalHeight = items.length * ITEM_HEIGHT;

        if (scrollTop < ITEM_HEIGHT) {
            col.scrollTop = scrollTop + totalHeight;
            return;
        } else if (scrollTop > totalHeight * 2 - ITEM_HEIGHT) {
            col.scrollTop = scrollTop - totalHeight;
            return;
        }
        updatePerspective(col);
    });

    updatePerspective(col);
}

function updatePerspective(col) {
    const center = col.scrollTop + 75;
    const items = col.querySelectorAll('.picker-item');

    items.forEach(item => {
        const itemCenter = item.offsetTop + (ITEM_HEIGHT / 2);
        const dist = Math.abs(center - itemCenter);

        let scale = 1 - (dist / 150) * 0.4;
        scale = Math.max(0.6, Math.min(1.2, scale));

        let opacity = 1 - (dist / 100) * 0.8;
        opacity = Math.max(0.2, Math.min(1, opacity));

        const isSelected = dist < ITEM_HEIGHT / 2;
        item.style.color = isSelected ? 'var(--primary)' : '#888';
        item.style.fontWeight = isSelected ? 'bold' : 'normal';

        item.style.transform = `scale(${scale})`;
        item.style.opacity = opacity;
    });
}

function getPickerValue(id) {
    const col = document.getElementById(id);
    const center = col.scrollTop + 75;
    const items = Array.from(col.querySelectorAll('.picker-item'));

    let closest = null;
    let minDist = Infinity;

    items.forEach(item => {
        const itemCenter = item.offsetTop + (ITEM_HEIGHT / 2);
        const dist = Math.abs(center - itemCenter);
        if (dist < minDist) {
            minDist = dist;
            closest = item;
        }
    });

    return closest ? closest.dataset.val : "";
}

function setPickerValue(id, value, itemsList) {
    const col = document.getElementById(id);
    if (!col) return;
    const baseIndex = itemsList.indexOf(value);
    if (baseIndex === -1) return;

    const targetIndex = itemsList.length + baseIndex;
    col.scrollTop = targetIndex * ITEM_HEIGHT;
    updatePerspective(col);
}
