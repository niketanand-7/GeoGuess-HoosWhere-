from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Challenge, Guess
from django.views import generic
from django.shortcuts import render, redirect
from .forms import ChallengeForm, GuessForm, ApproveChallengeForm
import os

# Create your views here.
class Home(generic.TemplateView):
    template_name = "home.html"


class AddChallengeView(generic.CreateView):
    template_name = 'challenge.html'
    form_class = ChallengeForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps_api_key'] = os.environ.get('GOOGLE_MAPS_API_KEY')
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid() and request.user.is_authenticated:
            challenge = form.save(commit=False)
            challenge.user = request.user
            challenge.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        form.save(commit=True)
        return redirect("home")   # Redirect to homepage or any other page after saving
    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data()
        )
    
class MapsView(TemplateView):
    template_name = 'maps.html'
    form_class = GuessForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps_api_key'] = os.environ.get('GOOGLE_MAPS_API_KEY')
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid() and request.user.is_authenticated:
            guess = form.save(commit=False)
            guess.user = request.user
            guess.challenge = request.challenge
            guess.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        form.save(commit=True)
        return redirect("home")   # Redirect to homepage or any other page after saving
    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data()
        )

class ViewSubmissions(generic.ListView):
    template_name = "viewSubmissions.html"
    context_object_name = "challenges"

    # get all google registered users
    def get_queryset(self):
        return Challenge.objects.filter(user=self.request.user)
    
##########################################################################3
#Admin Views
class AdminUsersView(generic.ListView):
    template_name = "admin/users.html"
    login_url='/'
    context_object_name = "user_list"
    
    #get all google registered users
    def get_queryset(self):
        return User.objects.all()

class ApproveSubmissionsView(generic.ListView):
    template_name = "admin/approveSubmissions.html"
    form_name = ApproveChallengeForm
    context_object_name = "challenge_list"

    def post(self, request, *args, **kwargs):
        approved_challenge = request.POST.getlist('approved_challenges')
        Challenge.objects.filter(id__in=approved_challenge).update(approve_status=True)
        challenge_list = Challenge.objects.filter(approve_status=False)
        return render(request, "admin/approveSubmissions.html", {'challenge_list': challenge_list})

    def get_queryset(self):
        return Challenge.objects.all()




