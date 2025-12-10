// Autocomplete functionality for search inputs
class Autocomplete {
    constructor(input, options) {
        this.input = input;
        this.options = options;
        this.currentFocus = -1;
        this.debounceTimer = null;
        this.minChars = options.minChars || 2;  // Minimum characters before searching
        this.debounceDelay = options.debounceDelay || 300;  // Wait 300ms after user stops typing
        this.init();
    }

    init() {
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        document.addEventListener('click', (e) => {
            if (e.target !== this.input) {
                this.closeList();
            }
        });
    }

    handleInput() {
        const value = this.input.value.trim();
        this.closeList();
        
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Check minimum character requirement
        if (!value || value.length < this.minChars) {
            return;
        }
        
        // Debounce: wait for user to stop typing
        this.debounceTimer = setTimeout(() => {
            this.performSearch(value);
        }, this.debounceDelay);
    }

    async performSearch(value) {
        // Show loading indicator
        this.showLoading();
        
        // Fetch data from API
        const items = await this.fetchData(value);
        
        // Hide loading indicator
        this.hideLoading();
        
        if (items.length === 0) {
            this.showNoResults();
            return;
        }

        // Create autocomplete container
        const listDiv = document.createElement('div');
        listDiv.setAttribute('id', this.input.id + '-autocomplete-list');
        listDiv.setAttribute('class', 'autocomplete-items');
        this.input.parentNode.appendChild(listDiv);

        // Limit displayed items to prevent huge dropdowns
        const maxDisplayItems = 15;
        const displayItems = items.slice(0, maxDisplayItems);
        
        // Create items
        displayItems.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.innerHTML = this.formatItem(item, value);
            itemDiv.addEventListener('click', () => {
                this.selectItem(item);
                this.closeList();
            });
            listDiv.appendChild(itemDiv);
        });
        
        // Show "more results" message if there are more items
        if (items.length > maxDisplayItems) {
            const moreDiv = document.createElement('div');
            moreDiv.className = 'autocomplete-more';
            moreDiv.textContent = `... and ${items.length - maxDisplayItems} more. Type more to narrow results.`;
            listDiv.appendChild(moreDiv);
        }
    }
    
    showLoading() {
        // Optional: show loading indicator
        // Can be implemented if needed
    }
    
    hideLoading() {
        // Optional: hide loading indicator
    }
    
    showNoResults() {
        // Optional: show "no results" message
    }

    async fetchData(query) {
        try {
            const response = await fetch(`${this.options.apiUrl}?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Autocomplete fetch error:', error);
            return [];
        }
    }

    formatItem(item, query) {
        const displayText = this.options.displayField(item);
        const regex = new RegExp(query, 'gi');
        const highlighted = displayText.replace(regex, match => `<strong>${match}</strong>`);
        
        if (this.options.subtitle) {
            const subtitle = this.options.subtitle(item);
            return `<div class="autocomplete-main">${highlighted}</div><div class="autocomplete-subtitle">${subtitle}</div>`;
        }
        
        return highlighted;
    }

    selectItem(item) {
        if (this.options.onSelect) {
            this.options.onSelect(item);
        }
    }

    handleKeydown(e) {
        let list = document.getElementById(this.input.id + '-autocomplete-list');
        if (!list) return;
        
        let items = list.getElementsByTagName('div');
        
        if (e.keyCode === 40) { // Down
            this.currentFocus++;
            this.addActive(items);
            e.preventDefault();
        } else if (e.keyCode === 38) { // Up
            this.currentFocus--;
            this.addActive(items);
            e.preventDefault();
        } else if (e.keyCode === 13) { // Enter
            e.preventDefault();
            if (this.currentFocus > -1 && items[this.currentFocus]) {
                items[this.currentFocus].click();
            }
        } else if (e.keyCode === 27) { // Escape
            this.closeList();
        }
    }

    addActive(items) {
        if (!items) return false;
        this.removeActive(items);
        
        if (this.currentFocus >= items.length) this.currentFocus = 0;
        if (this.currentFocus < 0) this.currentFocus = items.length - 1;
        
        items[this.currentFocus].classList.add('autocomplete-active');
    }

    removeActive(items) {
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove('autocomplete-active');
        }
    }

    closeList() {
        const lists = document.getElementsByClassName('autocomplete-items');
        for (let i = 0; i < lists.length; i++) {
            lists[i].parentNode.removeChild(lists[i]);
        }
        this.currentFocus = -1;
    }
}

// Initialize autocomplete for clients
function initClientAutocomplete(inputId, onSelectCallback) {
    const input = document.getElementById(inputId);
    if (!input) return;

    new Autocomplete(input, {
        apiUrl: '/clients/api/search',
        displayField: (item) => item.name,
        subtitle: (item) => `${item.email || ''} ${item.phone ? '• ' + item.phone : ''}`.trim(),
        onSelect: onSelectCallback
    });
}

// Initialize autocomplete for products
function initProductAutocomplete(inputElement, onSelectCallback) {
    if (!inputElement) return;

    new Autocomplete(inputElement, {
        apiUrl: '/products/api/search',
        minChars: 2,  // Require at least 2 characters
        debounceDelay: 300,  // Wait 300ms after user stops typing
        displayField: (item) => {
            // If it's a variant, show product name with variant label
            if (item.variant_data && Object.keys(item.variant_data).length > 0) {
                const variantLabel = Object.entries(item.variant_data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(' - ');
                return `${item.product_name || item.name} - ${variantLabel}`;
            }
            return item.name;
        },
        subtitle: (item) => {
            const price = item.price ? `$${item.price.toFixed(2)}` : '';
            const sku = item.sku ? `SKU: ${item.sku}` : '';
            return [price, sku].filter(Boolean).join(' • ');
        },
        onSelect: onSelectCallback
    });
}
