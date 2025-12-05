import { API_URL, addLongPressListener, showProductDetailsOverlay } from './common.js';

let products = [];

export async function loadProducts() {
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
                <a href="/products/edit/${p.id}" class="btn-edit" style="text-decoration:none; padding: 0.3rem 0.6rem; border: 1px solid var(--primary); border-radius: 4px;">Editar</a>
                <button class="btn-delete" data-id="${p.id}">Borrar</button>
            </div>
        `;

        // Add Long Press
        addLongPressListener(li, () => showProductDetailsOverlay(p));

        // Add Delete Listener (since we can't use onclick with module scope easily without attaching to window)
        const deleteBtn = li.querySelector('.btn-delete');
        deleteBtn.addEventListener('click', () => deleteProduct(p.id));

        container.appendChild(li);
    });
}

async function deleteProduct(id) {
    if (!confirm("¿Seguro que deseas borrar este producto?")) return;
    const res = await fetch(`${API_URL}/products/${id}`, { method: 'DELETE' });
    if (res.status === 401) { window.location.href = '/login'; return; }
    loadProducts();
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
