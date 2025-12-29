from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.CustomerProfileView.as_view(), name="profile"),
]