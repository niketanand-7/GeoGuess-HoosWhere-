from django.db import models

class Location(models.Model):
    place = models.CharField(max_length=200)
    
    def __str__(self):
        return self.place