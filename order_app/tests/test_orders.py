from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from offer_app.models import Offer, OfferDetail
from profile_app.models import Profile


class OrderTests(APITestCase):

    def test_order_list_success(self):
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
