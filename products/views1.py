# FreshCart/products/views.py
# Handles product listing and detail views.

from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.cache import cache # For Redis caching
from django.contrib.auth.decorators import login_required # Ensure user is logged in

@login_required # Protect this view
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # Example of caching product list
    # cached_products = cache.get('all_products_list')
    # if cached_products:
    #     products = cached_products
    # else:
    #     products = Product.objects.filter(available=True)
    #     cache.set('all_products_list', products, 60*15) # Cache for 15 minutes

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

@login_required # Protect this view
def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'products/product_detail.html', {'product': product})


