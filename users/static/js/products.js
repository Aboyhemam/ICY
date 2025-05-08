function toggleDropdown() {
    document.querySelector(".dropdown-content").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('.person-icon')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}



// Handle Diamond Pack Selection
const packs = document.querySelectorAll('.topup-pack');
const packName = document.getElementById('pack-name');
const payableAmount = document.getElementById('payable-amount');

packs.forEach(pack => {
    pack.addEventListener('click', () => {
        const packPrice = pack.getAttribute('data-price');
        const packTitle = pack.querySelector('h3').textContent;
        
        packName.textContent = `Selected Pack: ${packTitle}`;
        payableAmount.textContent = `Amount: ₹${Number(packPrice).toLocaleString('en-IN')}`;

    });
});

// Function to open modal
function openDialog(button) {
    const modal = document.getElementById('idDialog');
    const product = button.closest('.topup-pack');  // ✅ Fixed here

    document.getElementById('idForm').action = `/add-to-cart/${product.dataset.id}/`;
    document.getElementById('selectedProductName').textContent = product.dataset.name;
    document.getElementById('selectedProductPrice').textContent = `₹${product.dataset.price}`;
    document.getElementById('productId').value = product.dataset.id;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}


function closeDialog() {
    const modal = document.getElementById('idDialog');
    modal.style.display = 'none';
    document.body.style.overflow = '';
}


// Close modal when clicking outside content
document.getElementById('idDialog').addEventListener('click', function(e) {
    if (e.target === this) {
        closeDialog();
    }
});
function viewCart() {
    window.location.href = "/cart/";  // Redirect to the cart page
}

