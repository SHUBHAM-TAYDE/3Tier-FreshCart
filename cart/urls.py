# FreshCart/cart/urls.py
# URL patterns for the cart app.

from django.urls import path
from . import views

app_name = 'cart' # Namespace for cart URLs

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    # path('update/<int:product_id>/', views.update_cart_item, name='update_cart_item'), # If you implement update
]

