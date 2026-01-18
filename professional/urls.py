from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import ServiceCategoryViewset, ProfessionalProfileViewSet

router = DefaultRouter()
router.register(r'services', ServiceCategoryViewset)
router.register('profile', ProfessionalProfileViewSet, basename='professionals')

urlpatterns = [
    path('', include(router.urls)),
    # path("profile/", ProfessionalProfileView.as_view(), name="professional_profile"),
    # path("profile/", ProfessionalProfileView.as_view()),
    # path("profile/<int:pk>/", ProfessionalProfileView.as_view()),
]