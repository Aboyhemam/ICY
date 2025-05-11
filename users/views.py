from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import logout
from .models import Product, Cart, Order, Game, UserAgreement, FAQ, Review
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
import uuid
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django import forms
# Create your views here.

def terms(request):
    return render(request, 'terms.html')


def contact(request):
    return render(request, 'contact.html')

def home(request):
    if request.user.is_authenticated:
        return redirect('products')  # Replace 'products' with your actual URL name for the products page

    try:
        site = Site.objects.get(id=1)
    except ObjectDoesNotExist:
        site = None

    return render(request, 'home.html', {'site': site})


@login_required
def products_by_game(request, game_id):
    form= ReviewForm()
    try:
        game = Game.objects.get(id=game_id)
        products = Product.objects.filter(game=game)  # Assuming Product has a ForeignKey to Game
    except Game.DoesNotExist:
        products = []

    return render(request, 'products_by_game.html', {
        'game': game,
        'products': products,
        'form': form
    })


@login_required
def payment(request):
    return render(request, 'payment.html')

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def products(request):
    search_query = request.GET.get('search', '')  
    form= ReviewForm()

    if search_query:
        games = Game.objects.filter(name__icontains=search_query)
    else:
        games = Game.objects.all()
    
    # ✅ Get cart item count for the current user
    cart_count = Cart.objects.filter(user=request.user).count()

    context = {
        'games': games,
        'search': search_query,
        'cart_count': cart_count,
        'form': form,# ✅ Pass to template
    }

    return render(request, 'products.html', context)

@login_required
def support(request):
    questions= FAQ.objects.all
    
    return render(request, 'support.html', {'questions': questions})


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        server_id = request.POST.get('server_id')
        product = Product.objects.get(id=product_id)

        Cart.objects.create(
    user=request.user,
    product=product,
    game=product.game,  # ✅ Assign the game
    player_id=player_id,
    server_id=server_id,
    quantity=1
)

        return redirect('cart_page')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = 0
    form = ReviewForm()

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
          player_id=player_id,
          server_id=server_id,
          product_name="Multiple Items",  # You can handle naming as needed
          game=cart_items.first().game if cart_items else None  # ✅ Assign game from one of the items
        )

        return redirect('checkout', order_id=order.order_id)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'form': form })




@login_required
def remove_from_cart(request, item_id):
    cart_item = Cart.objects.get(id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_page')

@login_required
def checkout(request, item_id):
    try:
        cart_item = Cart.objects.get(id=item_id, user=request.user)
        order_id = str(uuid.uuid4())

        # Create the Order for this cart item
        order = Order.objects.create(
            username=request.user,
            price=cart_item.product.price * cart_item.quantity,
            order_id=order_id,
            player_id=cart_item.player_id,
            server_id=cart_item.server_id,
            product_name=cart_item.product.name,
            game=cart_item.game
        )

        # Get or create the user's agreement record
        agreement, _ = UserAgreement.objects.get_or_create(user=request.user)

        return render(request, 'checkout.html', {
            'order': order,
            'total_price': order.price,
            'player_id': cart_item.player_id,
            'server_id': cart_item.server_id,
            'has_agreed': agreement.has_agreed_terms  # ✅ Used to pre-check checkbox
        })
    except Cart.DoesNotExist:
        return redirect('cart_page')



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
    form = ReviewForm()

    return render(request, 'orders.html', {'user_orders': user_orders, 'form':form})


@login_required
def account_settings(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        form = ReviewForm()

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

    return render(request, 'account_settings.html', {'form':form})

@login_required
def order_detail(request, order_id):
    form= ReviewForm()
    order = get_object_or_404(Order, id=order_id, username=request.user)
    return render(request, 'order_detail.html', {'order': order, 'form': form})

@login_required
def confirm_terms_and_payment(request):
    if request.method == 'POST' and request.POST.get('confirm_terms') == 'yes':
        agreement, _ = UserAgreement.objects.get_or_create(user=request.user)
        if not agreement.has_agreed_terms:
            agreement.has_agreed_terms = True
            agreement.agreed_at = timezone.now()
            agreement.save()
        return redirect('payment')
    return redirect('checkout')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text', 'rating']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'placeholder': 'Write your feedback...',
                'rows': 4,
                'style': 'width: 100%; padding: 10px; border-radius: 8px;'
            }),
        }
    
@login_required
def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
    return redirect('products')

def non_refund(request):
    return render(request, 'non-refundable.html')