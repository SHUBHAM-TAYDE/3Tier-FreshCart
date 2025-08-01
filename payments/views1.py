# FreshCart/payments/views.py
# Handles Stripe payment integration.

import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt # For webhook
from django.http import JsonResponse, HttpResponse
import json

from orders.models import Order

# Set your Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, paid=False)

    if request.method == 'POST':
        try:
            # Create a PaymentIntent with the order amount and currency
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.get_total_cost() * 100), # Amount in cents
                currency='inr', # Or your desired currency
                metadata={'order_id': order.id},
            )
            order.stripe_id = payment_intent.id # Save PaymentIntent ID to order
            order.save()
            return JsonResponse({'clientSecret': payment_intent.client_secret})
        except Exception as e:
            messages.error(request, f"Error creating payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    # For GET request, render the payment page with Stripe Publishable Key
    return render(request, 'payments/process_payment.html', {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@csrf_exempt # CSRF protection is handled by Stripe's webhook signature verification
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.save()
            # Send order confirmation email, update inventory, etc.
            print(f"PaymentIntent {payment_intent.id} succeeded for Order {order.id}")
        except Order.DoesNotExist:
            print(f"Order {order_id} not found for PaymentIntent {payment_intent.id}")
            return HttpResponse(status=404) # Order not found
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"PaymentIntent {payment_intent.id} failed.")
        # Handle failed payment, e.g., notify user
    # ... handle other event types
    
    return HttpResponse(status=200)
