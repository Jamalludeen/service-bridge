from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .recommendation_engine import (
    RecommendationEngine,
    ProfessionalRecommendationEngine
)
from .predictive_analytics import CancellationRiskPredictor, DemandForecaster
from .serializers import (
    ServiceRecommendationSerializer,
    ProfessionalRecommendationSerializer,
    CategoryRecommendationSerializer,
    CancellationRiskSerializer,
    DemandForecastSerializer,
    PeakHoursSerializer,
    PricingSuggestionSerializer
)
from booking.models import Booking
from service.models import Service


# CUSTOMER RECOMMENDATION ENDPOINTS

class RecommendedServicesView(APIView):
    """
    GET /api/ml/recommendations/services/

    Get personalized service recommendations for the authenticated customer.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'customer':
            return Response(
                {"error": "Only customers can access recommendations."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = request.user.customerprofile
        except:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        limit = int(request.query_params.get('limit', 10))

        engine = RecommendationEngine(customer)
        services = engine.get_recommended_services(limit=limit)

        serializer = ServiceRecommendationSerializer(services, many=True)

        return Response({
            "count": len(services),
            "recommendations": serializer.data
        })



class RecommendedProfessionalsView(APIView):
    """
    GET /api/ml/recommendations/professionals/
    GET /api/ml/recommendations/professionals/?category_id=1

    Get recommended professionals for the authenticated customer.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'customer':
            return Response(
                {"error": "Only customers can access recommendations."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = request.user.customerprofile
        except:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        category_id = request.query_params.get('category_id')
        limit = int(request.query_params.get('limit', 10))

        engine = RecommendationEngine(customer)
        professionals = engine.get_recommended_professionals(
            category_id=category_id,
            limit=limit
        )

        serializer = ProfessionalRecommendationSerializer(professionals, many=True)

        return Response({
            "count": len(professionals),
            "recommendations": serializer.data
        })


class RecommendedCategoriesView(APIView):
    """
    GET /api/ml/recommendations/categories/

    Get recommended service categories for the customer.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'customer':
            return Response(
                {"error": "Only customers can access recommendations."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = request.user.customerprofile
        except:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        limit = int(request.query_params.get('limit', 5))

        engine = RecommendationEngine(customer)
        categories = engine.get_recommended_categories(limit=limit)

        serializer = CategoryRecommendationSerializer(categories, many=True)

        return Response({
            "count": len(categories),
            "recommendations": serializer.data
        })


class SimilarServicesView(APIView):
    """
    GET /api/ml/recommendations/services/{service_id}/similar/

    Get services similar to a given service.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id):
        try:
            customer = request.user.customerprofile
        except:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        limit = int(request.query_params.get('limit', 5))

        engine = RecommendationEngine(customer)
        services = engine.get_similar_services(service_id, limit=limit)

        serializer = ServiceRecommendationSerializer(services, many=True)

        return Response({
            "count": len(services),
            "similar_services": serializer.data
        })
