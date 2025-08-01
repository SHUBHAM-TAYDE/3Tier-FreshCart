# FreshCart/cart/tests.py
# Example tests for the cart app.

from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category
from django.contrib.auth import get_user_model
from .models import Cart, CartItem

User = get_user_model()

class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.product1 = Product.objects.create(category=self.category, name='Apple', slug='apple', price=100.00, stock=10, available=True)
        self.product2 = Product.objects.create(category=self.category, name='Orange', slug='orange', price=50.00, stock=20, available=True)

    def test_cart_creation_for_user(self):
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertIsNone(cart.session_key)

    def test_cart_creation_for_anonymous_user(self):
        cart = Cart.objects.create(session_key='testsessionkey123')
        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, 'testsessionkey123')

    def test_cart_item_creation(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        self.assertEqual(cart_item.cart, cart)
        self.assertEqual(cart_item.product, self.product1)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.get_cost(), 200.00)

    def test_cart_get_total_price(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2) # 200
        CartItem.objects.create(cart=cart, product=self.product2, quantity=3) # 150
        self.assertEqual(cart.get_total_price(), 350.00)

class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.product1 = Product.objects.create(category=self.category, name='Apple', slug='apple', price=100.00, stock=10, available=True)
        self.product2 = Product.objects.create(category=self.category, name='Orange', slug='orange', price=50.00, stock=20, available=True)

    def test_add_to_cart_anonymous(self):
        response = self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1})
        self.assertEqual(response.status_code, 302) # Redirects to cart detail
        self.assertTrue(Cart.objects.exists())
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product, self.product1)
        self.assertEqual(cart.items.first().quantity, 1)

    def test_add_to_cart_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product, self.product1)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_add_to_cart_existing_item(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1})
        self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1}) # Add again
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1) # Still one item
        self.assertEqual(cart.items.first().quantity, 2) # Quantity updated

    def test_cart_detail_view_anonymous(self):
        self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1})
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertContains(response, '₹100.00')
        self.assertTemplateUsed(response, 'cart/cart_detail.html')

    def test_cart_detail_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1})
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertContains(response, '₹100.00')
        self.assertTemplateUsed(response, 'cart/cart_detail.html')

    def test_remove_from_cart(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1})
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)

        response = self.client.post(reverse('cart:remove_from_cart', args=[self.product1.id]))
        self.assertEqual(response.status_code, 302) # Redirects
        cart.refresh_from_db() # Refresh cart instance
        self.assertEqual(cart.items.count(), 0)

    def test_add_to_cart_not_enough_stock(self):
        self.product1.stock = 0
        self.product1.save()
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('cart:add_to_cart', args=[self.product1.id]), {'quantity': 1})
        self.assertEqual(response.status_code, 302) # Redirects back to product detail
        self.assertFalse(CartItem.objects.filter(product=self.product1).exists())
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Not enough stock for Apple. Available: 0")


