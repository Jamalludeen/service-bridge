from rest_framework import serializers
from .models import ServiceCategory, Professional


class ProfessionalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = [
            'city', 'bio', 'years_of_experience', 'services', 'profile',
            'document', 'preferred_language'
        ]

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = [
            "id", "name"
        ]


class ProfessionalCreateSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        many=True
    )

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Professional
        fields = [
            "user", "city", "bio", "years_of_experience", "services", "verification_status",
            "profile", "document", "latitude", "longitude", "preferred_language", 
        ]

    def create(self, validated_data):
        # Pop user object
        user = validated_data.pop('user')

        # Pop services (ManyToMany)
        services = validated_data.pop('services', [])

        # Create Professional instance
        professional = Professional(user=user, **validated_data)
        professional.save()  # must save before assigning M2M

        # Assign ManyToMany services
        if services:
            professional.services.set(services)

        return professional
    