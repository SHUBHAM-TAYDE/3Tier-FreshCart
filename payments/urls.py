# FreshCart/payments/urls.py
# URL patterns for the payments app.

from django.urls import path
from . import views

app_name = 'payments' # Namespace for payments URLs

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]

