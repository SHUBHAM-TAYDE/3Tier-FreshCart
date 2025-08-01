# FreshCart/orders/tests.py
# Example tests for the orders app.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category
from cart.models import Cart, CartItem
from .models import Order, OrderItem

User = get_user_model()

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.product1 = Product.objects.create(category=self.category, name='Apple', slug='apple', price=100.00, stock=10, available=True)
        self.product2 = Product.objects.create(category=self.category, name='Orange', slug='orange', price=50.00, stock=20, available=True)

        self.order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=False
        )
        OrderItem.objects.create(order=self.order, product=self.product1, price=self.product1.price, quantity=2) # 200
        OrderItem.objects.create(order=self.order, product=self.product2, price=self.product2.price, quantity=3) # 150

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.first_name, 'John')
        self.assertFalse(self.order.paid)

    def test_order_item_creation(self):
        self.assertEqual(self.order.items.count(), 2)
        item1 = self.order.items.get(product=self.product1)
        self.assertEqual(item1.quantity, 2)
        self.assertEqual(item1.price, 100.00)
        self.assertEqual(item1.get_cost(), 200.00)

    def test_order_get_total_cost(self):
        self.assertEqual(self.order.get_total_cost(), 350.00)

    def test_order_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.id}')

class OrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.product1 = Product.objects.create(category=self.category, name='Apple', slug='apple', price=100.00, stock=10, available=True)
        self.product2 = Product.objects.create(category=self.category, name='Orange', slug='orange', price=50.00, stock=20, available=True)

        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)

        self.order_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'address': '456 Oak Ave',
            'postal_code': '54321',
            'city': 'Anotherville',
        }

    def test_order_create_view_get(self):
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_create.html')
        self.assertIn('form', response.context)
        self.assertIn('cart', response.context)
        self.assertEqual(response.context['cart'], self.cart)

    def test_order_create_view_post_success(self):
        initial_stock_p1 = self.product1.stock
        initial_stock_p2 = self.product2.stock

        response = self.client.post(reverse('orders:order_create'), self.order_data)
        self.assertEqual(response.status_code, 302) # Redirect to payments
        self.assertTrue(Order.objects.filter(user=self.user, first_name='Jane').exists())

        order = Order.objects.get(user=self.user, first_name='Jane')
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.get_total_cost(), 2 * 100 + 1 * 50) # 250

        # Check if cart is cleared
        self.assertEqual(self.cart.items.count(), 0)

        # Check if product stock is reduced
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, initial_stock_p1 - 2)
        self.assertEqual(self.product2.stock, initial_stock_p2 - 1)

    def test_order_create_view_post_empty_cart(self):
        self.cart.items.all().delete() # Empty the cart
        response = self.client.post(reverse('orders:order_create'), self.order_data)
        self.assertEqual(response.status_code, 302) # Redirects to cart detail
        self.assertFalse(Order.objects.filter(user=self.user, first_name='Jane').exists()) # No order created
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Your cart is empty. Please add items before checking out.")

    def test_order_history_view(self):
        # Create a paid order
        Order.objects.create(
            user=self.user, first_name='Paid', last_name='Order', email='paid@example.com',
            address='1 Paid St', postal_code='11111', city='PaidCity', paid=True
        )
        # Create an unpaid order
        Order.objects.create(
            user=self.user, first_name='Unpaid', last_name='Order', email='unpaid@example.com',
            address='2 Unpaid St', postal_code='22222', city='UnpaidCity', paid=False
        )

        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_history.html')
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 2)
        self.assertContains(response, 'Paid Order')
        self.assertContains(response, 'Unpaid Order')

    def test_order_history_view_no_orders(self):
        Order.objects.filter(user=self.user).delete() # Ensure no orders for this user
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have no past orders.')
