from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from .import views
from .views import Home
from .views import AdminUsersView
from .views import Home, Choice_View

urlpatterns = [
    path("", Home.as_view(), name="home"),
    #path('', TemplateView.as_view(template_name="index.html")),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('maps/', views.maps_view, name = "challenge"),
    path('admin_users/', AdminUsersView.as_view(),name="admin_users"),
    path('choice/', Choice_View.as_view(), name="choice")
]