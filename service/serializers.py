from rest_framework import serializers
from .models import Service, Professional


class AdminServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "professional", "category", "title", "description", "pricing_type", "price_per_unit", "is_active"]


class ProfessionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "professional",
            "category",
            "title",
            "description",
            "pricing_type",
            "price_per_unit",
            "is_active",
        ]
        read_only_fields = ["professional"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        if user.role != "professional":
            raise serializers.ValidationError(
                {"detail": "Only professional users can create services."}
            )

        # Professional profile existence check
        try:
            professional = Professional.objects.get(user=user)
        except Professional.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Professional profile not found. Please create your profile first."}
            )

        # Force ownership
        validated_data["professional"] = professional
        return super().create(validated_data)