from django.contrib.auth import get_user_model

from rest_framework import serializers

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


class RetrieveUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class ProfessionalUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = Professional
        fields = [
            'user',
            'city',
            'bio',
            'years_of_experience',
            'services',
            'profile',
            'document',
            'preferred_language',
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        # Only update user IF user data is explicitly sent
        if user_data is not None:
            user = instance.user

            email = user_data.get("email")
            phone = user_data.get("phone")

            if email and email != user.email:
                if not email.endswith("@gmail.com"):
                    raise serializers.ValidationError({
                        "user": {"email": "Please enter a valid Gmail address"}
                    })
                user.email = email

            if phone and phone != user.phone:
                afghan_phone_regex = r'^\+93\d{9}$'
                if not re.match(afghan_phone_regex, phone):
                    raise serializers.ValidationError({
                        "user": {"phone": "Phone number must start with +93"}
                    })
                user.phone = phone

            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.save()

        # ✅ Update Professional fields normally
        return super().update(instance, validated_data)



class ProfessionalRetrieveSerializer(serializers.ModelSerializer):
    user = RetrieveUserSerializer(required=False)
    class Meta:
        model = Professional
        fields = [
            'id', 'user', 'city', 'bio', 'years_of_experience', 'services', 'profile',
            'document', 'preferred_language', 'avg_rating'
        ]


class ProfessionalListSerializer(serializers.ModelSerializer):
    """Public-facing serializer with reduced fields for list endpoint."""
    user = RetrieveUserListSerializer(read_only=True)
    class Meta:
        model = Professional
        fields = [
            'id', 'user', 'city', 'years_of_experience', 'services', 'profile', 'avg_rating'
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
    