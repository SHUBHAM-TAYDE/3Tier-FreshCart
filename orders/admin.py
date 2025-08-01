# FreshCart/orders/admin.py
# Registers Order and OrderItem models with the Django admin interface.

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Useful if you have many products
    readonly_fields = ['price'] # Price is captured at order time

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'paid', 'created_at', 'get_total_cost']
    list_filter = ['paid', 'created_at', 'updated_at']
    search_fields = ['id', 'user__username', 'first_name', 'last_name', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'stripe_id'] # These fields should not be editable in admin

    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Total Cost'

