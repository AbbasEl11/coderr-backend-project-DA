from rest_framework.test import APITestCase, APIClient
from django.urls import reverse


class RegistrationTests(APITestCase):
    """Test suite for user registration endpoint."""

    def test_user_registration_customer(self):
        """
        Test successful customer user registration.
        
        Verifies customer registration with valid credentials returns
        201 status code and authentication token.
        """
        url = reverse('registration')

        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'securepassword123',
            'repeated_password': 'securepassword123',
            'type': 'customer'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertIn('user_id', response.data)

    def test_user_registration_business(self):
        """Test successful business user registration with status code 201"""
        url = reverse('registration')

        data = {
            'username': 'businessuser',
            'email': 'business@example.com',
            'password': 'securepassword123',
            'repeated_password': 'securepassword123',
            'type': 'business'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertIn('user_id', response.data)

    def test_registration_password_mismatch(self):
        """Test registration failure with mismatched passwords - status code 400"""
        url = reverse('registration')

        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'securepassword123',
            'repeated_password': 'differentpassword',
            'type': 'customer'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_registration_missing_username(self):
        """Test registration failure with missing username - status code 400"""
        url = reverse('registration')

        data = {
            'email': 'testuser3@example.com',
            'password': 'securepassword123',
            'repeated_password': 'securepassword123',
            'type': 'customer'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_registration_missing_email(self):
        """Test registration failure with missing email - status code 400"""
        url = reverse('registration')

        data = {
            'username': 'testuser4',
            'password': 'securepassword123',
            'repeated_password': 'securepassword123',
            'type': 'customer'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_registration_missing_password(self):
        """Test registration failure with missing password - status code 400"""
        url = reverse('registration')

        data = {
            'username': 'testuser5',
            'email': 'testuser5@example.com',
            'repeated_password': 'securepassword123',
            'type': 'customer'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_registration_invalid_email(self):
        """Test registration failure with invalid email format - status code 400"""
        url = reverse('registration')

        data = {
            'username': 'testuser6',
            'email': 'invalidemail',
            'password': 'securepassword123',
            'repeated_password': 'securepassword123',
            'type': 'customer'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_registration_duplicate_username(self):
        """Test registration failure with duplicate username - status code 400"""
        url = reverse('registration')

        data = {
            'username': 'duplicateuser',
            'email': 'duplicate1@example.com',
            'password': 'securepassword123',
            'repeated_password': 'securepassword123',
            'type': 'customer'
        }

        self.client.post(url, data, format='json')

        data['email'] = 'duplicate2@example.com'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)
