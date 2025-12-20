from rest_framework import serializers
from .models import CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        


class CustomerRetrieveProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = [
            "id", "profile_image", "city", "district", "detailed_address", 
            "latitude", "longitude", "preferred_language", "total_bookings", "avg_rating_given"
            ]


class CustomerUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ["profile_image", "city", "district", "detailed_address"]