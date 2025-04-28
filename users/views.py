from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Product, Cart, Order
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
import uuid
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return redirect('products')  # 'products' should be the name of your URL pattern
    return render(request, 'home.html')

@login_required
def payment(request):
    return render(request, 'payment.html')

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def products(request):
    products = Product.objects.all()  # Fetch all products from the database

    # Count the items in the cart for the logged-in user
    cart_item_count = Cart.objects.filter(user=request.user).count()

    # Pass the products and cart item count to the template
    return render(request, 'products.html', {'products': products, 'cart_item_count': cart_item_count})

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        server_id = request.POST.get('server_id')
        product = Product.objects.get(id=product_id)

        Cart.objects.create(
            user=request.user,
            product=product,
            player_id=player_id,
            server_id=server_id,
            quantity=1
        )
        return redirect('cart_page')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = 0

    # Assuming all items in the cart have the same player_id and server_id
    player_id = None
    server_id = None

    for item in cart_items:
        item.total_price = item.product.price * item.quantity
        total_price += item.total_price

        # Get player_id and server_id from the first item in the cart
        if not player_id and not server_id:
            player_id = item.player_id
            server_id = item.server_id

    # If user clicks "Proceed to Checkout", create an order
    if request.method == 'POST':
        order_id = str(uuid.uuid4())  # Generate a unique order ID

        # Create the Order with player_id and server_id from the cart
        order = Order.objects.create(
            username=request.user,
            price=total_price,
            order_id=order_id,
            player_id=player_id,  # Use the player_id from cart
            server_id=server_id   # Use the server_id from cart
        )

        return redirect('checkout', order_id=order.order_id)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})




@login_required
def remove_from_cart(request, item_id):
    cart_item = Cart.objects.get(id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_page')

@login_required
def checkout(request, item_id):
    try:
        # Get the cart item for the logged-in user
        cart_item = Cart.objects.get(id=item_id, user=request.user)
        
        # Create an order for this specific item
        order_id = str(uuid.uuid4())  # Generate a unique order ID
        
        # Create the Order for this cart item
        order = Order.objects.create(
            username=request.user,
            price=cart_item.product.price * cart_item.quantity,
            order_id=order_id,
            player_id=cart_item.player_id,
            server_id=cart_item.server_id,
            product_name=cart_item.product.name,
        )

        return render(request, 'checkout.html', {
            'order': order,
            'total_price': order.price,
            'player_id': cart_item.player_id,
            'server_id': cart_item.server_id,
        })
    except Cart.DoesNotExist:
        return redirect('cart_page')  # Or handle error page if the cart item doesn't exist



@login_required
def create_order(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        order_id = str(uuid.uuid4())  # Unique Order ID
        
        # Create a new order
        order = Order.objects.create(
            username=request.user,
            product_name=product_name,
            price=price,
            order_id=order_id
        )
        # Redirect to checkout page
        return redirect('checkout', order_id=order.order_id)

@login_required
def orders(request):
    # Fetch all orders for the logged-in user
    user_orders = Order.objects.filter(username=request.user)

    return render(request, 'orders.html', {'user_orders': user_orders})


@login_required
def account_settings(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')

        # Validate email format
        try:
            EmailValidator()(new_email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('account_settings')

        # Check if username or email already exists
        if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('account_settings')

        if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email is already associated with another account.')
            return redirect('account_settings')

        # Update user details
        request.user.username = new_username
        request.user.email = new_email
        request.user.save()
        messages.success(request, 'Your account has been updated successfully.')
        return redirect('account_settings')  # Or redirect to another page if needed

    return render(request, 'account_settings.html')