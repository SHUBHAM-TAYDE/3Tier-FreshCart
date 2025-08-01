# FreshCart/orders/views.py
# Handles order creation and history.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart # Make sure Cart is imported
from .models import Order, OrderItem
from .forms import OrderCreateForm # Now importing actual form

@login_required
def order_create(request):
    # Ensure the user has a cart, or create an empty one if not
    cart, created = Cart.objects.get_or_create(user=request.user)

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price, # Capture price at time of order
                    quantity=item.quantity
                )
                # Reduce product stock
                item.product.stock -= item.quantity
                item.product.save()

            cart.items.all().delete() # Clear the cart after order creation
            messages.success(request, f"Order {order.id} created successfully. Proceed to payment.")
            return redirect('payments:process_payment', order_id=order.id)
        else:
            messages.error(request, "Please correct the errors in the order form.")
    else:
        # Pre-fill form with user's existing details if available
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        # You might have a UserProfile model to store address, postal_code, city
        # if hasattr(request.user, 'userprofile'):
        #     initial_data['address'] = request.user.userprofile.address
        #     initial_data['postal_code'] = request.user.userprofile.postal_code
        #     initial_data['city'] = request.user.userprofile.city
        form = OrderCreateForm(initial=initial_data)
    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})
