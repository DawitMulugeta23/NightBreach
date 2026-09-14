import './src/style.css';

// API Configuration
const API_BASE = `http://${window.location.hostname}:8000`;

// Auth state
let currentToken = localStorage.getItem('roha_token');

// --- Page Navigation ---
function showPage(pageId) {
    const pages = ['landing-screen', 'learning-paths-screen', 'challenges-screen', 'leaderboard-screen', 'auth-screen'];
    pages.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === 'auth-screen') {
                el.style.display = 'none';
            } else {
                el.style.display = 'none';
            }
        }
    });
    
    const target = document.getElementById(pageId);
    if (target) {
        target.style.display = 'block';
        if (pageId === 'auth-screen') {
            target.style.display = 'flex';
        }
        window.scrollTo(0, 0);
    }
}

function revealAuthScreen() {
    showPage('auth-screen');
    const registerView = document.getElementById('register-view');
    const loginView = document.getElementById('login-view');
    if (registerView) registerView.style.display = 'none';
    if (loginView) loginView.style.display = 'block';
}

function backToLanding() {
    showPage('landing-screen');
}

// --- Navigation Event Listeners ---

// Home from all pages
document.getElementById('brand-home')?.addEventListener('click', () => showPage('landing-screen'));
document.getElementById('brand-home-from-paths')?.addEventListener('click', () => showPage('landing-screen'));
document.getElementById('brand-home-from-challenges')?.addEventListener('click', () => showPage('landing-screen'));
document.getElementById('brand-home-from-leaderboard')?.addEventListener('click', () => showPage('landing-screen'));

// Nav - Home
document.getElementById('nav-home')?.addEventListener('click', (e) => { e.preventDefault(); showPage('landing-screen'); });
document.getElementById('nav-home-from-paths')?.addEventListener('click', (e) => { e.preventDefault(); showPage('landing-screen'); });
document.getElementById('nav-home-from-challenges-link')?.addEventListener('click', (e) => { e.preventDefault(); showPage('landing-screen'); });
document.getElementById('nav-home-from-leaderboard-link')?.addEventListener('click', (e) => { e.preventDefault(); showPage('landing-screen'); });

// Nav - Learning Paths
document.getElementById('nav-paths')?.addEventListener('click', (e) => { e.preventDefault(); showPage('learning-paths-screen'); });
document.getElementById('nav-paths-from-paths')?.addEventListener('click', (e) => { e.preventDefault(); showPage('learning-paths-screen'); });
document.getElementById('nav-paths-from-challenges')?.addEventListener('click', (e) => { e.preventDefault(); showPage('learning-paths-screen'); });
document.getElementById('nav-paths-from-leaderboard')?.addEventListener('click', (e) => { e.preventDefault(); showPage('learning-paths-screen'); });

// Nav - Challenges
document.getElementById('nav-challenges')?.addEventListener('click', (e) => { e.preventDefault(); showPage('challenges-screen'); });
document.getElementById('nav-challenges-from-paths')?.addEventListener('click', (e) => { e.preventDefault(); showPage('challenges-screen'); });
document.getElementById('nav-challenges-from-challenges-link')?.addEventListener('click', (e) => { e.preventDefault(); showPage('challenges-screen'); });
document.getElementById('nav-challenges-from-leaderboard')?.addEventListener('click', (e) => { e.preventDefault(); showPage('challenges-screen'); });

// Nav - Leaderboard
document.getElementById('nav-leaderboard')?.addEventListener('click', (e) => { e.preventDefault(); showPage('leaderboard-screen'); });
document.getElementById('nav-leaderboard-from-paths')?.addEventListener('click', (e) => { e.preventDefault(); showPage('leaderboard-screen'); });
document.getElementById('nav-leaderboard-from-challenges')?.addEventListener('click', (e) => { e.preventDefault(); showPage('leaderboard-screen'); });
document.getElementById('nav-leaderboard-from-leaderboard-link')?.addEventListener('click', (e) => { e.preventDefault(); showPage('leaderboard-screen'); });

// Login buttons
document.getElementById('login-btn')?.addEventListener('click', revealAuthScreen);
document.getElementById('login-btn-paths')?.addEventListener('click', revealAuthScreen);
document.getElementById('login-btn-challenges')?.addEventListener('click', revealAuthScreen);
document.getElementById('login-btn-leaderboard')?.addEventListener('click', revealAuthScreen);

// Get started buttons
document.querySelectorAll('.get-started-trigger').forEach(btn => {
    btn.addEventListener('click', revealAuthScreen);
});

// Auth navigation
document.getElementById('show-register-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-view').style.display = 'none';
    document.getElementById('register-view').style.display = 'block';
});

document.getElementById('show-login-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('register-view').style.display = 'none';
    document.getElementById('login-view').style.display = 'block';
});

document.getElementById('back-to-map-login')?.addEventListener('click', (e) => {
    e.preventDefault();
    backToLanding();
});

document.getElementById('back-to-map-register')?.addEventListener('click', (e) => {
    e.preventDefault();
    backToLanding();
});

// --- Auth API Functions ---
async function authRequest(endpoint, data) {
    const res = await fetch(`${API_BASE}/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Authentication failed');
    }
    return res.json();
}

// --- Login/Register Handlers ---
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('auth-error');

    try {
        const data = await authRequest('login', { username, password });
        currentToken = data.access_token;
        localStorage.setItem('roha_token', currentToken);
        if (errorEl) errorEl.textContent = '';
        alert('Login successful!');
        showPage('landing-screen');
    } catch (err) {
        if (errorEl) errorEl.textContent = err.message;
        console.error(err);
    }
});

document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-confirm-password').value;
    const errorEl = document.getElementById('auth-error');

    if (password !== confirm) {
        if (errorEl) errorEl.textContent = 'Passwords do not match';
        return;
    }

    try {
        const data = await authRequest('register', { username, email, password });
        currentToken = data.access_token;
        localStorage.setItem('roha_token', currentToken);
        if (errorEl) errorEl.textContent = '';
        alert('Registration successful! Please login.');
        document.getElementById('register-view').style.display = 'none';
        document.getElementById('login-view').style.display = 'block';
    } catch (err) {
        if (errorEl) errorEl.textContent = err.message;
        console.error(err);
    }
});

// --- Data Fetching ---
async function fetchCurrentUser() {
    if (!currentToken) return;
    try {
        const res = await fetch(`${API_BASE}/auth/me?token=${encodeURIComponent(currentToken)}`);
        if (!res.ok) {
            if (res.status === 401) {
                localStorage.removeItem('roha_token');
                currentToken = null;
            }
            return;
        }
        const user = await res.json();
        console.log('User:', user);
        return user;
    } catch (err) {
        console.error('Error fetching user:', err);
    }
}

// --- Initialization ---
if (currentToken) {
    fetchCurrentUser();
}

console.log('✅ NightBreach Frontend loaded');
