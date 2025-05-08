from django.contrib import admin

from django.contrib import admin
from .models import Product,Cart,Order,Game,UserAgreement

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Game)
admin.site.register(UserAgreement)

# Register your models here.
