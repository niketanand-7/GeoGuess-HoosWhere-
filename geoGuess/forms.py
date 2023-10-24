from django import forms
from .models import Location, Challenge

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['place']

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['image', 'longitude', 'latitude']
