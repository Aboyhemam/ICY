from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # This links cart items to users
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # This links each cart item to a product
    player_id = models.CharField(max_length=255)  # Store the player's ID
    server_id = models.CharField(max_length=255)  # Store the server ID
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product
    added_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the item was added to the cart

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
    status = models.CharField(max_length=20, default="Pending")  # Add this line if needed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.username}"

transaction_id = models.CharField(max_length=100, blank=True, null=True)