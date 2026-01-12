from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

from .models import ServiceCategory, Professional

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email"]


class RetrieveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "role"]


class ProfessionalUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    class Meta:
        model = Professional
        fields = [
            'user', 'city', 'bio', 'years_of_experience', 'services', 'profile',
            'document', 'preferred_language'
        ]
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            email: str = user_data.get("email", "")
            phone: str = user_data.get("phone", "")

            if email and not email.endswith("@gmail.com"):
                raise serializers.ValidationError({
                    "email": "Please enter a valid Gmail address"
                })

            # Afghanistan phone validation
            if phone:
                afghan_phone_regex = r'^\+93\d{9}$'
                if not re.match(afghan_phone_regex, phone):
                    raise serializers.ValidationError({
                        "phone": "Phone number must be a valid Afghanistan number starting with +93"
                    })

            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return super().update(instance, validated_data)


class ProfessionalRetrieveSerializer(serializers.ModelSerializer):
    user = RetrieveUserSerializer(required=False)
    class Meta:
        model = Professional
        fields = [
            'user', 'city', 'bio', 'years_of_experience', 'services', 'profile',
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
    