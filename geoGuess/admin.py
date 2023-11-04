from django.contrib import admin

# Register your models here.
from .models import Challenge, Guess, DailyChallenge
admin.site.register(Challenge)
admin.site.register(Guess)
admin.site.register(DailyChallenge)