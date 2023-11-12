from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from .import views
from .views import Home, AdminUsersView, AddChallengeView 
from .views import ViewSubmissions, ApproveSubmissionsView, LeaderboardView, DailyChallengeView, DailyChallengeListView, ProfileView


urlpatterns = [
    path("", Home.as_view(), name="home"),

    #these two are part of Google Oauth
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('daily_challenges', DailyChallengeListView.as_view(), name="daily_challenge_list"),
    path('daily_challenge/<int:pk>/', DailyChallengeView.as_view(), name="daily_challenge"),
    path('submissions/', ViewSubmissions.as_view(), name="submissions"),
    path('admin_users/', AdminUsersView.as_view(), name="admin_users"),
    path('approve_submissions/', ApproveSubmissionsView.as_view(), name="approve_submissions"),
    path('challenge_form/', AddChallengeView.as_view(), name="challenge"),
    path('leaderboard/', LeaderboardView.as_view(), name="leaderboard"),

    path('edit_user/<int:user_id>/', views.edit_user, name='user_edit'),
    path('user/<int:pk>/', ProfileView.as_view(), name="profile"),
    path('challenge_feedback/<int:challenge_id>/', views.get_admin_feedback, name='admin_feedback'),
]