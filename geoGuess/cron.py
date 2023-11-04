from .models import Challenge
import math
def generate_daily_challenge():
    challenge_list = Challenge.objects.filter(approve_status=True)
    if len(challenge_list) > 0:
        challenge = challenge_list[math.random(0, challenge_list.count())]
        return challenge
    else:
        return None
