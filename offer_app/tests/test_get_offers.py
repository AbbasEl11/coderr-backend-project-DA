from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User


class GetOffersTests(APITestCase):

    def test_get_offers(self):

        url = reverse('offers-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)


class PostOfferTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    """
    successful post offer test for unauthenticated user
    """

    def test_post_offer_unauthenticated(self):

        url = reverse('offers-list')
        data = {
            "title": "Test Offer",
            "description": "This is a test offer.",
            "details": [
                {
                    "title": "Basic Plan",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": "50.00",
                    "features": ["Feature 1", "Feature 2"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Plan",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": "100.00",
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Plan",
                    "revisions": 3,
                    "delivery_time_in_days": 1,
                    "price": "150.00",
                    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['description'], data['description'])
        self.assertEqual(len(response.data['details']), 3)
