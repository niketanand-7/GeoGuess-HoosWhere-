from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from .import views
from .views import Home, AdminUsersView, AddChallengeView, MapsView, ViewSubmissions, ApproveSubmissionsView, LeaderboardView


urlpatterns = [
    path("", Home.as_view(), name="home"),

    #these two are part of Google Oauth
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('maps/', MapsView.as_view(), name="maps"),
    path('submissions/', ViewSubmissions.as_view(), name="submissions"),
    path('admin_users/', AdminUsersView.as_view(), name="admin_users"),
    path('approve_submissions/', ApproveSubmissionsView.as_view(), name="approve_submissions"),
    path('challenge_form/', AddChallengeView.as_view(), name="challenge"),
    path('leaderboard/', LeaderboardView.as_view(), name="leaderboard"),

    path('challenge_feedback/<int:challenge_id>/', views.get_admin_feedback, name='admin_feedback'),
]