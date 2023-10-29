from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from .import views
from .views import Home, AdminUsersView, AddChallengeView, MapsView, ViewSubmissions


urlpatterns = [
    path("", Home.as_view(), name="home"),
    #path('', TemplateView.as_view(template_name="index.html")),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('maps/', MapsView.as_view(), name="maps"),
    path('submissions/', ViewSubmissions.as_view(), name="submissions"),
    path('admin_users/', AdminUsersView.as_view(), name="admin_users"),
    path('challenge_form/', AddChallengeView.as_view(), name="challenge")
]