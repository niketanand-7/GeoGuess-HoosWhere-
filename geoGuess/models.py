from django.db import models
from django.contrib.auth.models import User

class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # Link to the user who created the challenge
    image = models.ImageField(upload_to='challenges/')          # Store the uploaded image
    longitude = models.FloatField()                             # Store the answer coordinates
    latitude = models.FloatField()                              # Store the answer coordinates
    timestamp = models.DateTimeField(auto_now_add=True)         # Automatically set when the challenge is created
    approve_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Challenge {self.pk} by {self.user.username}"

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"

class DailyChallenge(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)  # Links to the challenge
    timestamp = models.DateTimeField(auto_now_add=True)                 # Automatically set when the daily challenge is created 

    """
    Checks if the user has already guessed the daily challenge

    :param user: The user to check
    :return: True if the user has already guessed the daily challenge, false otherwise
    """
    def hasBeenGuessed(self, user):
        return Guess.objects.filter(user=user, challenge=self.challenge).exists()

    def __str__(self):
        return f"Daily Challenge {self.pk} from {self.timestamp}"

class Guess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    distanceFromAnswer = models.FloatField(default=0)
    
    def __str__(self):
        return f"Guess {self.pk} by {self.user.username}"
    
