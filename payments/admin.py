# FreshCart/payments/admin.py
# Registers any payment-related models with the Django admin interface.
# Currently, payment status is handled within the Order model.
# You might add models here for payment transactions or refunds if needed.

from django.contrib import admin
# from .models import PaymentTransaction # Example if you create a PaymentTransaction model

# @admin.register(PaymentTransaction)
# class PaymentTransactionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'order', 'amount', 'transaction_id', 'status', 'created_at']
#     list_filter = ['status', 'created_at']
#     search_fields = ['order__id', 'transaction_id']
