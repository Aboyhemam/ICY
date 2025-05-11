from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("terms/", views.terms, name='terms'),
    path("support/", views.support, name='support'),
    path("contact/", views.contact, name='contact'),
    path("logout/", views.logout_view, name='logout'),
    path('products/', views.products, name='products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_page'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/<int:item_id>/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('account-settings/', views.account_settings, name='account_settings'),
    path('payment/', views.payment, name='payment'),
    path('products/<int:game_id>/', views.products_by_game, name='products_by_game'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('confirm_terms_and_payment/', views.confirm_terms_and_payment, name='confirm_terms_and_payment'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('non_refund/', views.non_refund, name='non_refund'),
]
