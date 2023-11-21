from django.core.management.base import BaseCommand
from geoGuess.models import DailyChallenge
from geoGuess.cron import generate_daily_challenge  # Implement a function to select a random challenge

"""
Created with help from GPT 3.5, of how to create a cron service to generate a daily challenge at a specific time every day.
"""
class Command(BaseCommand):
    help = 'Generate daily challenge at 12:00 AM EST every day.'

    def handle(self, *args, **kwargs):
        daily_challenge = generate_daily_challenge()  # Implement this function to select a random challenge
        if daily_challenge is None:
            self.stdout.write(self.style.ERROR('No challenges to add.'))
            return
        DailyChallenge.objects.create(challenge=daily_challenge)
        self.stdout.write(self.style.SUCCESS('Daily challenge added successfully.'))