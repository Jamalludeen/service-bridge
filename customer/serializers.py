from rest_framework import serializers

from django.contrib.auth import get_user_model

import re 

from .models import CustomerProfile, Cart, CartItem
from service.models import Service
from service.serializers import ProfessionalServiceSerializer, CartServiceSerializer


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
        fields = ["user", "profile_image", "city", "district", "detailed_address", "latitude", "longitude"]
    
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
    
class CartItemSerializer(serializers.ModelSerializer):
    service_details = CartServiceSerializer(source='service', read_only=True)
    estimated_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_service_available = serializers.BooleanField(read_only=True)
    professional_name = serializers.CharField(
        source='service.professional.get_full_name',
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'service',
            'service_details',
            'quantity',
            'estimated_price',
            'is_service_available',
            'professional_name',
        ]
        read_only_fields = [
            'id',
            'price_per_unit',
        ]
    
    def validate_service(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "This service is not longer available"
            )

        if not value.professional.is_active:
            raise serializers.ValidationError(
                "This professional is not longer available"
            )
        return value
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity cannot be less than 1."
            )
        if value > 100:
            raise serializers.ValidationError(
                "Maximum quantity is 100 per item."
            )
        return value
 

class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding items to cart
    Simplified version for creation
    """
    class Meta:
        model = CartItem
        fields = [
            'service',
            'quantity',
        ]

    # def validate_service(self, value):
    #     """Ensure service exists and is available"""
    #     if not value.is_active:
    #         raise serializers.ValidationError("Service is not available")
    #     return value

class CartItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating cart items
    Service cannot be changed, only other fields
    """
    class Meta:
        model = CartItem
        fields = [
            'quantity',
        ]


class CartSerializer(serializers.ModelSerializer):
    """
    Complete cart serializer with all items
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_empty = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'customer',
            'items',
            'total_items',
            'total_price',
            'is_empty',
            # 'created_at',
            # 'updated_at',
        ]
        read_only_fields = [
            'id',
            'customer',
            # 'created_at',
            # 'updated_at',
        ]
