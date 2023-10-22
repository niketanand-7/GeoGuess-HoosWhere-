from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.views import generic
from django.shortcuts import render
import os

# def is_superuser(user):
#     return user.is_superuser

class Home(TemplateView):
    template_name = "home.html"

# Create your views here.
@login_required
def index(request):
    return HttpResponse("Hello, you are at the geoguessing homepage.")

@login_required
def maps_view(request):
    context = {
        'maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY')
    }
    return render(request, 'maps.html', context)

class AdminUsersView(generic.ListView):
    template_name = "admin/users.html"
    context_object_name = "user_list"
    
    #get all google registered users
    def get_queryset(self):
        return User.objects.all()
