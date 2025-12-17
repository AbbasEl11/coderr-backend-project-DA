"""
Tests for user profile management functionality.
"""
from rest_framework.test import APITestCase
from django.urls import reverse


def register_user(self):
    """
    Helper function to register a test user.

    Returns:
        str: Authentication token for the registered user.
    """
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
    """Tests for profile CRUD operations."""

    def test_get_profile_success_200(self):
        """Test GET /api/profile/{pk}/ - Status 200: Profile data was successfully retrieved"""
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

        self.assertIsNotNone(response.data['first_name'])
        self.assertIsNotNone(response.data['last_name'])
        self.assertIsNotNone(response.data['location'])
        self.assertIsNotNone(response.data['tel'])
        self.assertIsNotNone(response.data['description'])
        self.assertIsNotNone(response.data['working_hours'])

        self.assertIsInstance(response.data['first_name'], str)
        self.assertIsInstance(response.data['last_name'], str)
        self.assertIsInstance(response.data['location'], str)
        self.assertIsInstance(response.data['tel'], str)
        self.assertIsInstance(response.data['description'], str)
        self.assertIsInstance(response.data['working_hours'], str)

        type_choices = ['customer', 'business']
        self.assertIn(response.data['type'], type_choices)
        self.assertIn('created_at', response.data)

    def test_get_profile_unauthenticated_401(self):
        """Test GET /api/profile/{pk}/ - Status 401: User is not authenticated"""
        token = register_user(self)
        
        url = reverse('profile-detail', kwargs={'pk': 1})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 401)

    def test_get_profile_not_found_404(self):
        """Test GET /api/profile/{pk}/ - Status 404: User profile was not found"""
        token = register_user(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        url = reverse('profile-detail', kwargs={'pk': 9999})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 404)

    def test_patch_profile_success_200(self):
        """Test PATCH /api/profile/{pk}/ - Status 200: Profile was successfully updated"""

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

        self.assertIsNotNone(response.data['first_name'])
        self.assertIsNotNone(response.data['last_name'])
        self.assertIsNotNone(response.data['location'])
        self.assertIsNotNone(response.data['tel'])
        self.assertIsNotNone(response.data['description'])
        self.assertIsNotNone(response.data['working_hours'])

        types = ['customer', 'business']
        self.assertIn(response.data['type'], types)
        self.assertEqual(response.data['email'], data['email'])
        self.assertIn('created_at', response.data)

    def test_patch_profile_unauthenticated_401(self):
        """Test PATCH /api/profile/{pk}/ - Status 401: User is not authenticated"""
        token = register_user(self)
        
        url = reverse('profile-detail', kwargs={'pk': 1})
        data = {'first_name': 'John'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, 401)

    def test_patch_profile_forbidden_403(self):
        """Test PATCH /api/profile/{pk}/ - Status 403: Authenticated user is not the owner of the profile"""
        token1 = self._register_user_with_type(
            'user1', 'user1@example.com', 'password123', 'customer')
        token2 = self._register_user_with_type(
            'user2', 'user2@example.com', 'password123', 'customer')

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2)
        url = reverse('profile-detail', kwargs={'pk': 1})
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, 403)

    def test_patch_profile_not_found_404(self):
        """Test PATCH /api/profile/{pk}/ - Status 404: User profile was not found"""
        token = register_user(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        url = reverse('profile-detail', kwargs={'pk': 9999})
        data = {'first_name': 'John'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, 404)

    def _register_user_with_type(self, username, email, password, user_type):
        """Helper method to register a user with specific type."""
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

    def test_list_profiles_business_success_200(self):
        """Test GET /api/profiles/business/ - Status 200: Successful response with the list of business users"""
        customer_token = self._register_user_with_type(
            'customeruser', 'customer@example.de', 'securepassword123', 'customer')

        business_token = self._register_user_with_type(
            'businessuser', 'business@example.de', 'securepassword123', 'business')

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + business_token)
        business_url = reverse('profile-business')
        business_response = self.client.get(business_url, format='json')
        
        self.assertEqual(business_response.status_code, 200)
        self.assertEqual(len(business_response.data), 1)
        self.assertEqual(business_response.data[0]['username'], 'businessuser')
        self.assertEqual(business_response.data[0]['type'], 'business')
        
        self.assertIsNotNone(business_response.data[0]['first_name'])
        self.assertIsNotNone(business_response.data[0]['last_name'])
        self.assertIsNotNone(business_response.data[0]['location'])
        self.assertIsNotNone(business_response.data[0]['tel'])
        self.assertIsNotNone(business_response.data[0]['description'])
        self.assertIsNotNone(business_response.data[0]['working_hours'])

    def test_list_profiles_business_unauthenticated_401(self):
        """Test GET /api/profiles/business/ - Status 401: User is not authenticated"""
        business_url = reverse('profile-business')
        response = self.client.get(business_url, format='json')
        
        self.assertEqual(response.status_code, 401)

    def test_list_profiles_customer_success_200(self):
        """Test GET /api/profiles/customer/ - Status 200: Successful response with the list of customer profiles"""
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
        
        self.assertIn('user', customer_response.data[0])
        self.assertIn('username', customer_response.data[0])
        self.assertIn('first_name', customer_response.data[0])
        self.assertIn('last_name', customer_response.data[0])
        self.assertIn('file', customer_response.data[0])
        self.assertIn('type', customer_response.data[0])
        
        self.assertIsNotNone(customer_response.data[0]['first_name'])
        self.assertIsNotNone(customer_response.data[0]['last_name'])

    def test_list_profiles_customer_unauthenticated_401(self):
        """Test GET /api/profiles/customer/ - Status 401: User is not authenticated"""
        customer_url = reverse('profile-customer')
        response = self.client.get(customer_url, format='json')
        
        self.assertEqual(response.status_code, 401)
