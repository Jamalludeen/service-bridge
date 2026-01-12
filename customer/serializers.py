from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomerProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email"]


class RetrieveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "role"]


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = CustomerProfile
        fields = '__all__'



class CustomerRetrieveProfileSerializer(serializers.ModelSerializer):
    user = RetrieveUserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            "id", "user", "profile_image", "city", "district", "detailed_address",
            "latitude", "longitude", "preferred_language", "total_bookings", "avg_rating_given"
            ]


class CustomerUpdateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = CustomerProfile
        fields = ["user", "profile_image", "city", "district", "detailed_address"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return super().update(instance, validated_data)