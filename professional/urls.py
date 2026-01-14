from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import ServiceCategoryViewset, ProfessionalProfileView

router = DefaultRouter()
router.register(r'services', ServiceCategoryViewset)

urlpatterns = [
    path('', include(router.urls)),
    path("profile/", ProfessionalProfileView.as_view(), name="professional_profile"),
]