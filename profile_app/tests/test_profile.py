from rest_framework.test import APITestCase
from django.urls import reverse


def register_user(self):

    reg_url = reverse('registration')

    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'securepassword123',
        'repeated_password': 'securepassword123',
        'type': 'customer'
    }

    response = self.client.post(reg_url, data, format='json')
    self.assertIn(response.status_code, [200, 201])
    token = response.data.get('token')
    self.assertIsNotNone(token)
    return token


class ProfileTests(APITestCase):

    def test_get_profile(self):

        token = register_user(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        url = reverse('profile-detail', kwargs={'pk': 1})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)

        self.assertIn('user', response.data)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('description', response.data)
        self.assertIn('location', response.data)
        self.assertIn('tel', response.data)
        self.assertIn('working_hours', response.data)

        type_choices = ['customer', 'business']
        self.assertIn(response.data['type'], type_choices)
        self.assertIn('created_at', response.data)

    def test_patch_profile(self):

        token = register_user(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        url = reverse('profile-detail', kwargs={'pk': 1})

        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'location': 'New York',
            'tel': '1234567890',
            'description': 'A test user',
            'working_hours': '9am - 5pm',
            'email': 'John@example.com',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])
        self.assertEqual(response.data['location'], data['location'])
        self.assertEqual(response.data['tel'], data['tel'])
        self.assertEqual(response.data['description'], data['description'])
        self.assertEqual(response.data['working_hours'], data['working_hours'])

        types = ['customer', 'business']
        self.assertIn(response.data['type'], types)
        self.assertEqual(response.data['email'], data['email'])
        self.assertIn('created_at', response.data)

    def _register_user_with_type(self, username, email, password, user_type):
        reg_url = reverse('registration')

        data = {
            'username': username,
            'email': email,
            'password': password,
            'repeated_password': password,
            'type': user_type
        }

        response = self.client.post(reg_url, data, format='json')
        self.assertIn(response.status_code, [200, 201])
        token = response.data.get('token')
        self.assertIsNotNone(token)
        return token

    def test_list_profiles_business_and_customer(self):
        customer_token = self._register_user_with_type(
            'customeruser', 'customer@example.de', 'securepassword123', 'customer')

        business_token = self._register_user_with_type(
            'businessuser', 'business@example.de', 'securepassword123', 'business')

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + customer_token)
        customer_url = reverse('profile-customer')
        customer_response = self.client.get(customer_url, format='json')
        self.assertEqual(customer_response.status_code, 200)
        self.assertEqual(len(customer_response.data), 1)
        self.assertEqual(customer_response.data[0]['username'], 'customeruser')
        self.assertEqual(customer_response.data[0]['type'], 'customer')

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + business_token)
        business_url = reverse('profile-business')
        business_response = self.client.get(business_url, format='json')
        self.assertEqual(business_response.status_code, 200)
        self.assertEqual(len(business_response.data), 1)
        self.assertEqual(business_response.data[0]['username'], 'businessuser')
        self.assertEqual(business_response.data[0]['type'], 'business')
