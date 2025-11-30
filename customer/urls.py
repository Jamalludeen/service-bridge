from django.urls import path
from . import views

urlpatterns = [
    path("create-profile/", views.CustomerProfileView.as_view(), name="create_profile"),
]