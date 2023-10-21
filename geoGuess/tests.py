from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from pathlib import Path
# Create your tests here.
class HomeTestCases(TestCase):
    def test_google_login_redirect(self):
        c = Client()
        #google_oauth_url = reverse('Home')
        #response = c.get(google_oauth_url)
        #assert response.status_code == 302

class ChallengeTests(TestCase):
    #checking if challenge page contains necessary static files
    def test_javascript_included(self):
        file_path = finders.find('geoGuess.js')
        self.assertTrue(staticfiles_storage.exists(file_path))
    def test_css_included(self):
        file_path = finders.find('geoGuess.css')
        self.assertTrue(staticfiles_storage.exists(file_path))


