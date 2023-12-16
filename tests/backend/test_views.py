from django.urls import reverse
from rest_framework import status
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from backend.models import ConfirmEmailToken

@pytest.mark.django_db
def test_register_account_with_valid_data(client):
    url = reverse('backend:user-register')
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'secure_password',
        'company': 'Example Company',
        'position': 'Developer',
    }

    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['Status'] is True

@pytest.mark.django_db
def test_register_account_with_invalid_data(client):
    url = reverse('backend:user-register')
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        # Отсутствует 'email'
        'password': 'secure_password',
        'company': 'Example Company',
        'position': 'Developer',
    }

    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['Status'] is False
    assert 'Errors' in response.json()

@pytest.mark.django_db
def test_confirm_account_view():
    client = APIClient()

    # Create a user and a corresponding confirmation token
    user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
    token = ConfirmEmailToken.objects.create(user=user)

    # Attempt to confirm the account with valid data
    data = {
        'email': 'testuser@example.com',
        'token': token.key,
    }
    response = client.post('backend:user/register/confirm', data=data, format='json')

    # Check that the response is successful and the account is confirmed
    assert response.status_code == 200
    assert response.json()['Status'] is True

    # Check that the user is now active
    user.refresh_from_db()
    assert user.is_active is True

    # Check that the token is deleted
    with pytest.raises(ConfirmEmailToken.DoesNotExist):
        token.refresh_from_db()

@pytest.mark.django_db
def test_account_details_view_authenticated():
    client = APIClient()
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.force_authenticate(user=user)
    response = client.get('backend:user-details')
    assert response.status_code == 200
    assert response.json()['Status'] is True

@pytest.mark.django_db
def test_account_details_view_unauthenticated():
    client = APIClient()
    response = client.get('backend:user-details')
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type.lower():
        # If it's JSON, check the status code and assertions accordingly
        assert response.status_code == 404
        assert 'Not Found' in response.content.decode('utf-8')
    else:
        # If it's not JSON, check for HTML content
        assert response.status_code == 404
        assert 'Not Found' in response.content.decode('utf-8')

# Additional test for LoginAccount
@pytest.mark.django_db
def test_login_account_view_invalid_credentials():
    client = APIClient()
    User.objects.create_user(username='testuser', password='testpassword')
    data = {
        'email': 'testuser',
        'password': 'invalid_password',
    }
    response = client.post('/backend:user-login', data=data, format='json')
    assert response.status_code == 200
    assert response.json()['Status'] is False
    assert 'Unable to authenticate' in response.json()['Errors']