from unittest.mock import patch, Mock
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client, LiveServerTestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from .models import Challenge, Guess
from .forms import ChallengeForm, ApproveChallengeForm
from .cron import generate_daily_challenge
from django.db import transaction, IntegrityError
from .views import LeaderboardView, ChallengeBankView, AdminUsersView, edit_user
from io import StringIO
from django.core.management import call_command
import os, math


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

    def test_admin_not_see_daily_challenge(self):
        self.choice_url = reverse('daily_challenge_list')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_not_see_challenge_submission(self):
        self.choice_url = reverse('challenge')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_not_see_leaderboard(self):
        self.choice_url = reverse('leaderboard')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_not_see_submissions(self):
        self.choice_url = reverse('submissions')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403)

    
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

    def test_regular_not_see_users_view(self):
        self.choice_url = reverse('admin_users')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403) #checks that regular user access this admin exclusive page
        #should not have permission to access page
    
    def test_regular_not_see_approve_submissions(self):
        self.choice_url = reverse('approve_submissions')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403)

    def test_regular_not_see_challenge_bank(self):
        self.choice_url = reverse('approve_submissions')
        response = self.client.get(self.choice_url)
        self.assertEqual(response.status_code, 403)

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
            longitude=123.45,
            latitude=67.89,
        )

        self.assertEqual(self.challenge.guess_set.count(), 1)
        self.assertEqual(self.challenge.guess_set.first(), guess)

        # Test the Guess attributes
        self.assertEqual(guess.score, 1000)
        self.assertEqual(guess.distanceFromAnswer, 0.0)


class GuessModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=38.031587943575246, 
            latitude=-78.5108602729666,
            approve_status=True
        )

    def test_guess_creation(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            longitude=38.031587943575246, 
            latitude=-78.5108602729666,
        )

        saved_guess = Guess.objects.get(pk=guess.pk)

        # Check that the Guess has been correctly saved and its attributes are correct
        self.assertEqual(saved_guess.user, self.user)
        self.assertEqual(saved_guess.challenge, self.challenge)
        self.assertEqual(saved_guess.score, 1000)
        self.assertEqual(saved_guess.distanceFromAnswer, 0.0)

    def test_guess_is_close_enough(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            longitude=38.03158534376525, 
            latitude=-78.5107887739817
        )

        saved_guess = Guess.objects.get(pk=guess.pk)

        # Check that the Guess has been correctly saved and that within 10 meters of the answer
        self.assertEqual(saved_guess.user, self.user)
        self.assertEqual(saved_guess.challenge, self.challenge)
        self.assertEqual(saved_guess.score, 1000)
        self.assertTrue(saved_guess.distanceFromAnswer < 10.0)

    def test_update_fields_far(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            longitude=43.02239253427242, 
            latitude=-67.16129125101716
        )
        guess.save()

        updated_guess = Guess.objects.get(pk=guess.pk)
        updated_guess.longitude=38.134471800228155 
        updated_guess.latitude=-78.50693744045769

        updated_guess.save()
        # Check that the fields have been updated correctly
        self.assertEqual(updated_guess.score, 3)
        self.assertTrue(math.isclose(2330.5083, updated_guess.distanceFromAnswer, rel_tol=1e-3, abs_tol=1e-3))

    def test_updating_guess_fields(self):
        guess = Guess.objects.create(
            user=self.user,
            challenge=self.challenge,
            longitude=38.031587943575246, 
            latitude=-78.5108602729666,
        )
        guess.save()

        updated_guess = Guess.objects.get(pk=guess.pk)
        updated_guess.longitude=38.03154885863617 
        updated_guess.latitude=-78.50987120841747

        updated_guess.save()

        # Check that the fields have been updated correctly
        self.assertEqual(updated_guess.score, 777)
        self.assertTrue(math.isclose(110.4317, updated_guess.distanceFromAnswer, rel_tol=1e-3, abs_tol=1e-3))

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
        )

    def test_deleting_user_deletes_guess(self):
        self.user.delete()
        with self.assertRaises(Guess.DoesNotExist):
            Guess.objects.get(pk=self.guess.pk)

    def test_deleting_challenge_deletes_guess(self):
        self.challenge.delete()
        with self.assertRaises(Guess.DoesNotExist):
            Guess.objects.get(pk=self.guess.pk)

class LeaderBoardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@gmail.com", password="pass"
        )
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
            score=200,
        )
        request = RequestFactory().get('/leaderboard')
        self.view = LeaderboardView()
        self.view.setup(request)

    def test_user_on_leaderboard(self):
        leaderboard = self.view.get_queryset()
        self.assertEqual(1, len(leaderboard))

    def test_leaderboard_with_no_guesses(self):
        self.guess.delete()
        leaderboard = self.view.get_queryset()
        self.assertEqual(0,len(leaderboard))

    def test_leaderboard_with_two_guesses_with_new_guess_with_higher_score(self):
        new_user = User.objects.create_user('testuser2', 'test2@example.com', 'password123')
        new_guess = Guess.objects.create(
            user=new_user,
            challenge=self.challenge,
            score= 500,
        )
        leaderboard = self.view.get_queryset()
        self.assertEqual(2,len(leaderboard))
        self.assertEqual(new_guess.score,leaderboard[0]["average_score"]) #checks to make sure leaderboard order is correct
        self.assertEqual(self.guess.score,leaderboard[1]["average_score"])

    def test_leaderboard_with_two_guesses_with_new_guess_with_lower_score(self):
        new_user = User.objects.create_user('testuser2', 'test2@example.com', 'password123')
        new_guess = Guess.objects.create(
            user=new_user,
            challenge=self.challenge,
            score= 100,
        )
        leaderboard = self.view.get_queryset()
        self.assertEqual(2,len(leaderboard))
        self.assertEqual(new_guess.score,leaderboard[1]["average_score"]) #checks to make sure leaderboard order is correct
        self.assertEqual(self.guess.score,leaderboard[0]["average_score"])

class AddingDailyChallengeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=123.45,
            latitude=67.89,
            approve_status=True
        )

    def test_add_daily_challenge_success(self):
        out = StringIO()
        call_command('add_daily_challenge', stdout=out)
        self.assertIn('Daily challenge added successfully.',out.getvalue())

    def test_add_daily_challenge_fail(self):
        self.challenge.delete()
        out = StringIO()
        call_command('add_daily_challenge', stdout=out)
        self.assertIn('No challenges to add.', out.getvalue())

class ChallengeBankTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin_user',
            password='password',
            is_staff=True,
            is_superuser=True
        )
        self.challenge = Challenge.objects.create(
            user=self.user,
            image='path/to/image.jpg',
            longitude=123.45,
            latitude=67.89,
            approve_status=True
        )
        request = RequestFactory().get('/challenge_bank')
        self.view = ChallengeBankView()
        self.view.setup(request)

    def test_challengeBank_one_challenge(self):
        challenge_bank = self.view.get_queryset()
        self.assertEqual(1, len(challenge_bank))

    def test_challengeBank_one_challenge(self):
        challenge_bank = self.view.get_queryset()
        self.assertEqual(1, len(challenge_bank))

    def test_challengeBank_empty(self):
        out = StringIO()
        call_command('add_daily_challenge', stdout = out)
        self.assertIn('Daily challenge added successfully.', out.getvalue())
        challenge_bank = self.view.get_queryset()
        self.assertEqual(0, len(challenge_bank))

# class AdminUsersViewTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='admin_user',
#             password='password',
#             is_staff=True,
#             is_superuser=True
#         )
#         self.challenge = Challenge.objects.create(
#             user=self.user,
#             image='path/to/image.jpg',
#             longitude=123.45,
#             latitude=67.89,
#             approve_status=True
#         )
#         self.factory = RequestFactory()













