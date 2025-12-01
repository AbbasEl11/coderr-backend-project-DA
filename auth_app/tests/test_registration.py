from rest_framework.test import APITestCase, APIClient
from django.urls import reverse


class RegistrationTests(APITestCase):

    def test_user_registration(self):
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
