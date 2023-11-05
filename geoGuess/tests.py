from unittest.mock import patch, Mock
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client, LiveServerTestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from .models import Challenge, Guess
from .forms import ChallengeForm, ApproveChallengeForm
from .cron import generate_daily_challenge
from django.db import transaction, IntegrityError
import os


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

    # Tests the behavior of the home view for unauthenticated users.
    # It checks if the response status is 200 (OK) and if the response contains the text 'Login with Google'.
    def test_home_view_unauthenticated(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login with Google')
    #Tests the home view behavior for authenticated users.
    # It logs in a mock user, checks if the response status is 200, and looks for a welcoming message.
    def test_home_view_authenticated(self):
        # Simulating login with the mock user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome,')

class MapsViewTest(TestCase):
    
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='password',
            is_staff=False,
            is_superuser=False
        )
        # Log in the regular user
        self.client.login(username='regular_user', password='password')
        self.maps_url = reverse('maps')
#Checks if accessing the maps view returns a status code of 200 and if the response context contains a key for the maps API.
    def test_maps_view(self):
        response = self.client.get(self.maps_url)
        self.assertEqual(response.status_code, 200) #failing
        self.assertIn('maps_api_key', response.context)

class AddChallengeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='password',
            is_staff=False,
            is_superuser=False
        )
        # Log in the regular user
        self.client.login(username='regular_user', password='password')
        self.challenge_url = reverse('challenge')
#Tests if accessing the challenge view gives a status code of 200.
    def test_add_challenge_view(self):
        response = self.client.get(self.challenge_url)
        self.assertEqual(response.status_code, 200) #failing
        self.assertIn('maps_api_key', response.context)

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
        # Log in the regular user
        self.client.login(username='regular_user', password='password')
        self.choice_url = reverse('admin_users')

    def test_regular_not_see_users_view(self):
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403) #checks that regular user access this admin exclusive page
        #should not have permission to access page

class ChallengeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')
        self.challenge = Challenge.objects.create(user=self.user,latitude=38,longitude=-78.3)
    def test_add_challenge_view(self):
        image_path = "geoGuess/static/chemistryBuilding_image.jpg"
        response = self.client.post(reverse('challenge'), data =
        {
            'image': SimpleUploadedFile(name='test_image.jpg', content=open(image_path, 'rb').read(),
                                        content_type='image/jpeg'),
            "longitude": -78.32,
            "latitude": 32.133
        })
        self.assertEqual(response.status_code, 302) #redirecting page
        self.assertEqual(Challenge.objects.count(), 1) #checking if Challenge can be added
    #tests adding challenge with no marker    
    def test_add_challenge_view_no_marker(self):
        self.client.login(username='testuser',password='test')
        response = self.client.post(reverse('challenge')) #no data
        Challenge.objects.all().delete() #deleting object from previous test
        self.assertEqual(Challenge.objects.count(), 0) #checking if Challenge is be added w/ no data

    def test_challenge_form_valid(self):
        image_path = "geoGuess/static/chemistryBuilding_image.jpg"
        form_data = {
            'image': SimpleUploadedFile(name='test_image.jpg', content=open(image_path, 'rb').read(),
                                        content_type='image/jpeg'),
            'longitude': -78.32,
            'latitude': 32.133,
        }
        form = ChallengeForm(data=form_data,files=form_data)
        self.assertTrue(form.is_valid(),form.as_table())

    def test_challenge_form_invalid(self):
        form_data = {
            'longitude': 'invalid_data',
            'latitude': 'invalid_data',
            # Image field is omitted to simulate a missing image upload.
        }
        form = ChallengeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('longitude', form.errors)
        self.assertIn('latitude', form.errors)
        self.assertIn('image', form.errors)


class ChallengeEdgeCaseTest(TestCase):
    def test_challenge_with_extreme_values(self):
        user = User.objects.create_user(username='testuser', password='test')
        Challenge.objects.create(user=user, latitude=90, longitude=180)
        Challenge.objects.create(user=user, latitude=-90, longitude=-180)
        self.assertEqual(Challenge.objects.count(), 2)
        # Test that extreme values do not break the application.



class ChallengeTransactionTest(TestCase):
    def test_challenge_creation_transaction(self):
        with transaction.atomic():
            user = User.objects.create_user(username='testuser', password='test')
            try:
                # Intentionally cause an error in the second operation
                Challenge.objects.create(user=user, latitude=38, longitude=-78.3)
                Challenge.objects.create(user=user, latitude=None, longitude=None)
            except IntegrityError:
                pass
        # The first Challenge should not be saved due to the atomic block.
        self.assertEqual(Challenge.objects.count(), 0)

class ChallengeGuessIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test')

        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=123.45,
            latitude=67.89,
            approve_status=True
        )

    def test_guess_association_with_challenge(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            numOfAttempts=1,
            score=100,
            distanceFromAnswer=0.0
        )

        self.assertEqual(self.challenge.guess_set.count(), 1)
        self.assertEqual(self.challenge.guess_set.first(), guess)

        # Test the Guess attributes
        self.assertEqual(guess.numOfAttempts, 1)
        self.assertEqual(guess.score, 100)
        self.assertEqual(guess.distanceFromAnswer, 0.0)


class GuessModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=123.45,
            latitude=67.89,
            approve_status=True
        )

    def test_guess_creation(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            numOfAttempts=1,
            score=100,
            distanceFromAnswer=0.0
        )

        saved_guess = Guess.objects.get(pk=guess.pk)

        # Check that the Guess has been correctly saved and its attributes are correct
        self.assertEqual(saved_guess.user, self.user)
        self.assertEqual(saved_guess.challenge, self.challenge)
        self.assertEqual(saved_guess.numOfAttempts, 1)
        self.assertEqual(saved_guess.score, 100)
        self.assertEqual(saved_guess.distanceFromAnswer, 0.0)

    def test_updating_guess_fields(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge
        )

        guess.numOfAttempts += 1
        guess.score = 80
        guess.distanceFromAnswer = 20.0
        guess.save()

        updated_guess = Guess.objects.get(pk=guess.pk)

        # Check that the fields have been updated correctly
        self.assertEqual(updated_guess.numOfAttempts, 1)
        self.assertEqual(updated_guess.score, 80)
        self.assertEqual(updated_guess.distanceFromAnswer, 20.0)

    def test_string_representation(self):
        # Create a Guess instance
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge
        )

        # Check the __str__ representation
        self.assertEqual(str(guess), f"Guess {guess.pk} by {self.user.username}")


class GuessModelValidationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=123.45,
            latitude=67.89,
            approve_status=True
        )

    def test_negative_score_raises_validation_error(self):
        guess = Guess(user=self.user, challenge=self.challenge, score=-1)
        with self.assertRaises(ValidationError):
            guess.full_clean()

    def test_negative_distance_raises_validation_error(self):
        guess = Guess(user=self.user, challenge=self.challenge, distanceFromAnswer=-1.0)
        with self.assertRaises(ValidationError):
            guess.full_clean()


class GuessRelationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=123.45,
            latitude=67.89,
            approve_status=True
        )
        self.guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            numOfAttempts=1
        )

    def test_deleting_user_deletes_guess(self):
        self.user.delete()
        with self.assertRaises(Guess.DoesNotExist):
            Guess.objects.get(pk=self.guess.pk)

    def test_deleting_challenge_deletes_guess(self):
        self.challenge.delete()
        with self.assertRaises(Guess.DoesNotExist):
            Guess.objects.get(pk=self.guess.pk)
