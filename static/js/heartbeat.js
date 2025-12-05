import { API_URL } from './modules/common.js';

/**
 * Sends a heartbeat to the server indicating the user's login status
 * This function should be called periodically to keep the server updated
 */
export function sendHeartbeat() {
    try {
        const isUserLoggedIn = document.querySelector('a[href="/session/edit_cash"]') !== null;

        fetch(`${API_URL}/heartbeat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ logged_in: isUserLoggedIn })
        }).catch(() => { }); // Ignore errors
    } catch (e) {
        console.error('Error sending heartbeat:', e);
    }
}

/**
 * Initialize heartbeat system
 * Sends an initial heartbeat and sets up periodic updates
 */
export function initHeartbeat(intervalMs = 30000) {
    // Send initial heartbeat
    sendHeartbeat();

    // Set up periodic heartbeat
    setInterval(sendHeartbeat, intervalMs);
}
