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
from django.contrib.auth import authenticate, login, get_backends
from .forms import CustomUserCreationForm
from django.contrib import messages
from .models import OTPVerification
from .forms import EmailForm, OTPForm, PasswordResetForm
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.

def terms(request):
    return render(request, 'terms.html')


def contact(request):
    return render(request, 'contact.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('products')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


def manual_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('products')
        else:
            # Re-render the home page with an error message
            return render(request, 'home.html', {
                'login_error': "Invalid email or password. Please try again."
            })

    return redirect('home')

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
    form = ReviewForm()
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

    return render(request, 'account_settings.html', {'form': form})

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

def forgot_password_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = f"{random.randint(100000, 999999)}"

                # Save OTP to DB
                OTPVerification.objects.create(email=email, otp_code=otp)

                send_mail(
                    subject="Your ICY Store OTP",
                    message=f"Use this OTP to reset your password: {otp}",
                    from_email="noreply@icystore.com",
                    recipient_list=[email],
                    fail_silently=False
                )

                request.session['reset_email'] = email
                return redirect('verify_otp')

            except User.DoesNotExist:
                messages.error(request, "No user found with that email")
    else:
        form = EmailForm()
    return render(request, 'forgot_password_otp.html', {'form': form})

def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            input_otp = form.cleaned_data['otp']
            try:
                latest_otp = OTPVerification.objects.filter(email=email, is_used=False).latest('created_at')

                if latest_otp.otp_code == input_otp:
                    if latest_otp.is_expired():
                        messages.error(request, "OTP has expired")
                    else:
                        latest_otp.is_used = True
                        latest_otp.save()
                        request.session['otp_verified'] = True
                        return redirect('reset_password_custom')
                else:
                    messages.error(request, "Invalid OTP")
            except OTPVerification.DoesNotExist:
                messages.error(request, "No OTP found for this email")
    else:
        form = OTPForm()
    return render(request, 'verify_otp.html', {'form': form})


def reset_password_custom_view(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified', False)

    if not email or not otp_verified:
        return redirect('forgot_password')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Clean up
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)

            messages.success(request, "Password reset successful. Please log in.")
            return redirect('home')
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password_custom.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, 'Your password was successfully updated.')
            return redirect('account_settings')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('account_settings')
    else:
        return redirect('account_settings')

