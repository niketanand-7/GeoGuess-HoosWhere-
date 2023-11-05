from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Challenge, Guess
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ChallengeForm, GuessForm, ApproveChallengeForm
import os

# Create your views here.
class Home(generic.TemplateView):
    template_name = "home.html"


class AddChallengeView(LoginRequiredMixin, generic.CreateView):
    template_name = 'user/challenge.html'
    login_url = '/'

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
        return redirect("submissions")   # Redirect to homepage or any other page after saving
    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data()
        )
    
class MapsView(LoginRequiredMixin, TemplateView):
    template_name = 'user/maps.html'
    login_url = '/'

    form_class = GuessForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps_api_key'] = os.environ.get('GOOGLE_MAPS_API_KEY')
        context['Challenge'] = Challenge.objects.filter(approve_status=True).first() #sets the information for the challenge being used
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

class ViewSubmissions(LoginRequiredMixin, generic.ListView):
    template_name = "user/viewSubmissions.html"
    login_url = '/'

    context_object_name = "challenges"

    # get all google registered users
    def get_queryset(self):
        return Challenge.objects.filter(user=self.request.user)

class LeaderboardView(generic.ListView):
    template_name = "leaderboard.html"
    context_object_name = "leaderboard"
    # Determines how much weight to give to average score vs max score for leaderboard
    weight = 0.8
    def get_queryset(self):
        user_list = User.objects.all()
        guess_list = Guess.objects.all()
        user_stats = {}
        for guess in guess_list:
            username = guess.user.username
            if username not in user_stats:
                user_stats[username] = {"score": 0, "games_played": 0}

            user_stats[username]["games_played"] += 1
            user_stats[username]["score"] += guess.score

        leaderboard = []
        for user in user_list:
            if(user.username in user_stats):
                games_played = user_stats[user.username]["games_played"]
                average_score = 0
                if(games_played != 0):
                    average_score = user_stats[user.username]["score"] / games_played

                # Calculate rating based on average score and games played (Can be changed in the future)
                rating = (self.weight * average_score) + ((1 - self.weight) * games_played) * 1000

                leaderboard.append({"name": user.first_name, "average_score": int(average_score), 
                                    "games_played": int(games_played), "rating": int(rating)})
        return sorted(leaderboard, key=lambda x: x['rating'], reverse=True)

##########################################################################3
#Admin Views
class AdminUsersView(LoginRequiredMixin, generic.ListView):
    template_name = "admin/users.html"
    login_url='/'
    context_object_name = "user_list"
    
    #get all google registered users
    def get_queryset(self):
        return User.objects.all()
    
    # def post(self, request, *args, **kwargs):
    #     if 'deleteUser' in request.POST:

        

class ApproveSubmissionsView(LoginRequiredMixin, generic.ListView):
    template_name = "admin/approveSubmissions.html"
    login_url='/'
    form_name = ApproveChallengeForm
    context_object_name = "challenge_list"

    def get_queryset(self):
        return Challenge.objects.filter(Q(approve_status=False) & Q(approval_feedback=''))
    
    def post(self, request):
        challenge_id = request.POST.get('challenge_id')
        challenge = get_object_or_404(Challenge, id=challenge_id)
        return render(request, self.template_name, {'challenge': challenge})
    
def get_admin_feedback(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if 'approved' in request.POST:
        challenge.approve_status=True
        challenge.save()

    if 'denied' in request.POST:
        feedback = request.POST.get('feedback')
        challenge.approval_feedback = feedback
        challenge.save()

    return HttpResponseRedirect(reverse('approve_submissions'))


 