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
const packs = document.querySelectorAll('.diamond-pack');
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

function openDialog(button) {
    const pack = button.parentElement;
    const productId = pack.getAttribute('data-id');
    const productName = pack.getAttribute('data-name');
    const productPrice = pack.getAttribute('data-price');

    document.getElementById('selectedProductName').innerText = productName;
    document.getElementById('selectedProductPrice').innerText = "Price: ₹" + productPrice;
    document.getElementById('productId').value = productId;

    // Set form action dynamically
    document.getElementById('idForm').action = `/add-to-cart/${productId}/`;

    document.getElementById('idDialog').style.display = 'block';
}

function closeDialog() {
    document.getElementById('idDialog').style.display = 'none';
}

// Optional: Close modal when clicking outside the modal
window.onclick = function(event) {
    const modal = document.getElementById('idDialog');
    if (event.target == modal) {
        closeDialog();
    }
};
function viewCart() {
    window.location.href = "/cart/";  // Redirect to the cart page
}

