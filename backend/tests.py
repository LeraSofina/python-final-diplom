from django.test import TestCase

# Create your tests here.

from .models import User, ConfirmEmailToken
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class ApiTests(APITestCase):

    def test_register_account(self):
        count = User.objects.count()
        user = {
            'first_name': 'Marina',
            'last_name': 'Ivanova',
            'email': 'email@mail.ru',
            'password': '123',
            'company': 'zara',
            'position': 'statement',
            'type': 'client',
        }

        url = reverse('backend:user-register')
        response = self.client.post(url, user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)
        self.assertEqual(User.objects.count(), count + 1)

    def test_confirm_register(self):
        user = User.objects.create_user(
            first_name='Marina',
            last_name='Ivanova',
            email='email@mail.ru',
            password='123',
            company='zara',
            position='statement'
        )
        token = ConfirmEmailToken.objects.create(user_id=user.id).key
        url = reverse('backend:user-register-confirm')
        data = {'email': user.email, 'token': token}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)