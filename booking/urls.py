
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, BookingStatusHistoryViewSet

router = DefaultRouter()
router.register('', BookingViewSet, basename='booking')
router.register('history', BookingStatusHistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
]