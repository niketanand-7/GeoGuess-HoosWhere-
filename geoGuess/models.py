from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from geopy.distance import geodesic
import math

class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # Link to the user who created the challenge
    image = models.ImageField(upload_to='challenges/')          # Store the uploaded image
    longitude = models.FloatField()
    latitude = models.FloatField()                              # Store the answer coordinates
    timestamp = models.DateTimeField(auto_now_add=True)         # Automatically set when the challenge is created
    approve_status = models.BooleanField(default=False)         # whether or not challenge has been approved 
    approval_feedback = models.TextField(default="")            # the feedback given by admin if challenge was denied

    def __str__(self):
        return f"Challenge {self.pk} by {self.user.username}"

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"

class DailyChallenge(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)  # Links to the challenge
    timestamp = models.DateTimeField(auto_now_add=True)                 # Automatically set when the daily challenge is created 
    def __str__(self):
        return f"Daily Challenge {self.pk} from {self.timestamp}"

    def get_leaderboard(self):
        # Retrieve all guesses for the associated challenge, ordered by score descending
        guesses = Guess.objects.filter(challenge=self.challenge).order_by('-score')
        leaderboard = [
            {'username': guess.user.username, 'score': guess.score}
            for guess in guesses
        ]
        return leaderboard




class Guess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, validators=[MinValueValidator(limit_value=0, message='Score must be greater than or equal to 0')])                # Store the score / 1000 Automatically Calculated        
    distanceFromAnswer = models.FloatField(default=0, validators=[MinValueValidator(limit_value=0.0, message='Distance must be greater than or equal to 0')])# Store in meters, Automatically Calculated
    longitude = models.FloatField(default=0)                            # Store the guessed coordinates
    latitude = models.FloatField(default=0)                             # Store the  coordinates

    def __str__(self):
        return f"Guess {self.pk} by {self.user.username}"

# Functions to automatically calculate score and distance when a guess is saved
@receiver(pre_save, sender=Guess)
def calculate_distance_score(sender, instance, **kwargs):
    distance = get_distance(instance.latitude, instance.longitude, instance.challenge.latitude, instance.challenge.longitude)
    instance.score = calculate_score(distance)
    instance.distanceFromAnswer = distance
    
pre_save.connect(calculate_distance_score, sender=Guess)

# Uses geopy to get the distance between two coordinates in METERS
def get_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters

# Calculates the score / 1000 based on the distance from the correct answer in METERS
def calculate_score(distance):
    max_score = 1000
    max_score_range = 10
    dropoff_rate = 400

    # Max score is 1000, will give the max score if within 10 meters
    return min(int(max_score * math.exp(-(distance - max_score_range) / dropoff_rate)), max_score)