from django.urls import path
from . import views

urlpatterns = [
    path("create-profile/", views.CustomerProfileView.as_view(), name="create_profile"),
    path("my-profile/", views.CustomerProfileRetrieveView.as_view(), name="get_user_profile"),
]