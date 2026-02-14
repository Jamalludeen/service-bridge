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


# PROFESSIONAL RECOMMENDATION ENDPOINTS


class SuggestedCategoriesForProfessionalView(APIView):
    """
    GET /api/ml/professional/suggested-categories/

    Get suggested service categories for the professional to add.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'professional':
            return Response(
                {"error": "Only professionals can access this."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            professional = request.user.professional
        except:
            return Response(
                {"error": "Professional profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        engine = ProfessionalRecommendationEngine(professional)
        categories = engine.get_suggested_categories()

        serializer = CategoryRecommendationSerializer(categories, many=True)

        return Response({
            "suggestions": serializer.data
        })


class PricingSuggestionView(APIView):
    """
    GET /api/ml/professional/pricing-suggestion/{service_id}/

    Get optimal pricing suggestion for a service.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id):
        if request.user.role != 'professional':
            return Response(
                {"error": "Only professionals can access this."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            professional = request.user.professional
            service = Service.objects.get(id=service_id, professional=professional)
        except Service.DoesNotExist:
            return Response(
                {"error": "Service not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        engine = ProfessionalRecommendationEngine(professional)
        pricing = engine.get_optimal_pricing(service_id)

        if not pricing:
            return Response(
                {"error": "Not enough market data for pricing suggestion."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PricingSuggestionSerializer(pricing)

        return Response(serializer.data)


# PREDICTIVE ANALYTICS ENDPOINTS

class CancellationRiskView(APIView):
    """
    GET /api/ml/analytics/cancellation-risk/{booking_id}/

    Get cancellation risk prediction for a booking.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check access
        user = request.user
        if user.role == 'customer' and booking.customer.user != user:
            return Response(
                {"error": "Access denied."},
                status=status.HTTP_403_FORBIDDEN
            )
        if user.role == 'professional' and booking.professional.user != user:
            return Response(
                {"error": "Access denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        predictor = CancellationRiskPredictor()
        risk = predictor.predict_risk(booking)

        serializer = CancellationRiskSerializer(risk)

        return Response(serializer.data)


class DemandForecastView(APIView):
    """
    GET /api/ml/analytics/demand-forecast/
    GET /api/ml/analytics/demand-forecast/?category_id=1&city=Kabul&days=7

    Get demand forecast for services.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_id = request.query_params.get('category_id')
        city = request.query_params.get('city')
        days = int(request.query_params.get('days', 7))

        forecaster = DemandForecaster()
        forecasts = forecaster.get_demand_forecast(
            category_id=category_id,
            city=city,
            days_ahead=days
        )

        serializer = DemandForecastSerializer(forecasts, many=True)

        return Response({
            "category_id": category_id,
            "city": city,
            "forecasts": serializer.data
        })