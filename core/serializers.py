from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'phone', 'role', 'password',
        ]

    def validate_phone(self, phone: str):
        """
        Validate Afghan phone numbers only.
        Accepts:
        - +937XXXXXXXX
        - 07XXXXXXXX
        """

        phone = phone.strip().replace(" ", "")

        # Convert 07xxxxxxxx to +937xxxxxxxx
        if phone.startswith("07"):
            phone = "+93" + phone[1:]

        # Regex for Afghan mobile numbers
        afghan_phone_regex = r'^\+93(70|71|72|73|74|75|76|77|78|79)\d{7}$'

        if not re.match(afghan_phone_regex, phone):
            raise serializers.ValidationError(
                "Phone number must be a valid Afghan number (e.g. +9376XXXXXXX)."
            )

        return phone

    def validate(self, attrs):
        # Password confirmation
        # if attrs['password'] != attrs['password2']:
        #     raise serializers.ValidationError(
        #         {"password": "Passwords do not match."}
        #     )

        # Email validation (simple, exam-safe)
        email: str = attrs.get('email', '')
        if not email.endswith("@gmail.com"):
            raise serializers.ValidationError(
                {"email": "Please enter a valid email address."}
            )

        return attrs

    def create(self, validated_data):
        # validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
