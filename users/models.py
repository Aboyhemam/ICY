from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class Game(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='game_images/')  # Add this line

    def __str__(self):
        return self.name

class Product(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.game.name})"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)  # NEW
    player_id = models.CharField(max_length=255)
    server_id = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"


class Order(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, unique=True)
    player_id = models.CharField(max_length=255, null=False, default='unknown')
    server_id = models.CharField(max_length=255, null=False, default='unknown')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)  # NEW

    def __str__(self):
        return f"Order {self.order_id} by {self.username}"




class UserAgreement(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_agreed_terms = models.BooleanField(default=False)
    agreed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Agreement for {self.user.username}"
    
class FAQ(models.Model):
    Questions= models.CharField(max_length=300)
    Answers= models.CharField(max_length=300)
    

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 5)])  # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} - {self.rating} Stars'
    
class OTPVerification(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp_code} - {'Expired' if self.is_expired() else 'Active'}"
    
