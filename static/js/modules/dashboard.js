import { API_URL, addLongPressListener, showProductDetailsOverlay } from './common.js';

export async function loadStats() {
    try {
        // 1. Load Stats (Totals)
        const resStats = await fetch(`${API_URL}/stats`);
        if (resStats.status === 401) { window.location.href = '/login'; return; }
        const stats = await resStats.json();

        // Render Current Session Stats
        if (stats.current_session) {
            document.getElementById('initial-cash').textContent = `$${stats.current_session.initial_cash.toFixed(2)}`;
            document.getElementById('session-sales').textContent = `$${stats.current_session.sales_total.toFixed(2)}`;
            document.getElementById('box-total').textContent = `$${stats.current_session.box_total.toFixed(2)}`;
        } else {
            document.getElementById('initial-cash').textContent = "$0.00";
            document.getElementById('session-sales').textContent = "$0.00";
            document.getElementById('box-total').textContent = "$0.00";
        }

        // Render Historical Stats (if available)
        const histSection = document.getElementById('historical-section');
        if (stats.historical) {
            histSection.style.display = 'block';
            document.getElementById('total-revenue').textContent = `$${stats.historical.total_revenue.toFixed(2)}`;
        } else {
            histSection.style.display = 'none';
        }

        // 2. Load Sales List
        const resSales = await fetch(`${API_URL}/sales`);
        const data = await resSales.json();
        const sales = data.sales;
        const isAdmin = data.is_admin;

        const sessionList = document.getElementById('session-sales-list');
        const historicalList = document.getElementById('historical-sales-list');

        // --- Session List (Today's Sales) ---
        const now = new Date();
        // Robust YYYY-MM-DD generation for local time
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const todayStr = `${year}-${month}-${day}`;

        const getLocalDateStr = (ts) => {
            // Handle both "YYYY-MM-DD HH:MM:SS" and "YYYY-MM-DDTHH:MM:SS"
            return ts.split(/[ T]/)[0];
        };

        const todaySales = sales.filter(s => getLocalDateStr(s.timestamp) === todayStr);

        sessionList.innerHTML = "";
        if (todaySales.length > 0) {
            const totalToday = todaySales.length;
            todaySales.forEach((s, index) => {
                const dailyNum = totalToday - index;
                renderSaleItem(s, sessionList, dailyNum);
            });
        } else {
            sessionList.innerHTML = '<li class="empty-msg">No hay ventas hoy.</li>';
        }

        // --- Historical List (Admin Only) ---
        if (isAdmin) {
            historicalList.innerHTML = "";

            // 1. Group sales by date
            const salesByDate = {};
            sales.forEach(s => {
                const date = getLocalDateStr(s.timestamp);
                if (!salesByDate[date]) salesByDate[date] = [];
                salesByDate[date].push(s);
            });

            // 2. Generate all dates from first sale to today
            let allDates = Object.keys(salesByDate).sort().reverse(); // Newest first
            if (allDates.length > 0) {
                const firstDate = new Date(allDates[allDates.length - 1]);
                const lastDate = new Date(todayStr); // Up to today

                // Fill gaps
                const dateArray = [];
                let curr = new Date(lastDate);
                while (curr >= firstDate) {
                    dateArray.push(curr.toLocaleDateString('en-CA'));
                    curr.setDate(curr.getDate() - 1);
                }
                allDates = dateArray;
            } else {
                allDates = [todayStr];
            }

            // 3. Render
            allDates.forEach(dateStr => {
                // Header
                const dateObj = new Date(dateStr + "T00:00:00"); // Force local time
                const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                let label = dateObj.toLocaleDateString('es-ES', options);
                label = label.charAt(0).toUpperCase() + label.slice(1);

                const yesterday = new Date(now); yesterday.setDate(now.getDate() - 1);
                const yStr = yesterday.toLocaleDateString('en-CA');
                const antier = new Date(now); antier.setDate(now.getDate() - 2);
                const aStr = antier.toLocaleDateString('en-CA');

                if (dateStr === todayStr) label = "Hoy";
                else if (dateStr === yStr) label = "Ayer";
                else if (dateStr === aStr) label = "Antier";
                else {
                    const day = dateObj.getDate();
                    const month = dateObj.toLocaleDateString('es-ES', { month: 'long' });
                    const year = dateObj.getFullYear();
                    label = `${day} de ${month} del ${year}`;
                }

                const header = document.createElement('li');
                header.className = "date-header";
                header.style.padding = "10px";
                header.style.backgroundColor = "#e5e7eb";
                header.style.fontWeight = "bold";
                header.style.color = "#374151";
                header.style.marginTop = "15px";
                header.style.borderRadius = "4px";
                header.style.display = "flex";
                header.style.justifyContent = "space-between";
                header.innerHTML = `<span>${label}</span>`;
                historicalList.appendChild(header);

                const daySales = salesByDate[dateStr] || [];

                if (daySales.length > 0) {
                    const totalDay = daySales.length;
                    daySales.forEach((s, index) => {
                        const dailyNum = totalDay - index;
                        renderSaleItem(s, historicalList, dailyNum);
                    });
                } else {
                    const emptyMsg = document.createElement('li');
                    emptyMsg.style.padding = "10px";
                    emptyMsg.style.color = "#D9534F"; // Red
                    emptyMsg.style.fontStyle = "italic";
                    emptyMsg.textContent = "No se registraron ventas este día";
                    historicalList.appendChild(emptyMsg);
                }
            });
        }

    } catch (e) {
        console.error("Error loading stats:", e);
    }
}

function renderSaleItem(s, listElement, dailyNum) {
    const li = document.createElement('li');
    li.className = "item-container";

    // Header
    const header = document.createElement('div');
    header.className = "item";
    header.innerHTML = `
        <div class="item-info">
            <span class="item-name">Venta #${dailyNum !== undefined ? dailyNum : s.id}</span>
            <span class="item-meta">${s.timestamp} - ${s.payment_method}</span>
        </div>
        <div class="item-price">$${s.total.toFixed(2)}</div>
    `;
    li.appendChild(header);

    // Details
    const details = document.createElement('div');
    details.id = `sale-details-${s.id}`;
    details.className = "sale-details";
    details.style.display = "block"; // Always open
    details.style.background = "#f9f9f9";
    details.style.padding = "10px";
    details.style.borderBottom = "1px solid #eee";

    if (s.items) {
        s.items.forEach(i => {
            const row = document.createElement('div');
            row.className = "sale-item-row";
            row.style.display = "flex";
            row.style.alignItems = "center";
            row.style.marginBottom = "5px";

            const productObj = {
                name: i.name,
                barcode: i.barcode,
                price: i.price,
                image_path: i.image_path
            };

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
    }

    li.appendChild(details);
    listElement.appendChild(li);
}
