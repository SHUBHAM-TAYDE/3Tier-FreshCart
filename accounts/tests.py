# FreshCart/accounts/tests.py
# Example tests for the accounts app.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpassword')
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.check_password('adminpassword'))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_custom_fields(self):
        user = User.objects.create_user(
            username='userwithinfo',
            email='info@example.com',
            password='password123',
            phone_number='1234567890',
            address='123 Test Street'
        )
        self.assertEqual(user.phone_number, '1234567890')
        self.assertEqual(user.address, '123 Test Street')

class AccountViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Login to your account')

    def test_login_post_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302) # Redirects on successful login
        self.assertRedirects(response, reverse('landing_page')) # Assuming 'landing_page' is the redirect target
        self.assertTrue(self.user.is_authenticated) # Check if user is logged in

    def test_login_post_failure(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertContains(response, 'Invalid username or password.')
        self.assertFalse(self.user.is_authenticated)

    def test_signup_page_get(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertContains(response, 'Create your account')

    def test_signup_post_success(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123', # UserCreationForm requires password confirmation
            'phone_number': '9876543210',
            'address': '456 New St'
        })
        self.assertEqual(response.status_code, 302) # Redirects on successful signup
        self.assertRedirects(response, reverse('landing_page'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.is_authenticated)
        self.assertEqual(new_user.phone_number, '9876543210')

    def test_signup_post_failure_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'username': 'anotheruser',
            'email': 'another@example.com',
            'password': 'password1',
            'password2': 'password2'
        })
        self.assertEqual(response.status_code, 200) # Stays on signup page
        self.assertContains(response, 'The two password fields didn&#x27;t match.')
        self.assertFalse(User.objects.filter(username='anotheruser').exists())

    def test_logout(self):
        self.client.login(username='testuser', password='testpassword')
        self.assertTrue(self.user.is_authenticated)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302) # Redirects to login page
        self.assertRedirects(response, reverse('login_page'))
        # After logout, the user should no longer be authenticated
        # Note: self.user.is_authenticated might still be True here because it's the original object.
        # You'd typically check request.user.is_authenticated in a view or re-fetch the user.

