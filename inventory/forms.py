"""Forms for user registration, product management, and order handling in the inventory app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Order


class RegisterForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    """User registration form with email field."""
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProductForm(forms.ModelForm):
    """Form to create or update product details."""

    class Meta:
        model = Product
        fields = '__all__'


class OrderForm(forms.ModelForm):
    """Form to create or update an order (user and created_at are excluded)."""

    class Meta:
        model = Order
        exclude = ['user', 'created_at']
