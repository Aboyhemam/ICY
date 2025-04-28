from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("logout/", views.logout_view, name='logout'),
    path('products/', views.products, name='products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_page'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/<int:item_id>/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('account-settings/', views.account_settings, name='account_settings'),
    path('payment/', views.payment, name='payment'),
]
