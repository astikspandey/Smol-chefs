// Navigation handling
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.dataset.page;

        document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
        document.querySelectorAll('.page-section').forEach(section => section.classList.remove('active'));

        e.target.classList.add('active');
        document.getElementById(page).classList.add('active');
        history.pushState(null, null, `#${page}`);
    });
});

// Initial page load
window.addEventListener('load', () => {
    const hash = window.location.hash.substring(1);
    const validPages = ['our-story', 'menu', 'active-days'];
    const defaultPage = validPages.includes(hash) ? hash : 'our-story';

    document.querySelector(`[data-page="${defaultPage}"]`)?.classList.add('active');
    document.getElementById(defaultPage)?.classList.add('active');
});

// Cart functionality
let cart = [];

function addToCart(itemName, price) {
    const existingItem = cart.find(item => item.name === itemName);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({ name: itemName, price: price, quantity: 1 });
    }
    updateCartDisplay();
}

function adjustQuantity(index, change) {
    cart[index].quantity += change;
    if (cart[index].quantity < 1) {
        cart.splice(index, 1);
    }
    updateCartDisplay();
}

function removeItem(index) {
    cart.splice(index, 1);
    updateCartDisplay();
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cartItems');
    const cartCount = document.getElementById('cartCount');
    const cartTotal = document.getElementById('cartTotal');

    if (cartItems && cartCount && cartTotal) {
        cartItems.innerHTML = '';
        let total = 0;

        cart.forEach((item, index) => {
            total += item.price * item.quantity;
            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item';
            itemDiv.innerHTML = `
                <div style="flex-grow: 1;">
                    <div>${item.name}</div>
                    <div class="quantity-controls" data-index="${index}">
                        <button class="quantity-btn" data-action="decrease">-</button>
                        <span>${item.quantity}</span>
                        <button class="quantity-btn" data-action="increase">+</button>
                        <button class="remove-btn" data-action="remove">Remove</button>
                    </div>
                </div>
                <div>₹${(item.price * item.quantity).toFixed(2)}</div>
            `;
            cartItems.appendChild(itemDiv);
        });

        cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartTotal.textContent = total.toFixed(2);
    }
}

function toggleCart() {
    const cartModal = document.getElementById('cartModal');
    if (cartModal) {
        cartModal.classList.toggle('active');
    }
}

async function sendOrder() {
    if (cart.length === 0) {
        alert('Your cart is empty!');
        return;
    }

    // Get customer details (you can add a form for this)
    const customerName = prompt('Enter your name:');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    const orderData = {
        customer_name: customerName,
        items: cart.map(item => ({
            name: item.name,
            price: item.price,
            quantity: item.quantity
        })),
        total_amount: total
    };

    try {
        // Show loading state
        const orderBtn = document.querySelector('.order-btn');
        const originalText = orderBtn.textContent;
        orderBtn.textContent = 'Placing Order...';
        orderBtn.disabled = true;

        // Send order to Flask backend
        const response = await fetch('/place_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (response.ok) {
            // Success!
            alert(`Order placed successfully! Order ID: #${result.order_id}\n\nYour order has been sent to Little Chefs automatically!`);
            
            // Clear cart and close modal
            cart = [];
            updateCartDisplay();
            toggleCart();
        } else {
            alert('Failed to place order. Please try again.');
        }

        // Restore button
        orderBtn.textContent = originalText;
        orderBtn.disabled = false;

    } catch (error) {
        console.error('Error placing order:', error);
        alert('Error placing order. Please check your connection and try again.');
        
        // Restore button
        const orderBtn = document.querySelector('.order-btn');
        orderBtn.textContent = 'Place Order';
        orderBtn.disabled = false;
    }
}

// Event delegation for cart actions
document.addEventListener('click', function (e) {
    // Add to Cart buttons
    if (e.target.classList.contains('add-to-cart')) {
        const card = e.target.closest('.menu-card');
        const itemName = card.querySelector('h3').textContent;
        const price = parseFloat(card.querySelector('.price').textContent.replace(/[^\d.]/g, ''));
        addToCart(itemName, price);
    }

    // Cart icon
    if (e.target.closest('.cart-icon')) {
        toggleCart();
    }

    // Cart modal actions
    if (e.target.closest('.quantity-controls')) {
        const controls = e.target.closest('.quantity-controls');
        const index = parseInt(controls.dataset.index, 10);
        if (e.target.dataset.action === 'decrease') {
            adjustQuantity(index, -1);
        } else if (e.target.dataset.action === 'increase') {
            adjustQuantity(index, 1);
        } else if (e.target.dataset.action === 'remove') {
            removeItem(index);
        }
    }

    // Place Order button
    if (e.target.classList.contains('order-btn')) {
        sendOrder();
    }
});

// Optional: Add order history viewer
async function viewOrders() {
    try {
        const response = await fetch('/orders');
        const orders = await response.json();
        console.log('All orders:', orders);
    } catch (error) {
        console.error('Error fetching orders:', error);
    }
}