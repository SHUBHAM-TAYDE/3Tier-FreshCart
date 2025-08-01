# FreshCart/orders/urls.py
# URL patterns for the orders app.

from django.urls import path
from . import views

app_name = 'orders' # Namespace for orders URLs

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
]

