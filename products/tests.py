# FreshCart/products/tests.py
# Example tests for the products app.

from django.test import TestCase
from django.urls import reverse
from .models import Category, Product
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Dairy', slug='dairy')
        self.product = Product.objects.create(
            category=self.category,
            name='Milk',
            slug='milk',
            description='Fresh cow milk',
            price=50.00,
            stock=100,
            available=True
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Dairy')
        self.assertEqual(self.category.slug, 'dairy')

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Milk')
        self.assertEqual(self.product.price, 50.00)
        self.assertEqual(self.product.category, self.category)
        self.assertTrue(self.product.available)

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Milk')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Dairy')

class ProductViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.category1 = Category.objects.create(name='Fruits', slug='fruits')
        self.category2 = Category.objects.create(name='Vegetables', slug='vegetables')
        self.product1 = Product.objects.create(
            category=self.category1, name='Apple', slug='apple', price=100.00, stock=10, available=True
        )
        self.product2 = Product.objects.create(
            category=self.category2, name='Carrot', slug='carrot', price=50.00, stock=20, available=True
        )
        self.product3 = Product.objects.create(
            category=self.category1, name='Banana', slug='banana', price=30.00, stock=50, available=False # Not available
        )

    def test_product_list_view(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertContains(response, 'Carrot')
        self.assertNotContains(response, 'Banana') # Should not show unavailable product
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 2) # Only available products

    def test_product_list_by_category_view(self):
        response = self.client.get(reverse('product_list_by_category', args=['fruits']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertNotContains(response, 'Carrot')
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 1) # Only Apple

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=[self.product1.id, self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'], self.product1)

    def test_product_detail_view_unavailable_product(self):
        # Should return 404 for an unavailable product
        response = self.client.get(reverse('product_detail', args=[self.product3.id, self.product3.slug]))
        self.assertEqual(response.status_code, 404)


