from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, you are at the geoguessing homepage.")
