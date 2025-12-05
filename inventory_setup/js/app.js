const app = {
    data: {
        products: []
    },

    // --- IndexedDB Helper ---
    db: null,

    initDB: function () {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open("InventoryDB", 1);

            request.onerror = (event) => {
                console.error("IndexedDB error:", event.target.error);
                reject("Error opening database");
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains("products")) {
                    db.createObjectStore("products", { keyPath: "id" });
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve();
            };
        });
    },

    init: async function () {
        try {
            await this.loadData();
        } catch (e) {
            console.error("Error loading data:", e);
        }
        this.renderList();
    },

    navigate: function (viewId) {
        document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
        document.getElementById('view-' + viewId).classList.add('active');

        if (viewId === 'capture') {
            this.resetForm();
        } else if (viewId === 'home') {
            this.renderList();
        }
    },

    handleImage: function (input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.getElementById('img-preview');
                img.src = e.target.result;
                img.style.display = 'block';
                document.getElementById('camera-placeholder').style.display = 'none';
            }
            reader.readAsDataURL(input.files[0]);
        }
    },

    getNextBarcode: function () {
        if (this.data.products.length === 0) return "000001";

        // Find max barcode
        let max = 0;
        this.data.products.forEach(p => {
            const val = parseInt(p.barcode);
            if (!isNaN(val) && val > max) max = val;
        });

        const next = max + 1;
        return next.toString().padStart(6, '0');
    },

    adjustQty: function (id, delta) {
        const el = document.getElementById(id);
        let val = parseInt(el.value) || 0;
        val += delta;
        if (val < 1) val = 1;
        el.value = val;
    },

    saveProduct: async function () {
        // Auto-generate barcode
        const barcode = this.getNextBarcode();
        const name = document.getElementById('inp-name').value.trim();
        const price = document.getElementById('inp-price').value.trim();
        const qty = parseInt(document.getElementById('inp-qty').value) || 1;
        const imgSrc = document.getElementById('img-preview').src;

        if (!name || !price) {
            alert("Nombre y Precio son obligatorios");
            return;
        }

        const product = {
            id: Date.now().toString(),
            barcode,
            name,
            price: parseFloat(price) || 0,
            qty,
            image: imgSrc.startsWith('data:') ? imgSrc : null
        };

        this.data.products.push(product);

        try {
            await this.saveData();
            this.navigate('home');
        } catch (e) {
            alert("Error guardando: " + e);
        }
    },

    deleteProduct: async function (id) {
        if (confirm("¿Eliminar producto?")) {
            this.data.products = this.data.products.filter(p => p.id !== id);
            await this.saveData();
            this.renderList();
        }
    },

    updateProductQty: async function (id, newQty) {
        const p = this.data.products.find(p => p.id === id);
        if (p) {
            p.qty = parseInt(newQty);
            await this.saveData();
        }
    },

    renderList: function () {
        const container = document.getElementById('product-list');
        if (this.data.products.length === 0) {
            container.innerHTML = '<div style="text-align: center; padding: 40px; color: #888;">No hay productos.<br>Toca + para agregar.</div>';
            return;
        }

        container.innerHTML = this.data.products.map(p => `
            <div class="product-item">
                <img src="${p.image || 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MCIgaGVpZ2h0PSI1MCI+PHJlY3Qgd2lkdGg9IjUwIiBoZWlnaHQ9IjUwIiBmaWxsPSIjZWVlIi8+PC9zdmc+'}" class="product-thumb">
                <div class="product-info">
                    <div class="product-name">${p.name}</div>
                    <div class="product-meta">${p.barcode}</div>
                </div>
                <div class="qty-control">
                    <div class="qty-btn" onclick="app.updateProductQty('${p.id}', ${p.qty - 1}); app.renderList()">-</div>
                    <span style="width: 30px; text-align: center;">${p.qty}</span>
                    <div class="qty-btn" onclick="app.updateProductQty('${p.id}', ${p.qty + 1}); app.renderList()">+</div>
                </div>
                <button class="btn btn-outline" style="width: auto; margin: 0; padding: 4px 8px; border: none; color: #b00020;" onclick="app.deleteProduct('${p.id}')">🗑️</button>
            </div>
        `).join('');
    },

    resetForm: function () {
        document.getElementById('inp-name').value = '';
        document.getElementById('inp-price').value = '';
        document.getElementById('inp-qty').value = '1';
        document.getElementById('img-preview').src = '';
        document.getElementById('img-preview').style.display = 'none';
        document.getElementById('camera-placeholder').style.display = 'block';
        document.getElementById('inp-camera').value = '';
    },

    saveData: async function () {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(["products"], "readwrite");
            const store = transaction.objectStore("products");

            // Clear and rewrite (simplest for now)
            const clearReq = store.clear();

            clearReq.onsuccess = () => {
                let completed = 0;
                if (this.data.products.length === 0) {
                    resolve();
                    return;
                }

                this.data.products.forEach(p => {
                    const addReq = store.add(p);
                    addReq.onsuccess = () => {
                        completed++;
                        if (completed === this.data.products.length) resolve();
                    };
                    addReq.onerror = (e) => reject(e.target.error);
                });
            };

            clearReq.onerror = (e) => reject(e.target.error);
        });
    },

    loadData: async function () {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(["products"], "readonly");
            const store = transaction.objectStore("products");
            const request = store.getAll();

            request.onsuccess = () => {
                this.data.products = request.result || [];
                this.renderList();
                resolve();
            };

            request.onerror = (e) => reject(e.target.error);
        });
    },

    clearData: async function () {
        if (confirm("¿BORRAR TODO? Esto no se puede deshacer.")) {
            this.data.products = [];
            await this.saveData();
            this.renderList();
        }
    },

    generatePDF: async function () {
        if (this.data.products.length === 0) {
            alert("No hay productos para generar.");
            return;
        }

        document.getElementById('loading').style.display = 'flex';

        // Defer to allow UI update
        setTimeout(async () => {
            try {
                await pdfGenerator.generate(this.data.products);
            } catch (e) {
                alert("Error generando PDF: " + e.message);
                console.error(e);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }, 100);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
