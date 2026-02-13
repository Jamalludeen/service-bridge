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
