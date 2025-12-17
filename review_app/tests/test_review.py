"""
Tests for review management functionality.
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from profile_app.models import Profile
from review_app.models import Review


class ListReviewsHappyPathTests(APITestCase):
    """Tests for listing reviews - happy paths."""

    def setUp(self):
        """Set up test data for list reviews tests."""
        self.business_user1 = User.objects.create_user(
            username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user1, type='business')

        self.business_user2 = User.objects.create_user(
            username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')

        self.customer_user1 = User.objects.create_user(
            username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user1, type='customer')

        self.customer_user2 = User.objects.create_user(
            username='customer2', password='testpass123')
        Profile.objects.create(user=self.customer_user2, type='customer')

        self.review1 = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user1,
            rating=4,
            description="Sehr professioneller Service."
        )

        self.review2 = Review.objects.create(
            reviewer=self.customer_user2,
            business_user=self.business_user1,
            rating=5,
            description="Top Qualität und schnelle Lieferung!"
        )

        self.review3 = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user2,
            rating=3,
            description="Gut, aber Verbesserungspotenzial."
        )

    def test_list_all_reviews_as_authenticated_user(self):
        """Test that authenticated users can list all reviews."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_reviews_by_business_user_id(self):
        """Test filtering reviews by business_user_id."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-list')
        response = self.client.get(url, {'business_user': self.business_user1.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review['business_user'], self.business_user1.id)

    def test_filter_reviews_by_reviewer_id(self):
        """Test filtering reviews by reviewer_id."""
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('reviews-list')
        response = self.client.get(url, {'reviewer_id': self.customer_user1.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review['reviewer'], self.customer_user1.id)

    def test_order_reviews_by_rating_ascending(self):
        """Test ordering reviews by rating ascending."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-list')
        response = self.client.get(url, {'ordering': 'rating'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [review['rating'] for review in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_order_reviews_by_rating_descending(self):
        """Test ordering reviews by rating descending."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-list')
        response = self.client.get(url, {'ordering': '-rating'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [review['rating'] for review in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_order_reviews_by_updated_at(self):
        """Test ordering reviews by updated_at."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-list')
        response = self.client.get(url, {'ordering': 'updated_at'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class ListReviewsUnhappyPathTests(APITestCase):
    """Tests for listing reviews - unhappy paths."""

    def setUp(self):
        """Set up test data for list reviews unhappy path tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

    def test_list_reviews_without_authentication(self):
        """Test that unauthenticated users receive 401."""
        url = reverse('reviews-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RetrieveReviewHappyPathTests(APITestCase):
    """Tests for retrieving single review - happy paths."""

    def setUp(self):
        """Set up test data for retrieve review tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=5,
            description="Hervorragender Service!"
        )

    def test_retrieve_review_as_authenticated_user(self):
        """Test that authenticated users can retrieve a review."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.review.id)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], "Hervorragender Service!")
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['reviewer'], self.customer_user.id)


class RetrieveReviewUnhappyPathTests(APITestCase):
    """Tests for retrieving single review - unhappy paths."""

    def setUp(self):
        """Set up test data for retrieve review unhappy path tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

    def test_retrieve_review_without_authentication(self):
        """Test that unauthenticated users receive 401."""
        review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description="Test"
        )
        url = reverse('reviews-detail', kwargs={'pk': review.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_review(self):
        """Test that retrieving nonexistent review returns 404."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateReviewHappyPathTests(APITestCase):
    """Tests for creating reviews - happy paths."""

    def setUp(self):
        """Set up test data for create review tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

    def test_create_review_as_customer(self):
        """Test that customer can create a review."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Alles war toll!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['reviewer'], self.customer_user.id)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['description'], 'Alles war toll!')
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)

        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.reviewer, self.customer_user)
        self.assertEqual(review.business_user, self.business_user)

    def test_create_review_with_minimum_rating(self):
        """Test creating review with minimum rating (1)."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 1,
            'description': 'Nicht zufrieden.'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 1)

    def test_create_review_with_maximum_rating(self):
        """Test creating review with maximum rating (5)."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Perfekt!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)


class CreateReviewUnhappyPathTests(APITestCase):
    """Tests for creating reviews - unhappy paths."""

    def setUp(self):
        """Set up test data for create review unhappy path tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.business_user2 = User.objects.create_user(
            username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')

    def test_create_review_without_authentication(self):
        """Test that unauthenticated users receive 401."""
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_as_business_user(self):
        """Test that business users cannot create reviews."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user2.id,
            'rating': 5,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_without_customer_profile(self):
        """Test that users without customer profile cannot create reviews."""
        user_without_profile = User.objects.create_user(
            username='noprofile', password='testpass123')
        self.client.force_authenticate(user=user_without_profile)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_review_for_same_business_user(self):
        """Test that customer can only create one review per business user."""
        # Erste Bewertung erstellen
        Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description="Erste Bewertung"
        )

        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Zweite Bewertung'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_with_missing_rating(self):
        """Test that creating review without rating field returns 400."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'description': 'Test ohne Rating'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    def test_create_review_with_missing_description(self):
        """Test that creating review without description returns 400."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 4
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)

    def test_create_review_with_missing_business_user(self):
        """Test that creating review without business_user returns 400."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'rating': 4,
            'description': 'Test ohne Business-Benutzer'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user', response.data)

    def test_create_review_with_nonexistent_business_user(self):
        """Test that creating review with nonexistent business_user returns 400."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': 99999,
            'rating': 4,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_with_invalid_rating_too_low(self):
        """Test that creating review with rating too low (0) returns 400."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 0,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_with_invalid_rating_too_high(self):
        """Test that creating review with rating too high (6) returns 400."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 6,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateReviewHappyPathTests(APITestCase):
    """Tests for updating reviews - happy paths."""

    def setUp(self):
        """Set up test data for update review tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description="Ursprüngliche Bewertung"
        )

    def test_update_review_rating_with_patch(self):
        """Test that creator can update rating with PATCH."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {
            'rating': 5
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], "Ursprüngliche Bewertung")

        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)

    def test_update_review_description_with_patch(self):
        """Test that creator can update description with PATCH."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {
            'description': 'Noch besser als erwartet!'
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Noch besser als erwartet!')
        self.assertEqual(response.data['rating'], 4)

        self.review.refresh_from_db()
        self.assertEqual(self.review.description, 'Noch besser als erwartet!')

    def test_update_review_rating_and_description_with_patch(self):
        """Test that creator can update rating and description simultaneously with PATCH."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {
            'rating': 5,
            'description': 'Noch besser als erwartet!'
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Noch besser als erwartet!')

        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, 'Noch besser als erwartet!')

    def test_updated_at_changes_after_update(self):
        """Test that updated_at changes after an update."""
        self.client.force_authenticate(user=self.customer_user)
        original_updated_at = self.review.updated_at

        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertGreater(self.review.updated_at, original_updated_at)


class UpdateReviewUnhappyPathTests(APITestCase):
    """Tests for updating reviews - unhappy paths."""

    def setUp(self):
        """Set up test data for update review unhappy path tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user1 = User.objects.create_user(
            username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user1, type='customer')

        self.customer_user2 = User.objects.create_user(
            username='customer2', password='testpass123')
        Profile.objects.create(user=self.customer_user2, type='customer')

        self.review = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user,
            rating=4,
            description="Test Bewertung"
        )

    def test_update_review_without_authentication(self):
        """Test that unauthenticated users receive 401."""
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_as_different_customer(self):
        """Test that other customers cannot update the review."""
        self.client.force_authenticate(user=self.customer_user2)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_as_business_user(self):
        """Test that business users cannot update the review."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_review(self):
        """Test that updating nonexistent review returns 404."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': 99999})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_review_with_invalid_rating(self):
        """Test that updating with invalid rating returns 400."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {'rating': 10}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_business_user_field(self):
        """Test that business_user field cannot be updated."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {
            'business_user': self.business_user.id,
            'rating': 5
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_reviewer_field(self):
        """Test that reviewer field cannot be updated."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        data = {
            'reviewer': self.customer_user2.id,
            'rating': 5
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteReviewHappyPathTests(APITestCase):
    """Tests for deleting reviews - happy paths."""

    def setUp(self):
        """Set up test data for delete review tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description="Test Bewertung"
        )

    def test_delete_review_as_creator(self):
        """Test that creator can delete own review."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_review_returns_no_content(self):
        """Test that successful deletion returns empty body."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')


class DeleteReviewUnhappyPathTests(APITestCase):
    """Tests for deleting reviews - unhappy paths."""

    def setUp(self):
        """Set up test data for delete review unhappy path tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user1 = User.objects.create_user(
            username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user1, type='customer')

        self.customer_user2 = User.objects.create_user(
            username='customer2', password='testpass123')
        Profile.objects.create(user=self.customer_user2, type='customer')

        self.review = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user,
            rating=4,
            description="Test Bewertung"
        )

    def test_delete_review_without_authentication(self):
        """Test that unauthenticated users receive 401."""
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 1)

    def test_delete_review_as_different_customer(self):
        """Test that other customers cannot delete the review."""
        self.client.force_authenticate(user=self.customer_user2)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_delete_review_as_business_user(self):
        """Test that business users cannot delete the review."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_delete_nonexistent_review(self):
        """Test that deleting nonexistent review returns 404."""
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReviewPermissionsTests(APITestCase):
    """Tests for review permission classes."""

    def setUp(self):
        """Set up test data for permission tests."""
        self.business_user = User.objects.create_user(
            username='business', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.user_without_profile = User.objects.create_user(
            username='noprofile', password='testpass123')

    def test_is_customer_permission_allows_customer(self):
        """Test that IsCustomer permission allows customers."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_is_customer_permission_denies_business_user(self):
        """Test that IsCustomer permission denies business users."""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-list')
        data = {
            'business_user': self.customer_user.id,
            'rating': 5,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_customer_permission_denies_user_without_profile(self):
        """Test that IsCustomer permission denies users without profile."""
        self.client.force_authenticate(user=self.user_without_profile)
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Test'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_reviewer_permission_allows_creator(self):
        """Test that IsReviewer permission allows creator."""
        review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description="Test"
        )
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-detail', kwargs={'pk': review.pk})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_is_reviewer_permission_denies_non_creator(self):
        """Test that IsReviewer permission denies non-creators."""
        customer_user2 = User.objects.create_user(
            username='customer2', password='testpass123')
        Profile.objects.create(user=customer_user2, type='customer')

        review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description="Test"
        )
        self.client.force_authenticate(user=customer_user2)
        url = reverse('reviews-detail', kwargs={'pk': review.pk})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReviewModelTests(APITestCase):
    """Tests for the Review model."""

    def test_review_str_representation(self):
        """Test that Review __str__ returns formatted string."""
        business_user = User.objects.create_user(
            username='business', password='test')
        customer_user = User.objects.create_user(
            username='customer', password='test')

        review = Review.objects.create(
            reviewer=customer_user,
            business_user=business_user,
            rating=5,
            description="Excellent service"
        )

        expected_str = f'Review by customer for business - Rating: 5'
        self.assertEqual(str(review), expected_str)

    def test_review_timestamps_on_creation(self):
        """Test that Review has created_at and updated_at on creation."""
        business_user = User.objects.create_user(
            username='business', password='test')
        customer_user = User.objects.create_user(
            username='customer', password='test')

        review = Review.objects.create(
            reviewer=customer_user,
            business_user=business_user,
            rating=4,
            description="Good"
        )

        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)
        time_diff = abs((review.updated_at - review.created_at).total_seconds())
        self.assertLess(time_diff, 1)
