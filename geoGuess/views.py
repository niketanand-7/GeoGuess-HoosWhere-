from django.http import HttpResponse
from django.views.generic import TemplateView

class Home(TemplateView):
    template_name = "home.html"

# Create your views here.
def index(request):
    return HttpResponse("Hello, you are at the geoguessing homepage.")
