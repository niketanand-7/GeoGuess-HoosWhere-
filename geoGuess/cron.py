from .models import Challenge, DailyChallenge
from random import randint
def generate_daily_challenge():
    challenge_list = Challenge.objects.filter(approve_status=True)
    daily_challenge_list = DailyChallenge.objects.all()

    # Remove challenges that have already been used
    for daily_challenge in daily_challenge_list:
        challenge_list = challenge_list.exclude(id=daily_challenge.challenge.id)
    
    if len(challenge_list) > 0:
        challenge = challenge_list[randint(0, challenge_list.count() - 1)]
        return challenge
    else:
        return None
