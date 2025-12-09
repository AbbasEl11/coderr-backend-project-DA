from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from offer_app.models import Offer, OfferDetail
from profile_app.models import Profile


# ============================================
# HAPPY PATH TESTS
# ============================================

class ListOffersHappyPathTests(APITestCase):
    """Tests for listing offers - Happy Paths"""

    def setUp(self):
        # Create business user with offers
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        # Create customer user
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        # Create test offers
        self.offer1 = Offer.objects.create(
            user=self.business_user,
            title="Web Development",
            description="Professional web development services"
        )
        OfferDetail.objects.create(
            offer=self.offer1,
            title="Basic Plan",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1", "Feature 2"],
            offer_type="basic"
        )

        self.offer2 = Offer.objects.create(
            user=self.business_user,
            title="Logo Design",
            description="Creative logo design"
        )
        OfferDetail.objects.create(
            offer=self.offer2,
            title="Premium Plan",
            revisions=5,
            delivery_time_in_days=3,
            price=200,
            features=["Feature 1", "Feature 2", "Feature 3"],
            offer_type="premium"
        )

    def test_list_offers_without_authentication(self):
        """Unauthenticated users can list all offers"""
        url = reverse('offers-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_list_offers_with_authentication(self):
        """Authenticated users can list all offers"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_list_offers_with_pagination(self):
        """Offers are properly paginated"""
        url = reverse('offers-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_search_offers_by_title(self):
        """Search offers by title works correctly"""
        url = reverse('offers-list')
        response = self.client.get(url, {'search': 'Web'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)


class RetrieveOfferHappyPathTests(APITestCase):
    """Tests for retrieving single offer - Happy Paths"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Plan",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )

    def test_retrieve_offer_as_authenticated_user(self):
        """Authenticated users can retrieve a specific offer"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.offer.title)
        self.assertEqual(response.data['description'], self.offer.description)
        self.assertIn('details', response.data)

    def test_retrieve_offer_includes_user_info(self):
        """Retrieved offer includes user information"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.data)


class CreateOfferHappyPathTests(APITestCase):
    """Tests for creating offers - Happy Paths"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.offer_data = {
            "title": "New Test Offer",
            "description": "This is a test offer.",
            "details": [
                {
                    "title": "Basic Plan",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 50,
                    "features": ["Feature 1", "Feature 2"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Plan",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100,
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Plan",
                    "revisions": 3,
                    "delivery_time_in_days": 1,
                    "price": 150,
                    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
                    "offer_type": "premium"
                }
            ]
        }

    def test_create_offer_as_business_user(self):
        """Business user can successfully create an offer"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        response = self.client.post(url, self.offer_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], self.offer_data['title'])
        self.assertEqual(response.data['description'],
                         self.offer_data['description'])
        self.assertEqual(len(response.data['details']), 3)

        # Verify offer was created in database
        offer_exists = Offer.objects.filter(
            title=self.offer_data['title']).exists()
        self.assertTrue(offer_exists)

    def test_create_offer_sets_correct_user(self):
        """Created offer is assigned to the authenticated user"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        response = self.client.post(url, self.offer_data, format='json')

        self.assertEqual(response.status_code, 201)
        offer = Offer.objects.get(pk=response.data['id'])
        self.assertEqual(offer.user, self.business_user)

    def test_create_offer_with_all_detail_types(self):
        """Offer can be created with basic, standard, and premium details"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        response = self.client.post(url, self.offer_data, format='json')

        self.assertEqual(response.status_code, 201)
        offer = Offer.objects.get(pk=response.data['id'])
        details = offer.details.all()

        self.assertEqual(details.count(), 3)
        offer_types = [detail.offer_type for detail in details]
        self.assertIn('basic', offer_types)
        self.assertIn('standard', offer_types)
        self.assertIn('premium', offer_types)


class UpdateOfferHappyPathTests(APITestCase):
    """Tests for updating offers - Happy Paths"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Original Title",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Plan",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )

    def test_update_offer_as_owner(self):
        """Offer owner can update their offer"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        updated_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "details": [
                {
                    "title": "Updated Basic Plan",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 120,
                    "features": ["Feature 1", "Feature 2"],
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Updated Title")
        self.assertEqual(response.data['description'], "Updated Description")

    def test_partial_update_offer_as_owner(self):
        """Offer owner can partially update their offer"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        partial_data = {
            "title": "Partially Updated Title"
        }
        response = self.client.patch(url, partial_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Partially Updated Title")
        self.assertEqual(response.data['description'], "Original Description")


class DeleteOfferHappyPathTests(APITestCase):
    """Tests for deleting offers - Happy Paths"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Offer to Delete",
            description="Will be deleted"
        )

    def test_delete_offer_as_owner(self):
        """Offer owner can delete their offer"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

        # Verify offer was deleted
        offer_exists = Offer.objects.filter(pk=self.offer.pk).exists()
        self.assertFalse(offer_exists)


# ============================================
# UNHAPPY PATH TESTS
# ============================================

class ListOffersUnhappyPathTests(APITestCase):
    """Tests for listing offers - Unhappy Paths"""

    def test_list_offers_with_invalid_page(self):
        """Request with invalid page number returns appropriate response"""
        url = reverse('offers-list')
        response = self.client.get(url, {'page': 9999}, format='json')

        self.assertEqual(response.status_code, 404)


class RetrieveOfferUnhappyPathTests(APITestCase):
    """Tests for retrieving single offer - Unhappy Paths"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )

    def test_retrieve_offer_without_authentication(self):
        """Unauthenticated users cannot retrieve a specific offer"""
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 401)

    def test_retrieve_nonexistent_offer(self):
        """Retrieving non-existent offer returns 404"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 404)


class CreateOfferUnhappyPathTests(APITestCase):
    """Tests for creating offers - Unhappy Paths"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.valid_offer_data = {
            "title": "Test Offer",
            "description": "Test Description",
            "details": [
                {
                    "title": "Basic Plan",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 50,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }

    def test_create_offer_without_authentication(self):
        """Unauthenticated users cannot create offers"""
        url = reverse('offers-list')
        response = self.client.post(url, self.valid_offer_data, format='json')

        self.assertEqual(response.status_code, 401)

    def test_create_offer_as_customer_user(self):
        """Customer users cannot create offers (only business users can)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-list')
        response = self.client.post(url, self.valid_offer_data, format='json')

        self.assertEqual(response.status_code, 403)

    def test_create_offer_without_title(self):
        """Creating offer without title fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        invalid_data = self.valid_offer_data.copy()
        del invalid_data['title']
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_create_offer_without_description(self):
        """Creating offer without description fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        invalid_data = self.valid_offer_data.copy()
        del invalid_data['description']
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('description', response.data)

    def test_create_offer_without_details(self):
        """Creating offer without details fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        invalid_data = {
            "title": "Test Offer",
            "description": "Test Description"
        }
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_create_offer_with_invalid_detail_type(self):
        """Creating offer with invalid offer_type fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        invalid_data = self.valid_offer_data.copy()
        invalid_data['details'][0]['offer_type'] = 'invalid_type'
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_create_offer_with_negative_price(self):
        """Creating offer with negative price fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        invalid_data = self.valid_offer_data.copy()
        invalid_data['details'][0]['price'] = -100
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_create_offer_with_negative_delivery_time(self):
        """Creating offer with negative delivery time fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        invalid_data = self.valid_offer_data.copy()
        invalid_data['details'][0]['delivery_time_in_days'] = -5
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)


class UpdateOfferUnhappyPathTests(APITestCase):
    """Tests for updating offers - Unhappy Paths"""

    def setUp(self):
        self.business_user1 = User.objects.create_user(
            username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user1, type='business')

        self.business_user2 = User.objects.create_user(
            username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.offer = Offer.objects.create(
            user=self.business_user1,
            title="Original Title",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Plan",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )

    def test_update_offer_without_authentication(self):
        """Unauthenticated users cannot update offers"""
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        updated_data = {
            "title": "Hacked Title",
            "description": "Hacked Description",
            "details": []
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 401)

    def test_update_offer_as_non_owner(self):
        """Non-owner business user cannot update another user's offer"""
        self.client.force_authenticate(user=self.business_user2)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        updated_data = {
            "title": "Unauthorized Update",
            "description": "Should not work",
            "details": [
                {
                    "title": "Basic Plan",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 403)

    def test_update_offer_as_customer(self):
        """Customer users cannot update offers"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        updated_data = {
            "title": "Customer Update",
            "description": "Should not work",
            "details": []
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_offer(self):
        """Updating non-existent offer returns 404"""
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('offers-detail', kwargs={'pk': 99999})
        updated_data = {
            "title": "New Title",
            "description": "New Description",
            "details": []
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 404)


class DeleteOfferUnhappyPathTests(APITestCase):
    """Tests for deleting offers - Unhappy Paths"""

    def setUp(self):
        self.business_user1 = User.objects.create_user(
            username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user1, type='business')

        self.business_user2 = User.objects.create_user(
            username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.offer = Offer.objects.create(
            user=self.business_user1,
            title="Offer to Delete",
            description="Will be deleted"
        )

    def test_delete_offer_without_authentication(self):
        """Unauthenticated users cannot delete offers"""
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)

        # Verify offer still exists
        offer_exists = Offer.objects.filter(pk=self.offer.pk).exists()
        self.assertTrue(offer_exists)

    def test_delete_offer_as_non_owner(self):
        """Non-owner business user cannot delete another user's offer"""
        self.client.force_authenticate(user=self.business_user2)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)

        # Verify offer still exists
        offer_exists = Offer.objects.filter(pk=self.offer.pk).exists()
        self.assertTrue(offer_exists)

    def test_delete_offer_as_customer(self):
        """Customer users cannot delete offers"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)

        # Verify offer still exists
        offer_exists = Offer.objects.filter(pk=self.offer.pk).exists()
        self.assertTrue(offer_exists)

    def test_delete_nonexistent_offer(self):
        """Deleting non-existent offer returns 404"""
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 404)


class OfferPermissionsTests(APITestCase):
    """Dedicated tests for permission classes"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.user_without_profile = User.objects.create_user(
            username='noprofile', password='testpass123')

    def test_is_business_user_permission_with_business_user(self):
        """IsBusinessUser permission allows business users"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        data = {
            "title": "Test",
            "description": "Test",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 50,
                    "features": ["Feature"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100,
                    "features": ["Feature"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 1,
                    "price": 150,
                    "features": ["Feature"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)

    def test_is_business_user_permission_with_customer_user(self):
        """IsBusinessUser permission denies customer users"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-list')
        data = {
            "title": "Test",
            "description": "Test",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 50,
                    "features": ["Feature"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100,
                    "features": ["Feature"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 1,
                    "price": 150,
                    "features": ["Feature"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 403)

    def test_is_offer_owner_permission_with_owner(self):
        """IsOfferOwner permission allows owner to modify"""
        offer = Offer.objects.create(
            user=self.business_user,
            title="Test",
            description="Test"
        )

        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_is_offer_owner_permission_with_non_owner(self):
        """IsOfferOwner permission denies non-owner"""
        offer = Offer.objects.create(
            user=self.business_user,
            title="Test",
            description="Test"
        )

        other_business = User.objects.create_user(
            username='other', password='testpass123')
        Profile.objects.create(user=other_business, type='business')

        self.client.force_authenticate(user=other_business)
        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)


class OfferDetailViewTests(APITestCase):
    """Tests for OfferDetailView endpoint"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Plan",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1", "Feature 2"],
            offer_type="basic"
        )

    def test_get_offer_detail_as_authenticated_user(self):
        """Authenticated users can retrieve offer detail"""
        self.client.force_authenticate(user=self.customer_user)
        url = f'/api/offerdetails/{self.offer_detail.pk}/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Basic Plan")
        self.assertEqual(response.data['revisions'], 1)
        self.assertEqual(response.data['price'], 100)

    def test_get_offer_detail_without_authentication(self):
        """Unauthenticated users cannot retrieve offer detail"""
        url = f'/api/offerdetails/{self.offer_detail.pk}/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 401)

    def test_get_nonexistent_offer_detail(self):
        """Retrieving non-existent offer detail returns 404"""
        self.client.force_authenticate(user=self.customer_user)
        url = '/api/offerdetails/99999/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 404)


class ModelStringRepresentationTests(APITestCase):
    """Tests for model __str__ methods"""

    def test_offer_str_representation(self):
        """Offer __str__ returns title"""
        user = User.objects.create_user(username='testuser', password='test')
        offer = Offer.objects.create(
            user=user,
            title="Web Development Services",
            description="Professional web dev"
        )
        self.assertEqual(str(offer), "Web Development Services")

    def test_offer_detail_str_representation(self):
        """OfferDetail __str__ returns formatted string"""
        user = User.objects.create_user(username='testuser', password='test')
        offer = Offer.objects.create(
            user=user,
            title="Logo Design",
            description="Creative logos"
        )
        offer_detail = OfferDetail.objects.create(
            offer=offer,
            title="Premium Package",
            revisions=5,
            delivery_time_in_days=3,
            price=200,
            features=["Feature 1"],
            offer_type="premium"
        )
        self.assertEqual(str(offer_detail), "Logo Design - (premium)")


class SerializerValidationTests(APITestCase):
    """Tests for serializer validation and edge cases"""

    def setUp(self):
        self.business_user = User.objects.create_user(
            username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')

    def test_update_offer_with_non_matching_offer_types(self):
        """Updating offer with non-existing offer_type raises error"""
        self.client.force_authenticate(user=self.business_user)

        # Create offer with basic, standard, premium
        offer = Offer.objects.create(
            user=self.business_user,
            title="Original",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature"],
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Standard",
            revisions=2,
            delivery_time_in_days=3,
            price=150,
            features=["Feature"],
            offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Premium",
            revisions=3,
            delivery_time_in_days=1,
            price=200,
            features=["Feature"],
            offer_type="premium"
        )

        # Try to update with a non-matching offer type
        url = reverse('offers-detail', kwargs={'pk': offer.pk})

        # First delete one detail type to create a scenario
        OfferDetail.objects.filter(offer=offer, offer_type='premium').delete()

        # Now try to update the premium type that doesn't exist
        updated_data = {
            "title": "Updated",
            "description": "Updated Description",
            "details": [
                {
                    "title": "Premium Updated",
                    "revisions": 5,
                    "delivery_time_in_days": 1,
                    "price": 250,
                    "features": ["Feature"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_update_offer_detail_without_offer_type(self):
        """Updating offer detail without offer_type raises error"""
        self.client.force_authenticate(user=self.business_user)

        offer = Offer.objects.create(
            user=self.business_user,
            title="Original",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Feature"],
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Standard",
            revisions=2,
            delivery_time_in_days=3,
            price=150,
            features=["Feature"],
            offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Premium",
            revisions=3,
            delivery_time_in_days=1,
            price=200,
            features=["Feature"],
            offer_type="premium"
        )

        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        updated_data = {
            "title": "Updated",
            "description": "Updated Description",
            "details": [
                {
                    "title": "Basic Updated",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 120,
                    "features": ["Feature"]
                    # Missing offer_type
                }
            ]
        }
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_create_offer_with_duplicate_offer_types(self):
        """Creating offer with duplicate offer_types fails"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        data = {
            "title": "Test Offer",
            "description": "Test Description",
            "details": [
                {
                    "title": "Basic 1",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 50,
                    "features": ["Feature"],
                    "offer_type": "basic"
                },
                {
                    "title": "Basic 2",
                    "revisions": 2,
                    "delivery_time_in_days": 3,
                    "price": 100,
                    "features": ["Feature"],
                    "offer_type": "basic"
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 1,
                    "price": 150,
                    "features": ["Feature"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_offer_min_price_method(self):
        """Offer min_price method returns correct value"""
        user = User.objects.create_user(username='testuser', password='test')
        offer = Offer.objects.create(
            user=user,
            title="Test",
            description="Test"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=[],
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Premium",
            revisions=3,
            delivery_time_in_days=1,
            price=300,
            features=[],
            offer_type="premium"
        )

        self.assertEqual(offer.min_price(), 100)

    def test_offer_min_delivery_time_method(self):
        """Offer min_delivery_time method returns correct value"""
        user = User.objects.create_user(username='testuser', password='test')
        offer = Offer.objects.create(
            user=user,
            title="Test",
            description="Test"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=10,
            price=100,
            features=[],
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Premium",
            revisions=3,
            delivery_time_in_days=2,
            price=300,
            features=[],
            offer_type="premium"
        )

        self.assertEqual(offer.min_delivery_time(), 2)
