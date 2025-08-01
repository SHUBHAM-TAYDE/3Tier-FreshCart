# FreshCart/accounts/admin.py
# Registers your custom User model with the Django admin interface.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add your custom fields to the list_display, fieldsets, and add_fieldsets
    list_display = UserAdmin.list_display + ('phone_number', 'address',)
    fieldsets = UserAdmin.fieldsets + (
        ('Contact Info', {'fields': ('phone_number', 'address',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Contact Info', {'fields': ('phone_number', 'address',)}),
    )

