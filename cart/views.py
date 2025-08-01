# FreshCart/cart/views.py
# Handles adding, updating, and removing items from the cart.

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def _get_or_create_cart(request):
    # This function needs to handle anonymous carts merging with user carts upon login
    # For simplicity, this version prioritizes authenticated user's cart.
    # A more robust solution would merge session cart into user's cart on login.
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If there was an anonymous session cart, merge it here
        if request.session.session_key:
            anonymous_cart_items = CartItem.objects.filter(cart__session_key=request.session.session_key)
            for item in anonymous_cart_items:
                existing_item = CartItem.objects.filter(cart=cart, product=item.product).first()
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                else:
                    item.cart = cart
                    item.save()
            # Delete the anonymous cart after merging
            Cart.objects.filter(session_key=request.session.session_key).delete()
            request.session.pop('session_key', None) # Clear session key
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user__isnull=True) # Ensure it's truly anonymous
    return cart

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    # Basic stock check
    if product.stock < quantity:
        messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock}")
        return redirect('products:product_detail', id=product.id, slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = _get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()
    messages.info(request, f"{product.name} removed from cart.")
    return redirect('cart:cart_detail')

# You might also want an update_cart_item view for quantity changes
# @require_POST
# def update_cart_item(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart = _get_or_create_cart(request)
#     quantity = int(request.POST.get('quantity', 1))
#     cart_item = get_object_or_404(CartItem, cart=cart, product=product)
#     if quantity > 0:
#         cart_item.quantity = quantity
#         cart_item.save()
#         messages.success(request, f"Quantity for {product.name} updated.")
#     else:
#         cart_item.delete()
#         messages.info(request, f"{product.name} removed from cart.")
#     return redirect('cart:cart_detail')

