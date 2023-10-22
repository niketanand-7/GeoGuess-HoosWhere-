from unittest.mock import patch, Mock
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client

class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        
        # Create a test user and associated social account
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.init_login_mock() 
        app = SocialApp.objects.create(provider='google', name='google', client_id='123', secret='dummy')
       
        from django.contrib.sites.models import Site
        site = Site.objects.create(domain='test.com', name='test.com')
        app.sites.add(site)

    def init_login_mock(self):
        """
        Mock the login process for Google OAuth2Adapter
        """
        mocked_login = Mock()
        mocked_login.access_token = 'mocked_token'

        # Patch the specific methods of GoogleOAuth2Adapter
        patcher1 = patch.object(GoogleOAuth2Adapter, 'complete_login', return_value=mocked_login)
        patcher2 = patch.object(GoogleOAuth2Adapter, 'get_provider', return_value='google-oauth2')

        # Cleanup after the test case execution
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)

        # Start the mock patches
        patcher1.start()
        patcher2.start()


    def test_home_view_unauthenticated(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login with Google')

    def test_home_view_authenticated(self):
        # Simulating login with the mock user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome,')

class MapsViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.maps_url = reverse('challenge')

    def test_maps_view(self):
        response = self.client.get(self.maps_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('maps_api_key', response.context)

class ChoiceViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.choice_url = reverse('choice')

    def test_choice_view(self):
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 200)

class AdminAuthTest(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='password123',
            is_staff=True,  # Grant staff privileges
            is_superuser=True  # Grant superuser privileges
        )
        # Log in the admin user
        self.client.login(username='admin_test', password='password123')
        
    def test_admin_see_users_view(self):
        self.choice_url = reverse('admin_users')
        response = self.client.get(self.choice_url)
        self.assertContains(response, self.admin_user.username) #checks that the usernames are displayed for admin user with higher auth level

    
class RegularUserAuthTest(TestCase):

    def setUp(self):
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='password',
            is_staff=False, 
            is_superuser=False 
        )
        # Log in the regualar user
        self.client.login(username='regular_user', password='password')
        self.choice_url = reverse('admin_users')

    def test_regular_not_see_users_view(self):
        response = self.client.get(self.choice_url)
        self.assertNotContains(response, self.regular_user.username) #checks that regular user can NOT see the other users