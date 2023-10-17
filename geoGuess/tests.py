from django.test import TestCase
from django.test import Client
from django.urls import reverse
# Create your tests here.
class HomeTestCases(TestCase):
    def test_google_login_redirect(self):
        c = Client()
        google_oauth_url = reverse('Home')
        response = c.get(google_oauth_url)
        assert response.status_code == 302

