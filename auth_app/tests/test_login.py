from rest_framework.test import APITestCase
from django.urls import reverse


class LoginTests(APITestCase):
    def test_login_success(self):
        """Test successful user login after registration"""
        register_url = reverse('registration')

        registration_data = {
            'username': 'loginuser',
            'email': 'login@mail.de',
            'password': 'loginpassword123',
            'repeated_password': 'loginpassword123',
            'type': 'customer'
        }
        self.client.post(register_url, registration_data, format='json')

        login_url = reverse('login')
        login_data = {
            'username': 'loginuser',
            'password': 'loginpassword123'
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], login_data['username'])
        self.assertEqual(response.data['email'], registration_data['email'])
        self.assertIn('user_id', response.data)

    def test_login_failure(self):
        """Test login failure with incorrect credentials."""

        login_url = reverse('login')
        login_data = {
            'username': 'nonexistentuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
