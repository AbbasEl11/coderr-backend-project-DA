"""
Tests for order management functionality.
"""
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from offer_app.models import Offer, OfferDetail
from profile_app.models import Profile
from order_app.models import Order
from rest_framework import status


class OrderAPIHappyPathTests(APITestCase):
    """Tests for successful order API operations - happy paths."""

    def setUp(self):
        """Set up test data for happy path tests."""
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.customer, type='customer')

        self.business = User.objects.create_user(
            username='business1',
            email='business@test.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.business, type='business')

        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True
        )

        self.offer = Offer.objects.create(
            user=self.business,
            title='Test Offer',
            description='Test Description'
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Package',
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=['Feature 1', 'Feature 2'],
            offer_type='basic'
        )

        self.order = Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            status='in_progress'
        )

    def test_get_orders_list_as_customer(self):
        """Test that customer can view their orders."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)
        self.assertEqual(response.data[0]['customer_user'], self.customer.id)

    def test_get_orders_list_as_business(self):
        """Test that business user can view their orders."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['business_user'], self.business.id)

    def test_create_order_as_customer(self):
        """Test that customer can create an order."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-list')
        data = {
            'offer_detail_id': self.offer_detail.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('price', response.data)

    def test_update_order_status_to_completed_as_business(self):
        """Test that business user can update order status to completed."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIn('updated_at', response.data)

    def test_update_order_status_to_canceled_as_business(self):
        """Test that business user can update order status to canceled."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        data = {'status': 'canceled'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'canceled')

    def test_delete_order_as_admin(self):
        """Test that admin can delete an order."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_get_order_count_for_business_user(self):
        """Test that getting order count for business user returns correct count."""
        Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            status='in_progress'
        )
        Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            status='completed'
        )

        self.client.force_authenticate(user=self.customer)
        url = reverse('order-count-details', kwargs={'pk': self.business.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 2)

    def test_get_completed_order_count_for_business_user(self):
        """Test that getting completed order count for business user returns correct count."""
        Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            status='completed'
        )
        Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            status='completed'
        )

        self.client.force_authenticate(user=self.customer)
        url = reverse('completed-order-count-details', kwargs={'pk': self.business.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 2)


class OrderAPIUnhappyPathTests(APITestCase):
    """Tests for failed order API operations - unhappy paths."""

    def setUp(self):
        """Set up test data for unhappy path tests."""
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@test.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.customer, type='customer')

        self.business = User.objects.create_user(
            username='business1',
            email='business@test.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.business, type='business')

        self.other_business = User.objects.create_user(
            username='business2',
            email='business2@test.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.other_business, type='business')

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='testpass123'
        )

        self.offer = Offer.objects.create(
            user=self.business,
            title='Test Offer',
            description='Test Description'
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Package',
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=['Feature 1', 'Feature 2'],
            offer_type='basic'
        )

        self.order = Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            status='in_progress'
        )

    def test_get_orders_list_unauthenticated(self):
        """Test that unauthenticated access is denied."""
        url = reverse('orders-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_unauthenticated(self):
        """Test that unauthenticated user cannot create order."""
        url = reverse('orders-list')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_as_business_user(self):
        """Test that business user cannot create order."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-list')
        data = {'offer_detail_id': self.offer_detail.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_with_invalid_offer_detail_id(self):
        """Test that creating order with invalid offer_detail_id fails."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-list')
        data = {'offer_detail_id': ''}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_missing_offer_detail_id(self):
        """Test that creating order without offer_detail_id fails."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-list')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_nonexistent_offer_detail(self):
        """Test that creating order with nonexistent offer detail returns 404."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-list')
        data = {'offer_detail_id': 99999}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_status_as_customer(self):
        """Test that customer cannot update order status."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_status_unauthenticated(self):
        """Test that unauthenticated user cannot update order status."""
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_with_invalid_status(self):
        """Test that updating order with invalid status fails."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        data = {'status': 'invalid_status'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_order(self):
        """Test that updating nonexistent order returns 404."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-detail', kwargs={'pk': 99999})
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_as_customer(self):
        """Test that customer cannot delete order."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_as_business(self):
        """Test that business user cannot delete order."""
        self.client.force_authenticate(user=self.business)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_unauthenticated(self):
        """Test that unauthenticated user cannot delete order."""
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_order(self):
        """Test that deleting nonexistent order returns 404."""
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=admin)
        url = reverse('orders-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_count_unauthenticated(self):
        """Test that getting order count requires authentication."""
        url = reverse('order-count-details', kwargs={'pk': self.business.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_count_for_nonexistent_user(self):
        """Test that getting order count for nonexistent user returns 404."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-count-details', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_count_for_customer_user(self):
        """Test that getting order count for customer user returns 404."""
        self.client.force_authenticate(user=self.business)
        url = reverse('order-count-details', kwargs={'pk': self.customer.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_completed_order_count_unauthenticated(self):
        """Test that getting completed order count requires authentication."""
        url = reverse('completed-order-count-details', kwargs={'pk': self.business.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_completed_order_count_for_nonexistent_user(self):
        """Test that getting completed order count for nonexistent user returns 404."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('completed-order-count-details', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_completed_order_count_for_customer_user(self):
        """Test that getting completed order count for customer user returns 404."""
        self.client.force_authenticate(user=self.business)
        url = reverse('completed-order-count-details', kwargs={'pk': self.customer.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
