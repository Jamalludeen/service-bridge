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
