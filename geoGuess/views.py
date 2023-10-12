from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render
import os

class Home(TemplateView):
    template_name = "home.html"

# Create your views here.
def index(request):
    return HttpResponse("Hello, you are at the geoguessing homepage.")



def maps_view(request):
    context = {
        'maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY')
    }
    return render(request, 'maps.html', context)
