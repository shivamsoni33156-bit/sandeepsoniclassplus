// Updated JS with more features (previous + new)

const API_BASE = '/api';

let token = localStorage.getItem('token') || null;

function setToken(newToken) {
    token = newToken;
    if (newToken) {
        localStorage.setItem('token', newToken);
    } else {
        localStorage.removeItem('token');
    }
}

async function apiCall(endpoint, options = {}) {
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        ...options
    };
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
        setToken(null);
        showLogin();
        return;
    }
    return response.json();
}

// Auth
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        username: document.getElementById('loginUser').value,
        password: document.getElementById('loginPass').value
    };
    const res = await apiCall('/login', { method: 'POST', body: JSON.stringify(data) });
    if (res.access_token) {
        setToken(res.access_token);
        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
        loadDashboard();
    } else {
        alert(res.error);
    }
});

// ... (register same)

async function loadDashboard() {
    const res = await apiCall('/dashboard');
    showDashboard(res);
}

function showDashboard(data) {
    let html = `
        <nav class="navbar navbar-light">
            <div class="container-fluid">
                <button class="navbar-toggler" onclick="toggleSidebar()">
                    <span class="navbar-toggler-icon"></span>
                </button>
            </div>
        </nav>
        <div class="row">
            <div class="col-md-3 sidebar" id="sidebar">
                <ul class="nav flex-column p-3">
                    <li class="nav-item"><a class="nav-link" onclick="loadCourses()">My Courses</a></li>
                    <li class="nav-item"><a class="nav-link" onclick="loadMaterials()">Study Materials</a></li>
                    <li class="nav-item"><a class="nav-link" onclick="showPayments()">Payments</a></li>
                    <li class="nav-item"><a class="nav-link" onclick="loadTests()">Tests</a></li>
                    <li class="nav-item"><a class="nav-link" onclick="logout()">Logout</a></li>
                </ul>
            </div>
            <div class="col-md-9 ms-sm-auto px-md-4" id="main-content">
                <h2>Dashboard</h2>
    `;
    // Stats
    html += getStatsHtml(data);
    html += `</div></div>`;
    document.querySelector('.container').innerHTML = html;
}

function getStatsHtml(data) {
    let stats = '';
    if (data.earnings !== undefined) {
        stats = `
            <div class="row g-4">
                <div class="col-md-4"><div class="card p-4 text-center"><div class="stat-number">${data.students}</div>Total Students</div></div>
                <div class="col-md-4"><div class="card p-4 text-center"><div class="stat-number">${data.courses}</div>Total Courses</div></div>
                <div class="col-md-4"><div class="card p-4 text-center"><div class="stat-number">₹${data.earnings}</div>Earnings</div></div>
            </div>
        `;
    }
    return stats;
}

async function loadCourses() {
    const courses = await apiCall('/courses');
    let html = '<h3>Courses</h3>';
    html += '<div class="row">';
    courses.forEach(c => {
        html += `
            <div class="col-md-4 mb-3">
                <div class="card course-card">
                    <div class="card-body">
                        <h5>${c.name}</h5>
                        <p>₹${c.price}</p>
                        <button class="btn btn-sm btn-primary" onclick="enroll(${c.id})">Enroll</button>
                        <button class="btn btn-sm btn-success" onclick="loadCourseMaterials(${c.id})">Materials</button>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    document.getElementById('main-content').innerHTML = html;
}

function enroll(courseId) {
    apiCall(`/enroll/${courseId}`, {method: 'POST'}).then(res => alert(res.msg));
}

async function loadCourseMaterials(courseId) {
    const materials = await apiCall(`/materials/${courseId}`);
    let html = `<h3>Materials for Course ${courseId}</h3><div class="row">`;
    materials.forEach(m => {
        html += `
            <div class="col-md-6 mb-3 material-item">
                <h6>${m.subject} - ${m.chapter}</h6>
                <a href="/uploads/${m.file_path}" class="btn btn-outline-primary" download>Download ${m.type.toUpperCase()}</a>
            </div>
        `;
    });
    html += '</div>';
    document.getElementById('main-content').innerHTML = html;
}

function showPayments() {
    const html = `
        <h3>Payments</h3>
        <div class="payment-section">
            <h5>Pay Course Fee</h5>
            <p><strong>UPI:</strong> 7229985050 (PhonePe / GPay)</p>
            <a href="upi://pay?pa=7229985050@paytm&pn=Zakir%20Husain&am=500&cu=INR" class="btn btn-success">Pay ₹500 PhonePe</a>
            <a href="upi://pay?pa=7229985050@ybl&pn=Zakir%20Husain&am=500&cu=INR" class="btn btn-success">Pay ₹500 GPay</a>
            <br><br>
            <p><strong>Bank:</strong> Zakir Husain, SBI A/C 30392342115</p>
            <p>Upload payment receipt to admin for verification.</p>
        </div>
    `;
    document.getElementById('main-content').innerHTML = html;
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function logout() {
    setToken(null);
    location.reload();
}

// Init
if (token) loadDashboard();
