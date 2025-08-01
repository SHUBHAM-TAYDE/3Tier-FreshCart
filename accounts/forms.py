# FreshCart/accounts/forms.py
# Defines forms for user authentication.

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

class UserLoginForm(AuthenticationForm):
    # Customizations for login form if needed
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'your@example.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': '********'}))

    class Meta:
        model = User
        fields = ['username', 'password']

class UserRegistrationForm(UserCreationForm):
    # Add any extra fields from your custom User model here
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'input-field'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-field', 'rows': 3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone_number', 'address',) # Include custom fields


