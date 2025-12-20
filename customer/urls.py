from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.CustomerProfileView.as_view(), name="create_profile"),
    path("my-profile/", views.CustomerProfileRetrieveView.as_view(), name="get_customer_profile"),
    path("update-profile/", views.CustomerProfileUpdateView.as_view(), name="update_customer_profile"),
]