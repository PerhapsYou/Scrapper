// Force logout when admin.html is reloaded or reopened
sessionStorage.removeItem('slu_admin_auth');

class AdminPanel {
    constructor() {
        this.loginSection = document.getElementById('loginSection');
        this.adminContent = document.getElementById('adminContent');
        this.loginForm = document.getElementById('loginForm');
        this.menuList = document.getElementById('menuList');
        this.menuWindow = document.getElementById('menuWindow');
        this.confirmWindow = document.getElementById('confirmWindow');
        this.menuForm = document.getElementById('menuForm');
        this.statusMessage = document.getElementById('statusMessage');
        
        this.currentEditingId = null;
        this.menuData = {};
        
        this.initializeEventListeners();
        this.checkAuthentication();
    }
    
    initializeEventListeners() {
        // Login form
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        
        // Toolbar buttons
        document.getElementById('addMenuBtn').addEventListener('click', () => this.showAddMenuWindow());
        document.getElementById('saveAllBtn').addEventListener('click', () => this.saveAllChanges());
        document.getElementById('resetBtn').addEventListener('click', () => this.showResetConfirmation());
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        
        // Popup controls
        document.getElementById('closeWindow').addEventListener('click', () => this.closeMenuWindow());
        document.getElementById('cancelBtn').addEventListener('click', () => this.closeMenuWindow());
        this.menuForm.addEventListener('submit', (e) => this.handleMenuSave(e));
        
        // Confirmation popup
        document.getElementById('confirmCancel').addEventListener('click', () => this.closeConfirmWindow());
        document.getElementById('confirmOk').addEventListener('click', () => this.executeConfirmedAction());
        
        // Close windows on backdrop click
        this.menuWindow.addEventListener('click', (e) => {
            if (e.target === this.menuWindow) this.closeMenuWindow();
        });
        
        this.confirmWindow.addEventListener('click', (e) => {
            if (e.target === this.confirmWindow) this.closeConfirmWindow();
        });
        
        // Escape key to close windows
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeMenuWindow();
                this.closeConfirmWindow();
            }
        });
    }
    
    checkAuthentication() {
        const isAuthenticated = sessionStorage.getItem('slu_admin_auth') === 'true';
        if (isAuthenticated) {
            this.showAdminPanel();
        }
    }
    
    async handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const res = await fetch("http://localhost:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();

            if (res.ok && data.status === "success") {
                sessionStorage.setItem('slu_admin_auth', 'true');
                this.showAdminPanel();
                this.showStatus('Login successful!', 'success');
            } else {
                this.showStatus(data.detail || 'Login failed.', 'error');
            }
        } catch (err) {
            this.showStatus('Server error during login.', 'error');
            console.error("Login error:", err);
        }
    }

    
    showAdminPanel() {
        this.loginSection.style.display = 'none';
        this.adminContent.style.display = 'block';
        this.loadMenuData();
        this.renderMenuList();
    }
    
    logout() {
        sessionStorage.removeItem('slu_admin_auth');
        this.adminContent.style.display = 'none';
        this.loginSection.style.display = 'flex';
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        this.showStatus('Logged out successfully.', 'info');
    }
    
    async loadMenuData() {
        try {
            const res = await fetch("http://localhost:8000/admin/menu");
            const data = await res.json();
            this.menuData = {};
            for (const item of data.menu) {
                this.menuData[item.id] = item;
            }
        } catch (error) {
            console.error("Failed to fetch menu items:", error);
            this.menuData = {};
        }
    }
    
    renderMenuList() {
        this.menuList.innerHTML = '';
        
        Object.entries(this.menuData).forEach(([id, item]) => {
            const menuItem = document.createElement('div');
            menuItem.className = 'menu-item';
            menuItem.innerHTML = `
                <div class="menu-item-header">
                    <div class="menu-item-title">
                        <span class="emoji">${item.emoji}</span>
                        <h3>${this.escapeHtml(item.title)}</h3>
                    </div>
                    <div class="menu-item-actions">
                        <button class="action-btn edit" onclick="adminPanel.editMenuItem('${id}')">
                            ✏️ Edit
                        </button>
                        <button class="action-btn delete" onclick="adminPanel.deleteMenuItem('${id}')">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                <div class="menu-item-content">
                    ${this.formatContentPreview(item.content)}
                </div>
            `;
            this.menuList.appendChild(menuItem);
        });
    }
    
    formatContentPreview(content) {
        const textOnly = content.replace(/<[^>]*>/g, '');
        return textOnly.length > 200 ? textOnly.substring(0, 200) + '...' : textOnly;
    }
    
    showAddMenuWindow() {
        this.currentEditingId = null;
        document.getElementById('windowTitle').textContent = 'Add New Menu Item';
        document.getElementById('menuTitle').value = '';
        document.getElementById('menuEmoji').value = '';
        document.getElementById('menuContent').value = '';
        this.menuWindow.classList.add('active');
    }
    
    editMenuItem(id) {
        this.currentEditingId = id;
        const item = this.menuData[id];
        
        document.getElementById('windowTitle').textContent = 'Edit Menu Item';
        document.getElementById('menuTitle').value = item.title;
        document.getElementById('menuEmoji').value = item.emoji;
        document.getElementById('menuContent').value = item.content;
        this.menuWindow.classList.add('active');
    }
    
    deleteMenuItem(id) {
        this.pendingDeleteId = id;
        const item = this.menuData[id];
        document.getElementById('confirmMessage').textContent = 
            `Are you sure you want to delete "${item.title}"? This action cannot be undone.`;
        this.confirmWindow.classList.add('active');
        this.pendingAction = 'delete';
    }
    
    handleMenuSave(e) {
        e.preventDefault();
        
        const title = document.getElementById('menuTitle').value.trim();
        const emoji = document.getElementById('menuEmoji').value.trim();
        const content = document.getElementById('menuContent').value.trim();
        
        if (!title || !emoji || !content) {
            this.showStatus('Please fill in all fields.', 'error');
            return;
        }
        
        const menuItem = { title, emoji, content };
        
        if (this.currentEditingId) {
            // Edit existing item
            this.menuData[this.currentEditingId] = menuItem;
            this.showStatus('Menu item updated successfully!', 'success');
        } else {
            // Add new item
            const newId = this.generateNewId();
            this.menuData[newId] = menuItem;
            this.showStatus('Menu item added successfully!', 'success');
        }
        
        this.renderMenuList();
        this.closeMenuWindow();
        this.markAsUnsaved();
    }
    
    generateNewId() {
        const existingIds = Object.keys(this.menuData).map(id => parseInt(id));
        return (Math.max(...existingIds, 0) + 1).toString();
    }
    
    closeMenuWindow() {
        this.menuWindow.classList.remove('active');
        this.currentEditingId = null;
    }
    
    closeConfirmWindow() {
        this.confirmWindow.classList.remove('active');
        this.pendingDeleteId = null;
        this.pendingAction = null;
    }
    
    executeConfirmedAction() {
        if (this.pendingAction === 'delete' && this.pendingDeleteId) {
            delete this.menuData[this.pendingDeleteId];
            this.renderMenuList();
            this.showStatus('Menu item deleted successfully!', 'success');
            this.markAsUnsaved();
        } else if (this.pendingAction === 'reset') {
            this.menuData = this.getDefaultMenuData();
            this.renderMenuList();
            this.showStatus('Menu data has been reset to default.', 'info');
            this.markAsUnsaved();
        }
        
        this.closeConfirmWindow();
    }
    
    saveAllChanges() {
        try {
            localStorage.setItem('slu_chatbot_menu', JSON.stringify(this.menuData));
            this.showStatus('All changes saved successfully!', 'success');
            this.markAsSaved();
        } catch (error) {
            this.showStatus('Error saving changes. Please try again.', 'error');
            console.error('Save error:', error);
        }
    }
    
    showResetConfirmation() {
        document.getElementById('confirmMessage').textContent = 
            'Are you sure you want to reset all menu data to default? This will overwrite all current items and cannot be undone.';
        this.confirmWindow.classList.add('active');
        this.pendingAction = 'reset';
    }
    
    markAsUnsaved() {
        const saveBtn = document.getElementById('saveAllBtn');
        saveBtn.textContent = '💾 Save Changes*';
        saveBtn.classList.add('unsaved');
    }
    
    markAsSaved() {
        const saveBtn = document.getElementById('saveAllBtn');
        saveBtn.textContent = '💾 Save Changes';
        saveBtn.classList.remove('unsaved');
    }
    
    showStatus(message, type = 'info') {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message ${type} show`;
        this.statusMessage.style.display = 'block';
        
        if (this.statusTimeout) {
            clearTimeout(this.statusTimeout);
        }

        this.statusTimeout = setTimeout(() => {
            this.statusMessage.classList.remove('show');
            setTimeout(() => {
                this.statusMessage.style.display = 'none';
            }, 300);
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});