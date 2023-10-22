from django.test import TestCase
from django.test import Client
from django.urls import reverse
# Create your tests here.

class HomeViewTest(TestCase):
    def test_home_view(self):
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

# class ChoiceViewTest(TestCase):
#     def test_form_submission(self):
#         client = Client()
#         data = {'field_name': 'value', ...}  # Fill with form data
#         response = client.post(reverse('choice_view_name'), data=data)  # Use the correct URL pattern name for Choice_View
#         self.assertEqual(response.status_code, 302)  # Assuming you're redirecting after a successful post

class MapsViewTest(TestCase):
    def test_maps_view(self):
        client = Client()
        response = client.get(reverse('challenge'))  # Use the correct URL pattern name for maps_view
        self.assertEqual(response.status_code, 200)
        self.assertIn('maps_api_key', response.context)
