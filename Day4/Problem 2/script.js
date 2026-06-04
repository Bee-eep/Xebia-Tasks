// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme_preference');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    } else if (prefersDark) {
        document.body.classList.add('dark-mode');
    }
}

function toggleTheme() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme_preference', isDarkMode ? 'dark' : 'light');
}

// User Database (simulated with localStorage)
class UserDatabase {
    constructor() {
        this.storageKey = 'users_db';
        this.currentUserKey = 'current_user';
    }

    getAllUsers() {
        const data = localStorage.getItem(this.storageKey);
        return data ? JSON.parse(data) : [];
    }

    saveUser(user) {
        const users = this.getAllUsers();
        users.push(user);
        localStorage.setItem(this.storageKey, JSON.stringify(users));
    }

    getUserByEmail(email) {
        const users = this.getAllUsers();
        return users.find(user => user.email === email);
    }

    updateUser(email, updatedData) {
        const users = this.getAllUsers();
        const index = users.findIndex(user => user.email === email);
        if (index !== -1) {
            users[index] = { ...users[index], ...updatedData };
            localStorage.setItem(this.storageKey, JSON.stringify(users));
            return true;
        }
        return false;
    }

    setCurrentUser(user) {
        localStorage.setItem(this.currentUserKey, JSON.stringify(user));
    }

    getCurrentUser() {
        const data = localStorage.getItem(this.currentUserKey);
        return data ? JSON.parse(data) : null;
    }

    deleteUser(email) {
        const users = this.getAllUsers();
        const filtered = users.filter(user => user.email !== email);
        localStorage.setItem(this.storageKey, JSON.stringify(filtered));
    }

    logout() {
        localStorage.removeItem(this.currentUserKey);
    }
}

const db = new UserDatabase();

// Validation Functions
const Validator = {
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    isValidPassword(password) {
        return password.length >= 6;
    },

    isValidPhone(phone) {
        if (!phone) return true; // Optional field
        const phoneRegex = /^[0-9\-\+\s]{10,}$/;
        return phoneRegex.test(phone);
    },

    isValidName(name) {
        return name.trim().length >= 3;
    }
};

// Page Navigation
function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const page = document.getElementById(pageName);
    if (page) {
        page.classList.add('active');
    }

    // Update navbar active link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Update nav links based on authentication status
    const currentUser = db.getCurrentUser();
    const navLinks = document.getElementById('navLinks');
    
    if (pageName === 'dashboard' && currentUser) {
        // Authenticated view
        navLinks.innerHTML = `
            <a href="#" onclick="showPage('dashboard')" class="nav-link active">Dashboard</a>
            <a href="#" onclick="logout()" class="nav-link">Logout</a>
        `;
    } else if (currentUser && pageName !== 'editProfile') {
        // User is logged in but viewing other pages
        navLinks.innerHTML = `
            <a href="#" onclick="showPage('dashboard')" class="nav-link">Dashboard</a>
            <a href="#" onclick="logout()" class="nav-link">Logout</a>
        `;
    } else {
        // Not authenticated or on edit profile
        navLinks.innerHTML = `
            <a href="#" onclick="showPage('home')" class="nav-link ${pageName === 'home' ? 'active' : ''}">Home</a>
            <a href="#" onclick="showPage('login')" class="nav-link ${pageName === 'login' ? 'active' : ''}">Login</a>
            <a href="#" onclick="showPage('register')" class="nav-link ${pageName === 'register' ? 'active' : ''}">Register</a>
        `;
    }
}

// Registration Function
function registerUser(event) {
    event.preventDefault();

    // Get form values
    const fullName = document.getElementById('regFullName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    const phone = document.getElementById('regPhone').value;

    // Clear previous errors
    clearErrors(['regFullName', 'regEmail', 'regPassword', 'regConfirmPassword', 'regPhone']);

    let hasErrors = false;

    // Validate Full Name
    if (!Validator.isValidName(fullName)) {
        showError('regFullName', 'Full name must be at least 3 characters');
        hasErrors = true;
    }

    // Validate Email
    if (!Validator.isValidEmail(email)) {
        showError('regEmail', 'Please enter a valid email address');
        hasErrors = true;
    }

    // Check if email already exists
    if (db.getUserByEmail(email)) {
        showError('regEmail', 'Email already registered');
        hasErrors = true;
    }

    // Validate Password
    if (!Validator.isValidPassword(password)) {
        showError('regPassword', 'Password must be at least 6 characters');
        hasErrors = true;
    }

    // Validate Password Confirmation
    if (password !== confirmPassword) {
        showError('regConfirmPassword', 'Passwords do not match');
        hasErrors = true;
    }

    // Validate Phone
    if (!Validator.isValidPhone(phone)) {
        showError('regPhone', 'Please enter a valid phone number');
        hasErrors = true;
    }

    if (hasErrors) {
        return;
    }

    // Create new user
    const newUser = {
        fullName,
        email,
        password,
        phone,
        joinDate: new Date().toLocaleDateString(),
        bio: '',
        loginCount: 0
    };

    // Save user to database
    db.saveUser(newUser);

    // Show success message
    showSuccess('regSuccess', 'Registration successful! You can now login.');

    // Reset form
    document.getElementById('registerForm').reset();

    // Redirect to login after 2 seconds
    setTimeout(() => {
        showPage('login');
    }, 2000);
}

// Login Function
function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;

    // Clear previous errors
    clearErrors(['loginEmail', 'loginPassword']);

    let hasErrors = false;

    // Validate Email
    if (!email) {
        showError('loginEmail', 'Email is required');
        hasErrors = true;
    }

    // Validate Password
    if (!password) {
        showError('loginPassword', 'Password is required');
        hasErrors = true;
    }

    if (hasErrors) {
        return;
    }

    // Find user
    const user = db.getUserByEmail(email);

    // Check credentials
    if (!user || user.password !== password) {
        showError('loginEmail', 'Invalid email or password');
        showError('loginPassword', 'Invalid email or password');
        return;
    }

    // Update login count
    user.loginCount = (user.loginCount || 0) + 1;
    user.lastLogin = new Date().toLocaleString();

    // Save to current user
    db.updateUser(email, user);
    db.setCurrentUser(user);

    // Show success message
    showSuccess('loginSuccess', 'Login successful! Redirecting to dashboard...');

    // Reset form
    document.getElementById('loginForm').reset();

    // Redirect to dashboard after 2 seconds
    setTimeout(() => {
        loadDashboard();
        showPage('dashboard');
    }, 1500);
}

// Load Dashboard
function loadDashboard() {
    const currentUser = db.getCurrentUser();

    if (!currentUser) {
        showPage('home');
        return;
    }

    // Extract first name from full name
    const firstName = currentUser.fullName.split(' ')[0];

    // Update dashboard elements
    document.getElementById('userName').textContent = firstName;
    document.getElementById('userEmail').textContent = currentUser.email;
    document.getElementById('dashName').textContent = currentUser.fullName;
    document.getElementById('dashEmail').textContent = currentUser.email;
    document.getElementById('dashPhone').textContent = currentUser.phone || 'Not provided';
    document.getElementById('dashJoinDate').textContent = currentUser.joinDate;
    document.getElementById('lastLogin').textContent = currentUser.lastLogin || 'Today';
    document.getElementById('loginCount').textContent = currentUser.loginCount || 1;
}

// Update Profile
function updateProfile(event) {
    event.preventDefault();

    const currentUser = db.getCurrentUser();
    if (!currentUser) {
        showPage('login');
        return;
    }

    const fullName = document.getElementById('editFullName').value;
    const phone = document.getElementById('editPhone').value;
    const bio = document.getElementById('editBio').value;

    // Validate
    if (!Validator.isValidName(fullName)) {
        showError('editFullName', 'Full name must be at least 3 characters');
        return;
    }

    if (phone && !Validator.isValidPhone(phone)) {
        showError('editPhone', 'Please enter a valid phone number');
        return;
    }

    // Update user
    const updatedUser = {
        ...currentUser,
        fullName,
        phone,
        bio
    };

    db.updateUser(currentUser.email, updatedUser);
    db.setCurrentUser(updatedUser);

    // Show success message
    showSuccess('editSuccess', 'Profile updated successfully!');

    // Reload dashboard
    setTimeout(() => {
        loadDashboard();
        showPage('dashboard');
    }, 1500);
}

// Logout Function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        db.logout();
        showPage('home');
    }
}

// Change Password
function changePassword() {
    const newPassword = prompt('Enter new password (min 6 characters):');

    if (newPassword === null) return;

    if (!Validator.isValidPassword(newPassword)) {
        alert('Password must be at least 6 characters');
        return;
    }

    const currentUser = db.getCurrentUser();
    if (!currentUser) return;

    const confirmPassword = prompt('Confirm new password:');

    if (newPassword !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    // Update password
    currentUser.password = newPassword;
    db.updateUser(currentUser.email, currentUser);
    db.setCurrentUser(currentUser);

    alert('Password changed successfully!');
}

// Delete Account
function deleteAccount() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        const currentUser = db.getCurrentUser();
        if (currentUser) {
            db.deleteUser(currentUser.email);
            db.logout();
            alert('Account deleted successfully');
            showPage('home');
        }
    }
}

// Download Data
function downloadData() {
    const currentUser = db.getCurrentUser();
    if (!currentUser) return;

    const dataStr = JSON.stringify(currentUser, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `user-data-${currentUser.email}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    alert('Your data has been downloaded!');
}

// Helper Functions
function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}Error`);
    if (errorElement) {
        errorElement.textContent = message;
        const input = document.getElementById(fieldId);
        if (input) {
            input.classList.add('input-error');
        }
    }
}

function clearErrors(fieldIds) {
    fieldIds.forEach(fieldId => {
        const errorElement = document.getElementById(`${fieldId}Error`);
        if (errorElement) {
            errorElement.textContent = '';
        }
        const input = document.getElementById(fieldId);
        if (input) {
            input.classList.remove('input-error');
        }
    });
}

function showSuccess(elementId, message) {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.textContent = message;
        successElement.classList.add('show');

        setTimeout(() => {
            successElement.classList.remove('show');
        }, 3000);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme first
    initializeTheme();

    // Check if user is already logged in
    const currentUser = db.getCurrentUser();
    
    if (currentUser) {
        loadDashboard();
        showPage('dashboard');
    } else {
        showPage('home');
    }

    // Load edit profile data if available
    document.addEventListener('click', () => {
        if (document.getElementById('editProfile').classList.contains('active')) {
            const currentUser = db.getCurrentUser();
            if (currentUser) {
                document.getElementById('editFullName').value = currentUser.fullName;
                document.getElementById('editPhone').value = currentUser.phone || '';
                document.getElementById('editBio').value = currentUser.bio || '';
            }
        }
    });
});

// Populate edit profile when navigating to that page
const originalShowPage = showPage;
showPage = function(pageName) {
    originalShowPage(pageName);
    
    if (pageName === 'editProfile') {
        const currentUser = db.getCurrentUser();
        if (currentUser) {
            document.getElementById('editFullName').value = currentUser.fullName;
            document.getElementById('editPhone').value = currentUser.phone || '';
            document.getElementById('editBio').value = currentUser.bio || '';
        }
    }
};
