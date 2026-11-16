const API_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const forms = document.querySelectorAll('.form');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const messageDiv = document.getElementById('message');
    const apiStatus = document.getElementById('apiStatus');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`${targetTab}Form`).classList.add('active');
            messageDiv.textContent = '';
            messageDiv.className = 'message';
        });
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('regEmail').value;
        const username = document.getElementById('regUsername').value;
        const password = document.getElementById('regPassword').value;

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, username, password })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Registration successful! You can now login.', 'success');
                registerForm.reset();
            } else {
                showMessage(data.detail || 'Registration failed', 'error');
            }
        } catch (error) {
            showMessage('Network error. Is API running?', 'error');
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                showMessage(`Welcome, ${data.user.username}!`, 'success');
                loginForm.reset();
            } else {
                showMessage(data.detail || 'Login failed', 'error');
            }
        } catch (error) {
            showMessage('Network error. Is API running?', 'error');
        }
    });

    async function checkApiStatus() {
        try {
            const response = await fetch(`${API_URL}/health`);
            if (response.ok) {
                apiStatus.textContent = 'ONLINE';
                apiStatus.style.color = '#00ff88';
            } else {
                apiStatus.textContent = 'OFFLINE';
                apiStatus.style.color = '#ff4444';
            }
        } catch (error) {
            apiStatus.textContent = 'OFFLINE';
            apiStatus.style.color = '#ff4444';
        }
    }

    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type}`;
    }

    checkApiStatus();
    setInterval(checkApiStatus, 10000);
});