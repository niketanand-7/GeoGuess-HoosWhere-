from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.tests import OAuth2TestsMixin

class HomeViewTest(TestCase, OAuth2TestsMixin):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        
        # Create a test user and associated social account
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.init_login_mock(GoogleOAuth2Adapter)  # Mocks Google OAuth for testing
        app = SocialApp.objects.create(provider='google', name='google', client_id='123', secret='dummy')
        app.sites.add(1)  # Assuming you're using the default site (change if necessary)

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
