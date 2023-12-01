from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Challenge, Guess, DailyChallenge
from django.views import generic
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ChallengeForm, ApproveChallengeForm
import os


# Checks if the user has guessed a challenge
def hasBeenGuessed(challenge, user):
    return Guess.objects.filter(user=user, challenge=challenge).exists()

def rating_calc(average_score, games_played):
    # Determines how much weight to give to average score vs max score for leaderboard
    weight = 0.8
    return int((weight * average_score) + ((1 - weight) * games_played * average_score))

# Gets the leaderboard of players
def get_leaderboard():
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
            rating = rating_calc(average_score, games_played)

            leaderboard.append({"name": user.first_name, 
                                "average_score": int(average_score), 
                                "games_played": int(games_played), 
                                "rating": int(rating),
                                "id": user.id})
    return sorted(leaderboard, key=lambda x: x['rating'], reverse=True)

# Gets the statistics for an individual player
def get_player_stats(user):
    guess_list = Guess.objects.filter(user=user)
    games_played = guess_list.count()
    average_score = 0
    if(games_played != 0):
        average_score = sum([guess.score for guess in guess_list]) / games_played

    return {"games_played": games_played, "average_score": average_score, "rating": rating_calc(average_score, games_played)}
def get_user_leaderboard_position(user):
    leaderboard = get_leaderboard()
    for index, entry in enumerate(leaderboard, start = 1):
        if entry['id'] == user.id:
            return index
    return None
def get_recent_guesses(user):
    guess_list = Guess.objects.filter(user=user)
    return guess_list.order_by('-id')[:5]

#Home View
class Home(generic.TemplateView):
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            player_stats = get_player_stats(self.request.user)
            context['player_stats'] = get_player_stats(self.request.user)
            context['leaderboard_position'] = get_user_leaderboard_position(self.request.user)
        return context


# View to add a challenge
class AddChallengeView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
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
    
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff
    
# View to see past challenges and current challenge
class DailyChallengeListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "user/daily_challenge_list.html"
    login_url = '/'
    context_object_name = "daily_challenge_list"

    def get_queryset(self):
        return DailyChallenge.objects.filter(challenge__approve_status=True)
    
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff

# View to see a specific daily challenge
class DailyChallengeView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    template_name = "user/daily_challenge.html"
    login_url = '/'
    model = DailyChallenge

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps_api_key'] = os.environ.get('GOOGLE_MAPS_API_KEY')
        # Sets information for the challenge being used
        context['Challenge'] = self.get_object().challenge
        context['DailyChallenge'] = DailyChallenge.objects.get(challenge=self.get_object().challenge)

        print(self.get_template_names())
        if 'user/daily_challenge_guessed.html' in self.get_template_names():
            context['Guess'] = Guess.objects.get(user=self.request.user, challenge=self.get_object().challenge)
        return context

    def post(self, request, *args, **kwargs):
        longitude = request.POST.get('longitude')
        latitude = request.POST.get('latitude')
        challenge = self.get_object().challenge

        if longitude != '' and latitude != '':
            # TODO: add checks for the latitude and longitude to make sure they are valid            
            guess = Guess(user=request.user, challenge=challenge, longitude=longitude, latitude=latitude)
            guess.save()
            return redirect("daily_challenge", pk=self.get_object().pk)
         
        # TODO: can make this with less repeated code.
        return render(
            request,
            self.template_name,
            {
                'Challenge': challenge,
                'maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY'),
            }
        )

    def get_template_names(self):
        if(hasBeenGuessed(self.get_object().challenge, self.request.user)):
            return ["user/daily_challenge_guessed.html"]
        
        return ["user/daily_challenge.html"]
    
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff

class ViewSubmissions(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "user/viewSubmissions.html"
    login_url = '/'

    context_object_name = "challenges"

    # get all google registered users
    def get_queryset(self):
        return Challenge.objects.order_by('-id').filter(user=self.request.user)
    
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff

class LeaderboardView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "leaderboard.html"
    context_object_name = "leaderboard"
    
    def get_queryset(self):
        return get_leaderboard()
    
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff

class ProfileView(generic.DetailView, UserPassesTestMixin):
    template_name = "user/profile.html"
    context_object_name = "user"

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = get_player_stats(self.get_object())
        context['recent_guesses'] = get_recent_guesses(self.get_object())
        return context
    
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff

##########################################################################3
#Admin Views
class AdminUsersView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "admin/users.html"
    login_url='/'
    context_object_name = "user_list"
    
    #get all google registered users
    def get_queryset(self):
        return User.objects.all()

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    
    # def post(self, request, *args, **kwargs):
    #     if 'deleteUser' in request.POST:

def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if 'editAuth' in request.POST:
        checkbox = request.POST.get('admin')
        if checkbox == "on":
            admin = True
        else:
            admin = False

        user.is_staff = admin
        user.save()

    if 'deleteUser' in request.POST:
        user.delete()

    if request.user == user:
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('admin_users'))
        
class ApproveSubmissionsView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "admin/approveSubmissions.html"
    login_url='/'
    form_name = ApproveChallengeForm
    context_object_name = "challenge_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps_api_key'] = os.environ.get('GOOGLE_MAPS_API_KEY')
        return context

    def get_queryset(self):
        return Challenge.objects.filter(Q(approve_status=False) & Q(approval_feedback=''))

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    
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


class ChallengeBankView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = "admin/challengeBank.html"
    context_object_name = "challenge_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Count'] = self.get_queryset().count
        return context

    def get_queryset(self):
        challenge_list = Challenge.objects.filter(approve_status=True)
        daily_challenge_list = DailyChallenge.objects.all()
        for daily_challenge in daily_challenge_list:
            challenge_list = challenge_list.exclude(id=daily_challenge.challenge.id)
        return challenge_list

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff