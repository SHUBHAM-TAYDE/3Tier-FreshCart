# FreshCart/payments/tests.py
# Example tests for the payments app.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order, OrderItem
from unittest.mock import patch, MagicMock
import json
import stripe # Import stripe to mock its API calls

User = get_user_model()

class PaymentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.product = Product.objects.create(category=self.category, name='Apple', slug='apple', price=100.00, stock=10, available=True)

        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Testville',
            paid=False
        )
        OrderItem.objects.create(order=self.order, product=self.product, price=self.product.price, quantity=1)

    @patch('stripe.PaymentIntent.create')
    def test_process_payment_post_success(self, mock_create):
        mock_payment_intent = MagicMock()
        mock_payment_intent.client_secret = 'pi_test_client_secret'
        mock_payment_intent.id = 'pi_test_id'
        mock_create.return_value = mock_payment_intent

        response = self.client.post(reverse('payments:process_payment', args=[self.order.id]), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['clientSecret'], 'pi_test_client_secret')
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.stripe_id, 'pi_test_id')
        mock_create.assert_called_once_with(
            amount=int(self.order.get_total_cost() * 100),
            currency='inr',
            metadata={'order_id': self.order.id},
        )

    @patch('stripe.PaymentIntent.create')
    def test_process_payment_post_failure(self, mock_create):
        mock_create.side_effect = stripe.error.StripeError("Stripe API error")

        response = self.client.post(reverse('payments:process_payment', args=[self.order.id]), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], 'Stripe API error')

    def test_process_payment_get(self):
        response = self.client.get(reverse('payments:process_payment', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/process_payment.html')
        self.assertIn('order', response.context)
        self.assertIn('stripe_publishable_key', response.context)

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_payment_succeeded(self, mock_construct_event):
        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_succeeded_test',
                    'metadata': {'order_id': self.order.id}
                }
            }
        }
        mock_construct_event.return_value = mock_event

        response = self.client.post(reverse('payments:stripe_webhook'),
                                    json.dumps(mock_event),
                                    content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE='t=123,v1=abc')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertEqual(self.order.stripe_id, 'pi_succeeded_test')

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_payment_failed(self, mock_construct_event):
        mock_event = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': 'pi_failed_test',
                    'metadata': {'order_id': self.order.id}
                }
            }
        }
        mock_construct_event.return_value = mock_event

        response = self.client.post(reverse('payments:stripe_webhook'),
                                    json.dumps(mock_event),
                                    content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE='t=123,v1=abc')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid) # Should remain unpaid

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct_event):
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid signature", 'sig_header')

        response = self.client.post(reverse('payments:stripe_webhook'),
                                    json.dumps({'test': 'data'}),
                                    content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE='invalid_signature')
        self.assertEqual(response.status_code, 400)

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_order_not_found(self, mock_construct_event):
        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_succeeded_test',
                    'metadata': {'order_id': 99999} # Non-existent order ID
                }
            }
        }
        mock_construct_event.return_value = mock_event

        response = self.client.post(reverse('payments:stripe_webhook'),
                                    json.dumps(mock_event),
                                    content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE='t=123,v1=abc')
        self.assertEqual(response.status_code, 404) # Order not found
