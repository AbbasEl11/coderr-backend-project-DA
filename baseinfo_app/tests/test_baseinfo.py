"""
Tests for base info endpoint functionality.
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from profile_app.models import Profile
from review_app.models import Review
from offer_app.models import Offer, OfferDetail


class BaseInfoHappyPathTests(APITestCase):
    """Tests for the base-info endpoint - happy paths."""

    def setUp(self):
        """Set up test data for base info tests."""
        self.business_user1 = User.objects.create_user(
            username='business1', password='testpass123'
        )
        Profile.objects.create(user=self.business_user1, type='business')

        self.business_user2 = User.objects.create_user(
            username='business2', password='testpass123'
        )
        Profile.objects.create(user=self.business_user2, type='business')

        self.customer_user1 = User.objects.create_user(
            username='customer1', password='testpass123'
        )
        Profile.objects.create(user=self.customer_user1, type='customer')

        self.customer_user2 = User.objects.create_user(
            username='customer2', password='testpass123'
        )
        Profile.objects.create(user=self.customer_user2, type='customer')

        self.offer1 = Offer.objects.create(
            user=self.business_user1,
            title="Webentwicklung",
            description="Professionelle Webseiten"
        )
        OfferDetail.objects.create(
            offer=self.offer1,
            title="Basic Webentwicklung",
            revisions=2,
            delivery_time_in_days=14,
            price=1000,
            features=["Feature 1", "Feature 2"],
            offer_type='basic'
        )

        self.offer2 = Offer.objects.create(
            user=self.business_user1,
            title="Logo Design",
            description="Kreative Logos"
        )
        OfferDetail.objects.create(
            offer=self.offer2,
            title="Basic Logo",
            revisions=3,
            delivery_time_in_days=7,
            price=500,
            features=["Feature 1"],
            offer_type='basic'
        )

        self.offer3 = Offer.objects.create(
            user=self.business_user2,
            title="SEO Optimierung",
            description="Google Rankings verbessern"
        )
        OfferDetail.objects.create(
            offer=self.offer3,
            title="Standard SEO",
            revisions=5,
            delivery_time_in_days=30,
            price=800,
            features=["Feature 1", "Feature 2"],
            offer_type='standard'
        )

        self.review1 = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user1,
            rating=5,
            description="Hervorragende Arbeit!"
        )

        self.review2 = Review.objects.create(
            reviewer=self.customer_user2,
            business_user=self.business_user1,
            rating=4,
            description="Sehr gut, schnelle Lieferung"
        )

        self.review3 = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user2,
            rating=5,
            description="Perfekt!"
        )

        self.url = reverse('base-info')

    def test_get_base_info_without_authentication(self):
        """Test that base info can be retrieved without authentication (AllowAny)."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)

    def test_get_base_info_with_authentication_as_customer(self):
        """Test that base info can be retrieved as an authenticated customer."""
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)

    def test_get_base_info_with_authentication_as_business(self):
        """Test that base info can be retrieved as an authenticated business user."""
        self.client.force_authenticate(user=self.business_user1)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)

    def test_base_info_returns_correct_review_count(self):
        """Test that correct review count is returned."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 3)

    def test_base_info_returns_correct_average_rating(self):
        """Test that correct average rating is returned."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_avg = round((5 + 4 + 5) / 3, 2)
        self.assertEqual(response.data['average_rating'], expected_avg)

    def test_base_info_returns_correct_business_profile_count(self):
        """Test that correct business profile count is returned."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['business_profile_count'], 2)

    def test_base_info_returns_correct_offer_count(self):
        """Test that correct offer count is returned."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['offer_count'], 3)

    def test_base_info_with_no_data(self):
        """Test that base info returns zero values when database is empty."""
        Review.objects.all().delete()
        Offer.objects.all().delete()
        Profile.objects.filter(type='business').delete()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0)
        self.assertEqual(response.data['business_profile_count'], 0)
        self.assertEqual(response.data['offer_count'], 0)

    def test_base_info_average_rating_with_single_review(self):
        """Test average rating calculation with a single review."""
        Review.objects.all().delete()
        Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user1,
            rating=3,
            description="Okay"
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 1)
        self.assertEqual(response.data['average_rating'], 3.0)

    def test_base_info_data_types(self):
        """Test that returned data types are correct."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['review_count'], int)
        self.assertIsInstance(response.data['average_rating'], (int, float))
        self.assertIsInstance(response.data['business_profile_count'], int)
        self.assertIsInstance(response.data['offer_count'], int)

    def test_base_info_response_structure(self):
        """Test that response structure contains all required fields."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertTrue('review_count' in response.data)
        self.assertTrue('average_rating' in response.data)
        self.assertTrue('business_profile_count' in response.data)
        self.assertTrue('offer_count' in response.data)


class BaseInfoUnhappyPathTests(APITestCase):
    """Tests for the base-info endpoint - unhappy paths."""

    def setUp(self):
        """Set up test data for unhappy path tests."""
        self.url = reverse('base-info')
        
        self.business_user = User.objects.create_user(
            username='business', password='testpass123'
        )
        Profile.objects.create(user=self.business_user, type='business')
        
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123'
        )
        Profile.objects.create(user=self.customer_user, type='customer')

    def test_post_method_not_allowed(self):
        """Test that POST request is not allowed (405 Method Not Allowed)."""
        response = self.client.post(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_method_not_allowed(self):
        """Test that PUT request is not allowed (405 Method Not Allowed)."""
        response = self.client.put(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_method_not_allowed(self):
        """Test that PATCH request is not allowed (405 Method Not Allowed)."""
        response = self.client.patch(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_method_not_allowed(self):
        """Test that DELETE request is not allowed (405 Method Not Allowed)."""
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_base_info_with_invalid_url(self):
        """Test that invalid URL returns 404."""
        invalid_url = '/api/base-info-invalid/'
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_base_info_with_query_parameters_ignored(self):
        """Test that query parameters are ignored and response is still successful."""
        response = self.client.get(self.url, {'invalid_param': 'value'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)

    def test_base_info_with_trailing_slash_variation(self):
        """Test that URL variations without trailing slash work or redirect."""
        url_without_slash = '/api/base-info'
        response = self.client.get(url_without_slash)
        
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, 
            status.HTTP_301_MOVED_PERMANENTLY
        ])

    def test_base_info_average_rating_rounding(self):
        """Test that average rating is correctly rounded to 2 decimal places."""
        Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=1,
            description="Test 1"
        )
        Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=2,
            description="Test 2"
        )
        Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=2,
            description="Test 3"
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_avg = round((1 + 2 + 2) / 3, 2)
        self.assertEqual(response.data['average_rating'], expected_avg)
        avg_str = str(response.data['average_rating'])
        if '.' in avg_str:
            decimal_places = len(avg_str.split('.')[1])
            self.assertLessEqual(decimal_places, 2)

    def test_base_info_only_customer_profiles_not_counted(self):
        """Test that only business profiles are counted, not customer profiles."""
        customer2 = User.objects.create_user(
            username='customer2', password='testpass123'
        )
        Profile.objects.create(user=customer2, type='customer')
        
        customer3 = User.objects.create_user(
            username='customer3', password='testpass123'
        )
        Profile.objects.create(user=customer3, type='customer')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['business_profile_count'], 1)

    def test_base_info_with_accept_header_json(self):
        """Test that request with Accept header works correctly."""
        response = self.client.get(self.url, HTTP_ACCEPT='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_base_info_concurrent_data_consistency(self):
        """Test that data remains consistent across multiple calls."""
        test_offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test"
        )
        OfferDetail.objects.create(
            offer=test_offer,
            title="Test Detail",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Test"],
            offer_type='basic'
        )
        
        response1 = self.client.get(self.url)
        response2 = self.client.get(self.url)
        response3 = self.client.get(self.url)
        
        self.assertEqual(response1.data, response2.data)
        self.assertEqual(response2.data, response3.data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
