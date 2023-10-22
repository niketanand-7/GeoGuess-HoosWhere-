from django.test import TestCase, Client
from django.urls import reverse

class HomeViewTest(TestCase):

    def setUp(self):
        # Create a test client instance to simulate requests
        self.client = Client()
        self.home_url = reverse('home')

    def test_home_view_unauthenticated(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login with Google')  # Ensure login button is visible

    def test_home_view_authenticated(self):
        # Here, you'd simulate a user being logged in. 
        # This could be by using the `login` method of the test client or by mocking a user session.
        # The specifics would depend on how `django-allauth` integrates with Django's authentication.
        # This is a placeholder and might need adjustments based on your setup.
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome,')  # Ensure user-specific content is visible

    # This is your existing test case, unchanged
    def test_home_view(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

class MapsViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_maps_view(self):
        response = self.client.get(reverse('challenge'))  # Assuming 'challenge' is the correct URL pattern name for maps_view
        self.assertEqual(response.status_code, 200)
        self.assertIn('maps_api_key', response.context)