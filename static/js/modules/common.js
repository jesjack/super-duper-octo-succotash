export const API_URL = '/api';

export function addLongPressListener(element, callback) {
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

export function showProductDetailsOverlay(product) {
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
