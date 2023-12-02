from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from .import views
from .views import Home, AdminUsersView, AddChallengeView, ChallengeBankView, AboutView
from .views import ViewSubmissions, ApproveSubmissionsView, LeaderboardView, DailyChallengeView, DailyChallengeListView, ProfileView


urlpatterns = [
    path("", Home.as_view(), name="home"),

    #these two are part of Google Oauth
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),

    ##REGULAR USER URLS##
    path('about/', AboutView.as_view(), name='about'),
    path('daily_challenges', DailyChallengeListView.as_view(), name="daily_challenge_list"),
    path('daily_challenge/<int:pk>/', DailyChallengeView.as_view(), name="daily_challenge"),
    path('submissions/', ViewSubmissions.as_view(), name="submissions"),
    path('challenge_form/', AddChallengeView.as_view(), name="challenge"),
    path('leaderboard/', LeaderboardView.as_view(), name="leaderboard"),
    path('user/<int:pk>/', ProfileView.as_view(), name="profile"),


    ##ADMIN URLS##
    path('admin_users/', AdminUsersView.as_view(), name="admin_users"),
    path('challenge_bank/', ChallengeBankView.as_view(), name="challenge_bank"),
    path('edit_user/<int:user_id>/', views.edit_user, name='user_edit'),
    path('challenge_feedback/<int:challenge_id>/', views.get_admin_feedback, name='admin_feedback'),
    path('approve_submissions/', ApproveSubmissionsView.as_view(), name="approve_submissions"),
]