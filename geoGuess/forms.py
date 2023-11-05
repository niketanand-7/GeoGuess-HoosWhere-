from django import forms
from .models import Guess, Challenge

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['image', 'longitude', 'latitude']
        
class GuessForm(forms.ModelForm):
    class Meta:
        model = Guess
        fields = ['latitude', 'longitude']
        
class ApproveChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['approve_status', 'approval_feedback']
    
