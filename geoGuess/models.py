from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    place = models.CharField(max_length=200)
    
    def __str__(self):
        return self.place
    


class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who created the challenge
    image = models.ImageField(upload_to='challenges/')        # Store the uploaded image
    longitude = models.FloatField()
    latitude = models.FloatField()               # Store the answer coordinates
    timestamp = models.DateTimeField(auto_now_add=True)        # Automatically set when the challenge is created
    approve_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Challenge {self.pk} by {self.user.username}"

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"

    
