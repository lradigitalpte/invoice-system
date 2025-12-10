// Main JavaScript for Invoicing System

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    function toggleSidebar() {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('active');
    }
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleSidebar);
    }
    
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
        });
    }
    
    // Close sidebar when clicking a link on mobile
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 968) {
                sidebar.classList.remove('open');
                sidebarOverlay.classList.remove('active');
            }
        });
    });
    
    // Add event listeners for dynamic form fields
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', addInvoiceItem);
    }
});

function addInvoiceItem() {
    const container = document.getElementById('invoice-items');
    const itemCount = container.children.length;
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'invoice-item card';
    itemDiv.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label>Description</label>
                <input type="text" name="items[${itemCount}][description]" required>
            </div>
            <div class="form-group">
                <label>Quantity</label>
                <input type="number" name="items[${itemCount}][quantity]" step="0.01" value="1" required>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Unit Price ($)</label>
                <input type="number" name="items[${itemCount}][unit_price]" step="0.01" required>
            </div>
            <div class="form-group">
                <label>Tax Rate (%)</label>
                <input type="number" name="items[${itemCount}][tax_rate]" step="0.01" value="0">
            </div>
        </div>
        <button type="button" class="btn btn-danger" onclick="this.parentElement.remove()">Remove Item</button>
    `;
    
    container.appendChild(itemDiv);
}

function confirmDelete(message = 'Are you sure?') {
    return confirm(message);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}
