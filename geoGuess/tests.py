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
        self.init_login_mock(GoogleOAuth2Adapter)  # Mocks Google OAuth for testing
        app = SocialApp.objects.create(provider='google', name='google', client_id='123', secret='dummy')
        app.sites.add(1)  # Assuming you're using the default site (change if necessary)


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
        self.login(self.user)
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

# class AdminAuthTest(TestCase):
#     def setUp(self):
#         self.admin_user = User.objects.create_user(
#             username='admin_test',
#             password='password123',
#             is_staff=True,  # Grant staff privileges
#             is_superuser=True  # Grant superuser privileges
#         )
#         # Log in the admin user
#         self.client.login(username='admin_test', password='password123')

#     def admin_see_users_view():

