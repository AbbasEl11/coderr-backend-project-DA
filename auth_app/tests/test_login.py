"""
Tests for user login functionality.
"""
from rest_framework.test import APITestCase
from django.urls import reverse


class LoginTests(APITestCase):
    """
    Test cases for user authentication and login endpoints.
    """
    def test_login_success(self):
        """Test successful user login after registration - status code 200"""
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

    def test_login_wrong_password(self):
        """Test login failure with incorrect password - status code 400"""
        register_url = reverse('registration')

        registration_data = {
            'username': 'loginuser2',
            'email': 'login2@mail.de',
            'password': 'correctpassword123',
            'repeated_password': 'correctpassword123',
            'type': 'customer'
        }
        self.client.post(register_url, registration_data, format='json')

        login_url = reverse('login')
        login_data = {
            'username': 'loginuser2',
            'password': 'wrongpassword'
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_login_nonexistent_user(self):
        """Test login failure with non-existent username - status code 400"""
        login_url = reverse('login')
        login_data = {
            'username': 'nonexistentuser',
            'password': 'somepassword'
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_login_missing_username(self):
        """Test login failure with missing username - status code 400"""
        login_url = reverse('login')
        login_data = {
            'password': 'somepassword'
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_login_missing_password(self):
        """Test login failure with missing password - status code 400"""
        login_url = reverse('login')
        login_data = {
            'username': 'someuser'
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_login_empty_credentials(self):
        """Test login failure with empty credentials - status code 400"""
        login_url = reverse('login')
        login_data = {
            'username': '',
            'password': ''
        }

        response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(response.status_code, 400)
