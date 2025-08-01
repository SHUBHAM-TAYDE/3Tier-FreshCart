# FreshCart/freshcart_project/urls.py
# This is the main URL configuration for your FreshCart project.

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from django.views.generic import TemplateView # Removed as we'll use proper views
from accounts import views as accounts_views # Import views from accounts app
from products import views as products_views # Import views from products app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), # Include URLs from the accounts app
    path('products/', include('products.urls')), # Include URLs from the products app
    path('cart/', include('cart.urls')),         # Include URLs from the cart app
    path('orders/', include('orders.urls')),     # Include URLs from the orders app
    path('payments/', include('payments.urls')), # Include URLs from the payments app

    # Now using actual Django views for login and landing page
    path('', accounts_views.user_login, name='login_page'), # Maps root to login view
    path('landing/', products_views.product_list, name='landing_page'), # Maps /landing/ to product list view
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


