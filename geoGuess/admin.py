from django.contrib import admin

# Register your models here.
from .models import Challenge, Guess
admin.site.register(Challenge)
admin.site.register(Guess)