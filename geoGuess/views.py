from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import LocationForm
from django.views import generic
import os

class Home(generic.TemplateView):
    template_name = "home.html"

# Create your views here.
class Choice_View(generic.CreateView):
    template_name = 'addChoice.html'
    form_class = LocationForm

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        form.save(commit=True)
        return redirect("home") #can change later to have success page?
        
    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data()
        )


def maps_view(request):
    context = {
        'maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY')
    }
    return render(request, 'maps.html', context)
