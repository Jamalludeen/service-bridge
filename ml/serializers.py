from rest_framework import serializers
from service.serializers import CustomerServiceSerializer
from professional.serializers import ProfessionalSerializer


class ServiceRecommendationSerializer(serializers.Serializer):
    """Serializer for recommended services"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    pricing_type = serializers.CharField()
    category_name = serializers.SerializerMethodField()
    professional_name = serializers.SerializerMethodField()
    professional_rating = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_professional_name(self, obj):
        return obj.professional.user.get_full_name() or obj.professional.user.email

    def get_professional_rating(self, obj):
        return obj.professional.avg_rating


class ProfessionalRecommendationSerializer(serializers.Serializer):
    """Serializer for recommended professionals"""
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    bio = serializers.CharField()
    avg_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    years_of_experience = serializers.IntegerField()
    city = serializers.CharField()
    categories = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def get_categories(self, obj):
        return list(obj.services.values_list('name', flat=True))


class CategoryRecommendationSerializer(serializers.Serializer):
    """Serializer for recommended categories"""
    id = serializers.IntegerField()
    name = serializers.CharField()


class CancellationRiskSerializer(serializers.Serializer):
    """Serializer for cancellation risk prediction"""
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField()
    factors = serializers.DictField()



class DemandForecastSerializer(serializers.Serializer):
    """Serializer for demand forecast"""
    date = serializers.CharField()
    day_of_week = serializers.CharField()
    predicted_bookings = serializers.FloatField()
    confidence = serializers.CharField()
    trend = serializers.CharField()


class PeakHoursSerializer(serializers.Serializer):
    """Serializer for peak hours"""
    hour = serializers.IntegerField()
    time_range = serializers.CharField()
    bookings = serializers.IntegerField()
    intensity = serializers.FloatField()


class PricingSuggestionSerializer(serializers.Serializer):
    """Serializer for pricing suggestions"""
    current_price = serializers.FloatField()
    market_average = serializers.FloatField()
    suggested_price = serializers.FloatField()
    min_market = serializers.FloatField()
    max_market = serializers.FloatField()
