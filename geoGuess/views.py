from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.views import generic
from django.shortcuts import render, redirect
from .forms import LocationForm, ChallengeForm
import os

# Create your views here.
@login_required
def index(request):
    return HttpResponse("Hello, you are at the geoguessing homepage.")

class Home(generic.TemplateView):
    template_name = "home.html"

# # Create your views here.
# class Choice_View(generic.CreateView):
#     template_name = 'addChoice.html'
#     form_class = LocationForm

#     def post(self, request, *args, **kwargs):
#         self.object = None
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         form.save(commit=True)
#         return redirect("home") #can change later to have success page?
        
#     def form_invalid(self, form):
#         return self.render_to_response(
#             self.get_context_data()
#         )

def challenge_view(request):
    # Initialize the form
    if request.method == "POST":
        form = ChallengeForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the challenge and set the user before saving
            challenge = form.save(commit=False)
            challenge.user = request.user
            challenge.save()
            # Redirect to homepage or any other page after saving
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ChallengeForm()
    
    context = {
        'form': form,
        'maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY')
    }
    
    return render(request, 'challenge.html', context)

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
