"""Admin configuration for the inventory app."""
import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_register_view_success():
    client = Client()
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123'
    })
    assert response.status_code == 302  # redirect to login
    assert User.objects.filter(username='testuser').exists()
