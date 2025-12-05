// --- Logic ---
const API_URL = '/api';
let products = [];

// Picker Data (Sorted)
const TYPES = ["Blusa", "Camisa", "Chamarra", "Falda", "Leggins", "Pantalón", "Short", "Suéter", "Top", "Vestido"].sort();
const FABRICS = ["Algodón", "Encaje", "Licra", "Lino", "Mezclilla", "Poliéster", "Seda", "Vinil", "Lana"].sort();
const DETAILS = ["Acampanado", "Cargo", "Casual", "Corto", "Deportivo", "Estampado", "Formal", "Largo", "Liso", "Maternidad"].sort();

// Stats & Sales
async function loadStats() {
    const res = await fetch(`${API_URL}/stats`);
    if (res.status === 401) { window.location.href = '/login'; return; }
    const stats = await res.json();
    document.getElementById('total-revenue').textContent = `$${stats.total_revenue.toFixed(2)}`;

    const resSales = await fetch(`${API_URL}/sales`);
    const sales = await resSales.json();
    const list = document.getElementById('sales-list');
    list.innerHTML = ""; // Clear

    sales.forEach(s => {
        const li = document.createElement('li');
        li.className = "item-container";

        // Header
        const header = document.createElement('div');
        header.className = "item";
        // header.onclick = () => toggleSaleDetails(s.id); // modified by jesjack
        header.innerHTML = `
            <div class="item-info">
                <span class="item-name">Venta #${s.id}</span>
                <span class="item-meta">${s.timestamp} - ${s.payment_method}</span>
            </div>
            <div class="item-price">$${s.total.toFixed(2)}</div>
        `;
        li.appendChild(header);

        // Details
        const details = document.createElement('div');
        details.id = `sale-details-${s.id}`;
        details.className = "sale-details";
        details.style.display = "none";
        details.style.background = "#f9f9f9";
        details.style.padding = "10px";
        details.style.borderBottom = "1px solid #eee";

        s.items.forEach(i => {
            const row = document.createElement('div');
            row.className = "sale-item-row";
            row.style.display = "flex";
            row.style.alignItems = "center";
            row.style.marginBottom = "5px";

            // Construct product object for overlay
            const productObj = {
                name: i.name,
                barcode: i.barcode,
                price: i.price,
                image_path: i.image_path
            };

            // Add Long Press to Row
            addLongPressListener(row, () => showProductDetailsOverlay(productObj));

            row.innerHTML = `
                <img src="${i.image_path ? API_URL + '/uploads/' + i.image_path : '/static/placeholder.png'}" 
                     style="width:40px; height:40px; object-fit:cover; border-radius:4px; margin-right:10px;"
                     onerror="this.style.display='none'">
                <div style="flex:1;">
                    <div style="font-weight:bold; font-size:0.9rem;">${i.name}</div>
                    <div style="font-size:0.8rem; color:#666;">${i.barcode}</div>
                </div>
                <div style="font-size:0.9rem;">
                    ${i.quantity} x $${i.price.toFixed(2)}
                </div>
            `;
            details.appendChild(row);
        });

        li.appendChild(details);
        list.appendChild(li);
        toggleSaleDetails(s.id); // modified by jesjack porque necesito que esté siempre abierto ;)
    });
}

function toggleSaleDetails(id) {
    const el = document.getElementById(`sale-details-${id}`);
    if (el.style.display === 'none') {
        el.style.display = 'block';
    } else {
        el.style.display = 'none';
    }
}

// Products
async function loadProducts() {
    const res = await fetch(`${API_URL}/products`);
    if (res.status === 401) { window.location.href = '/login'; return; }
    products = await res.json();
    renderProducts(products);
}

function renderProducts(list) {
    const container = document.getElementById('products-list');
    container.innerHTML = "";

    list.forEach(p => {
        const li = document.createElement('li');
        li.className = "item";
        li.innerHTML = `
            <div class="item-info">
                <span class="item-name">${p.name}</span>
                <span class="item-meta">${p.barcode} - $${p.price.toFixed(2)}</span>
            </div>
            <div class="item-actions">
                <button class="btn-edit" onclick="editProduct(${p.id})">Editar</button>
                <button class="btn-delete" onclick="deleteProduct(${p.id})">Borrar</button>
            </div>
        `;

        // Add Long Press
        addLongPressListener(li, () => showProductDetailsOverlay(p));
        container.appendChild(li);
    });
}

// --- Long Press Logic ---
function addLongPressListener(element, callback) {
    let timer;

    const start = (e) => {
        if (e.type === 'click' && e.button !== 0) return;
        timer = setTimeout(() => {
            callback();
        }, 800); // 800ms long press
    };

    const end = () => {
        clearTimeout(timer);
    };

    element.addEventListener('mousedown', start);
    element.addEventListener('touchstart', start);

    element.addEventListener('mouseup', end);
    element.addEventListener('mouseleave', end);
    element.addEventListener('touchend', end);
    element.addEventListener('touchmove', end);

    // Prevent default context menu to avoid conflict with long press
    element.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });
}

function showProductDetailsOverlay(product) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.9)';
    overlay.style.zIndex = '2000';
    overlay.style.display = 'flex';
    overlay.style.flexDirection = 'column';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.color = 'white';
    // overlay.style.padding = '20px';
    overlay.onclick = () => document.body.removeChild(overlay);

    const imgPath = product.image_path ? `${API_URL}/uploads/${product.image_path}` : null;

    overlay.innerHTML = `
        <h2 style="margin-bottom:20px; text-align:center;">${product.name}</h2>
        ${imgPath ? `<img src="${imgPath}" style="max-width:90%; max-height:40vh; border-radius:8px; margin-bottom:20px;">` : '<div style="margin-bottom:20px; color:#aaa;">Sin Foto</div>'}
        
        <div style="background:white; padding:10px; border-radius:8px; margin-bottom:20px;">
            <img src="${API_URL}/preview_barcode?code=${product.barcode}" style="display:block; height:80px;">
            <div style="color:black; text-align:center; font-family:monospace; font-weight:bold; font-size:1.2rem;">${product.barcode}</div>
        </div>
        
        <div style="font-size:1.5rem; font-weight:bold;">$${product.price.toFixed(2)}</div>
        <p style="margin-top:20px; color:#ccc;">Toca para cerrar</p>
    `;

    document.body.appendChild(overlay);
}

// Search
const searchInput = document.getElementById('search-products');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = products.filter(p => p.name.toLowerCase().includes(term) || p.barcode.includes(term));
        renderProducts(filtered);
    });
}

// --- Wheel Picker Logic ---
const ITEM_HEIGHT = 50;

function initPickers() {
    // Populate with duplicates for infinite scroll illusion
    // Structure: [Buffer End] [Real Items] [Buffer Start]
    // We'll just repeat the list many times to make it feel infinite enough for practical use
    // Or use a smarter "reset scroll" approach.
    // Let's use the "reset scroll" approach with 3 copies: [Copy1] [Real] [Copy2]

    setupColumn('col-type', TYPES);
    setupColumn('col-fabric', FABRICS);
    setupColumn('col-detail', DETAILS);
}

function setupColumn(id, items) {
    const col = document.getElementById(id);
    if (!col) return;
    // Create 3 sets of items
    const allItems = [...items, ...items, ...items];

    col.innerHTML = allItems.map(item => `<div class="picker-item" data-val="${item}">${item}</div>`).join('');

    // Initial Scroll to middle set
    const middleIndex = items.length; // Start of middle set
    col.scrollTop = middleIndex * ITEM_HEIGHT;

    // Scroll Listener for Perspective & Infinite Loop
    col.addEventListener('scroll', () => {
        const scrollTop = col.scrollTop;
        const totalHeight = items.length * ITEM_HEIGHT;

        // Infinite Loop Logic
        if (scrollTop < ITEM_HEIGHT) {
            col.scrollTop = scrollTop + totalHeight;
            return;
        } else if (scrollTop > totalHeight * 2 - ITEM_HEIGHT) {
            col.scrollTop = scrollTop - totalHeight;
            return;
        }

        // Perspective Logic
        updatePerspective(col);
    });

    // Initial perspective update
    updatePerspective(col);
}

function updatePerspective(col) {
    const center = col.scrollTop + 75; // 150px height / 2 = 75
    const items = col.querySelectorAll('.picker-item');

    items.forEach(item => {
        const itemCenter = item.offsetTop + (ITEM_HEIGHT / 2);
        const dist = Math.abs(center - itemCenter);

        // Scale: 1.0 at center, down to 0.7 at edges
        let scale = 1 - (dist / 150) * 0.4;
        scale = Math.max(0.6, Math.min(1.2, scale)); // Clamp

        // Opacity: 1.0 at center, down to 0.3
        let opacity = 1 - (dist / 100) * 0.8;
        opacity = Math.max(0.2, Math.min(1, opacity));

        // Color highlight
        const isSelected = dist < ITEM_HEIGHT / 2;
        item.style.color = isSelected ? 'var(--primary)' : '#888';
        item.style.fontWeight = isSelected ? 'bold' : 'normal';

        item.style.transform = `scale(${scale})`;
        item.style.opacity = opacity;
    });
}

function getPickerValue(id) {
    const col = document.getElementById(id);
    // Find the item closest to center
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
    // We have 3 sets. Target the middle set.
    const baseIndex = itemsList.indexOf(value);
    if (baseIndex === -1) return;

    const targetIndex = itemsList.length + baseIndex; // Middle set
    col.scrollTop = targetIndex * ITEM_HEIGHT;
    updatePerspective(col);
}

// Modal
function openModal(product = null) {
    const modal = document.getElementById('product-modal');

    // Ensure pickers are populated
    const colType = document.getElementById('col-type');
    if (colType && colType.children.length === 0) {
        initPickers();
    }

    // Reset Image Input
    document.getElementById('prod-image').value = "";
    document.getElementById('image-preview-container').style.display = 'none';
    document.getElementById('image-preview').src = "";

    if (product) {
        document.getElementById('modal-title').textContent = "Editar Producto";
        document.getElementById('prod-id').value = product.id;
        document.getElementById('prod-barcode').value = product.barcode;
        document.getElementById('prod-price').value = product.price;

        // Show existing image if available
        if (product.image_path) {
            document.getElementById('image-preview').src = `${API_URL}/uploads/${product.image_path}`;
            document.getElementById('image-preview-container').style.display = 'block';
        }

        // Show barcode image with text below
        document.getElementById('barcode-container').innerHTML = `
            <div class="barcode-wrapper">
                <img src="${API_URL}/preview_barcode?code=${product.barcode}" alt="Barcode">
                <div class="barcode-text">${product.barcode}</div>
            </div>
        `;

        // Parse name
        const parts = product.name.split(' ');
        // Wait for modal render
        setTimeout(() => {
            setPickerValue('col-type', parts[0] || TYPES[0], TYPES);
            setPickerValue('col-fabric', parts[1] || FABRICS[0], FABRICS);
            setPickerValue('col-detail', parts.slice(2).join(' ') || DETAILS[0], DETAILS);
        }, 100);

    } else {
        document.getElementById('modal-title').textContent = "Nuevo Producto";
        document.getElementById('prod-id').value = "";

        // Auto-generate 6-digit barcode
        const randomBarcode = Math.floor(100000 + Math.random() * 900000).toString();
        document.getElementById('prod-barcode').value = randomBarcode;
        document.getElementById('barcode-container').innerHTML = `
            <div class="barcode-wrapper">
                <img src="${API_URL}/preview_barcode?code=${randomBarcode}" alt="Barcode">
                <div class="barcode-text">${randomBarcode}</div>
            </div>
        `;

        document.getElementById('prod-price').value = "";

        // Reset pickers to middle
        setTimeout(() => {
            setPickerValue('col-type', TYPES[0], TYPES);
            setPickerValue('col-fabric', FABRICS[0], FABRICS);
            setPickerValue('col-detail', DETAILS[0], DETAILS);
        }, 100);
    }
    modal.classList.add('open');
}

function closeModal() {
    document.getElementById('product-modal').classList.remove('open');
}

function editProduct(id) {
    const p = products.find(x => x.id === id);
    if (p) openModal(p);
}

async function deleteProduct(id) {
    if (!confirm("¿Seguro que deseas borrar este producto?")) return;
    const res = await fetch(`${API_URL}/products/${id}`, { method: 'DELETE' });
    if (res.status === 401) { window.location.href = '/login'; return; }
    loadProducts();
}

// Image Preview
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

async function saveProduct() {
    const id = document.getElementById('prod-id').value;

    const type = getPickerValue('col-type');
    const fabric = getPickerValue('col-fabric');
    const detail = getPickerValue('col-detail');
    const name = `${type} ${fabric} ${detail}`;

    const formData = new FormData();
    formData.append('barcode', document.getElementById('prod-barcode').value);
    formData.append('name', name);
    formData.append('price', document.getElementById('prod-price').value);

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
        body: formData // No Content-Type header, browser sets it with boundary
    });

    if (res.status === 401) { window.location.href = '/login'; return; }

    if (res.ok) {
        closeModal();
        loadProducts();
    } else {
        const err = await res.json();
        alert("Error: " + (err.error || "No se pudo guardar"));
    }
}
