from .models import Challenge
def generate_daily_challenge():
    challenge_list = Challenge.objects.filter(approve_status=True)
