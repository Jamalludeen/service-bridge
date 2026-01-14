from rest_framework import serializers
from .models import Service, Professional
from professional.models import ServiceCategory


class ProfessionalSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Professional
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
        ]


class AdminServiceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Service
        fields = ["id", "professional", "category", "category_name", "title", "description", "pricing_type", "price_per_unit", "is_active"]


class ProfessionalServiceSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "professional",
            "category",
            "category_name",
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