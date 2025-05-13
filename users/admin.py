from django.contrib import admin

from django.contrib import admin
from .models import Product,Cart,Order,Game,UserAgreement,FAQ, Review, OTPVerification

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Game)
admin.site.register(UserAgreement)
admin.site.register(FAQ)
admin.site.register(Review)
@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email', 'otp_code')
# Register your models here.
