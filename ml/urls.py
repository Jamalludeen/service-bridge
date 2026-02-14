from django.urls import path
from .views import (
    RecommendedServicesView,
    RecommendedProfessionalsView,
    RecommendedCategoriesView,
    SimilarServicesView,
    SuggestedCategoriesForProfessionalView,
    PricingSuggestionView,
    CancellationRiskView,
    DemandForecastView,
    PeakHoursView
)

urlpatterns = [
    # Customer Recommendations
    path(
        'recommendations/services/',
        RecommendedServicesView.as_view(),
        name='recommended-services'
    ),
    path(
        'recommendations/professionals/',
        RecommendedProfessionalsView.as_view(),
        name='recommended-professionals'
    ),
    path(
        'recommendations/categories/',
        RecommendedCategoriesView.as_view(),
        name='recommended-categories'
    ),
    path(
        'recommendations/services/<int:service_id>/similar/',
        SimilarServicesView.as_view(),
        name='similar-services'
    ),

    # Professional Recommendations
    path(
        'professional/suggested-categories/',
        SuggestedCategoriesForProfessionalView.as_view(),
        name='suggested-categories'
    ),
    path(
        'professional/pricing-suggestion/<int:service_id>/',
        PricingSuggestionView.as_view(),
        name='pricing-suggestion'
    ),

    # Predictive Analytics
    path(
        'analytics/cancellation-risk/<int:booking_id>/',
        CancellationRiskView.as_view(),
        name='cancellation-risk'
    ),
    path(
        'analytics/demand-forecast/',
        DemandForecastView.as_view(),
        name='demand-forecast'
    ),
    path(
        'analytics/peak-hours/',
        PeakHoursView.as_view(),
        name='peak-hours'
    ),
]
